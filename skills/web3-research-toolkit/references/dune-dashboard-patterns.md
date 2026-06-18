# Dune Dashboard Patterns

Reusable SQL templates for building Dune dashboards. All queries use `dex.trades` (Dune's aggregated DEX table) and are parameterized — swap contract address and chain to reuse.

## Pattern 1: Comprehensive Daily Stats (4-in-1)

```sql
WITH token_trades AS (
  SELECT block_time, taker, amount_usd,
    DATE_TRUNC('day', block_time) AS day
  FROM dex.trades
  WHERE blockchain = '{chain}'
    AND (token_bought_address = {contract} OR token_sold_address = {contract})
    AND block_time >= CURRENT_DATE - INTERVAL '90' DAY
),
first_trade AS (
  SELECT taker, MIN(day) AS first_day FROM token_trades GROUP BY 1
),
daily_stats AS (
  SELECT day, SUM(amount_usd) AS volume_usd, COUNT(*) AS trades,
    COUNT(DISTINCT taker) AS active_wallets
  FROM token_trades GROUP BY 1
),
daily_new AS (
  SELECT first_day AS day, COUNT(DISTINCT taker) AS new_addresses
  FROM first_trade GROUP BY 1
)
SELECT d.day, ROUND(d.volume_usd,2) AS volume_usd, d.trades,
  d.active_wallets, COALESCE(n.new_addresses,0) AS new_addresses
FROM daily_stats d
LEFT JOIN daily_new n ON d.day = n.day
ORDER BY d.day DESC
```

## Pattern 2: Realtime Stats Counter

```sql
WITH token_trades AS (
  SELECT block_time, taker, amount_usd,
    DATE_TRUNC('day', block_time) AS day
  FROM dex.trades
  WHERE blockchain = '{chain}'
    AND (token_bought_address = {contract} OR token_sold_address = {contract})
),
first_trade AS (
  SELECT taker, MIN(day) AS first_day FROM token_trades GROUP BY 1
)
SELECT
  ROUND(SUM(CASE WHEN x.block_time >= NOW() - INTERVAL '24' HOUR THEN x.amount_usd ELSE 0 END),2) AS volume_24h,
  COUNT(CASE WHEN x.block_time >= NOW() - INTERVAL '24' HOUR THEN 1 END) AS trades_24h,
  COUNT(DISTINCT CASE WHEN x.block_time >= NOW() - INTERVAL '24' HOUR THEN x.taker END) AS wallets_24h,
  COUNT(DISTINCT CASE WHEN f.first_day >= CURRENT_DATE THEN f.taker END) AS new_today,
  ROUND(SUM(CASE WHEN x.block_time >= NOW() - INTERVAL '7' DAY THEN x.amount_usd ELSE 0 END),2) AS volume_7d,
  ROUND(SUM(x.amount_usd),2) AS volume_all,
  COUNT(DISTINCT x.taker) AS wallets_all
FROM token_trades x
LEFT JOIN first_trade f ON x.taker = f.taker
```

## Pattern 3: Buy vs Sell Pressure

```sql
WITH flows AS (
  SELECT DATE_TRUNC('day', block_time) AS day,
    CASE WHEN token_bought_address = {contract} THEN 'buy'
         WHEN token_sold_address = {contract} THEN 'sell' END AS direction,
    amount_usd
  FROM dex.trades
  WHERE blockchain = '{chain}'
    AND (token_bought_address = {contract} OR token_sold_address = {contract})
    AND block_time >= CURRENT_DATE - INTERVAL '90' DAY
)
SELECT day,
  SUM(CASE WHEN direction='buy' THEN amount_usd ELSE 0 END) AS buy_vol,
  SUM(CASE WHEN direction='sell' THEN amount_usd ELSE 0 END) AS sell_vol,
  SUM(CASE WHEN direction='buy' THEN amount_usd ELSE 0 END) -
    SUM(CASE WHEN direction='sell' THEN amount_usd ELSE 0 END) AS net_flow
FROM flows GROUP BY 1 ORDER BY 1 DESC
```

## Delivery Preference

Ian prefers **inline SQL over file downloads**. Don't save .sql files — paste the query directly into chat. If multiple queries are needed, number them clearly and let him copy-paste one at a time.

## Dashboard Assembly (Step-by-Step UI)

**For time-series charts (volume / trades / wallets / new addresses):**
1. Create Query → paste Pattern 1 → click blue **"Run"** button (bottom right)
2. Click **"New visualization"** below the results table
3. Chart type dropdown → select **Bar Chart** (for volume) or **Line Chart** (for wallets/trades)
4. **X-axis** row → dropdown → pick `day`
5. **Y-axis** row → dropdown → pick the metric (`volume_usd` / `trades` / `active_wallets` / `new_addresses`)
6. **Title** field → name it (e.g. "XTTA Daily Volume")
7. Click **Save**
8. Repeat for remaining 3 metrics

**For summary stat counters (24h volume / trades / wallets / new today):**
1. Create a new Query → paste Pattern 2 → Run
2. New visualization → Chart type dropdown → select **"Counter"**
3. **Value column** → pick `volume_24h`
4. **Label** → name it (e.g. "📊 24h Volume")
5. Save → repeat for `trades_24h`, `wallets_24h`, `new_today`

**Grouping into Dashboard:**
1. Each chart's "..." menu → **"Add to dashboard"** → New dashboard → name it
2. Open Dashboard from left nav → drag to arrange (Counters top row, time-series below)
3. Dashboard auto-refreshes every 15 min when open; runs on visit when closed

## Common Pitfalls

- **Ambiguous column (error "Column 'taker' is ambiguous")**: When joining CTEs with same column names, always alias tables (`FROM xtta_trades x LEFT JOIN first_trade f`) and qualify columns (`x.taker`, `f.taker`)
- **Dune table**: `dex.trades` is cross-chain — always filter `blockchain = 'base'` etc.
- **amount_usd**: Returns NULL for low-liquidity tokens; use `amount_usd` not `usd_amount`
- **No data on first run**: Some tokens take minutes to appear; wait and retry
- **Contract discovery**: Use CoinGecko API (`/api/v3/coins/{id}`) to get contract address + chain before writing SQL
