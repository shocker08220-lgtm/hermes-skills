-- ===================================================================
-- Dune Token Dashboard Template
-- Replace __CONTRACT_ADDRESS__, __BLOCKCHAIN__, __DAYS__ below.
-- Produces: daily volume, trade count, active wallets, new addresses
-- ===================================================================

WITH token_trades AS (
  SELECT
    block_time,
    taker,
    amount_usd,
    DATE_TRUNC('day', block_time) AS day
  FROM dex.trades
  WHERE blockchain = '__BLOCKCHAIN__'           -- e.g. 'base', 'ethereum', 'bsc'
    AND (
      token_bought_address = __CONTRACT_ADDRESS__   -- e.g. 0xb4c64...
      OR token_sold_address = __CONTRACT_ADDRESS__
    )
    AND block_time >= CURRENT_DATE - INTERVAL '__DAYS__' DAY   -- e.g. 90
),
first_trade AS (
  SELECT taker, MIN(day) AS first_day
  FROM token_trades
  GROUP BY 1
),
daily_stats AS (
  SELECT
    day,
    SUM(amount_usd) AS volume_usd,
    COUNT(*) AS trade_count,
    COUNT(DISTINCT taker) AS active_wallets
  FROM token_trades
  GROUP BY 1
),
daily_new AS (
  SELECT first_day AS day, COUNT(DISTINCT taker) AS new_addresses
  FROM first_trade
  GROUP BY 1
)
SELECT
  d.day,
  ROUND(d.volume_usd, 2) AS volume_usd,
  d.trade_count,
  d.active_wallets,
  COALESCE(n.new_addresses, 0) AS new_addresses
FROM daily_stats d
LEFT JOIN daily_new n ON d.day = n.day
ORDER BY d.day DESC;


-- BONUS: Buy vs Sell Pressure
-- ===================================================================
WITH token_flows AS (
  SELECT
    DATE_TRUNC('day', block_time) AS day,
    CASE
      WHEN token_bought_address = __CONTRACT_ADDRESS__ THEN 'buy'
      WHEN token_sold_address = __CONTRACT_ADDRESS__ THEN 'sell'
    END AS direction,
    amount_usd
  FROM dex.trades
  WHERE blockchain = '__BLOCKCHAIN__'
    AND (
      token_bought_address = __CONTRACT_ADDRESS__
      OR token_sold_address = __CONTRACT_ADDRESS__
    )
    AND block_time >= CURRENT_DATE - INTERVAL '__DAYS__' DAY
)
SELECT
  day,
  SUM(CASE WHEN direction = 'buy' THEN amount_usd ELSE 0 END) AS buy_volume_usd,
  SUM(CASE WHEN direction = 'sell' THEN amount_usd ELSE 0 END) AS sell_volume_usd,
  SUM(CASE WHEN direction = 'buy' THEN amount_usd ELSE 0 END) 
    - SUM(CASE WHEN direction = 'sell' THEN amount_usd ELSE 0 END) AS net_flow_usd
FROM token_flows
GROUP BY 1
ORDER BY 1 DESC;
