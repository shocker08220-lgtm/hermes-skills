# CoinGecko 免费 API 限流经验

## 限流规则

免费 API（无需 Key）：**~10-30 次请求/分钟**。超出 → HTTP 429。

## 实用端点

| 端点 | 用途 | 
|------|------|
| `/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true` | BTC/ETH/SOL 现价+24h涨跌 |
| `/global` | 总市值、24h成交量、BTC/ETH 占比 |
| `/search/trending` | 热搜币 Top 10 |
| `/coins/categories` | 热门赛道（~700 个类别，按市值排序） |

## 避限流策略

1. **间隔 1.5 秒** — 每个 API 调用前 `time.sleep(1.5)`，4 次调用 ~7.5 秒完成
2. **限流时等 60 秒** — 如果 429，sleep 60 秒后重试，不要连点
3. **合并请求** — 一次 `/simple/price` 可以查多个币（逗号分隔 ID），不要循环单个查
4. **dry-run 和正式写入分开** — 如果刚跑过 dry-run 立即跑正式版，可能触发同 IP 限流。至少等 60 秒

## 替代端点

- **alternative.me `/fng/`** — 恐慌贪婪指数，无速率限制，可随时调用
- **DeFiLlama** — 无公开免费 airdrop API（`/airdrops` 端点不存在），需爬虫或付费

## 实战踩坑

- 2026-05-28：dry-run 后立即正式写入 → 429。等了 60 秒重试成功。
- 加到 `update_context.py` 的 `fetch()` 函数里 `time.sleep(1.5)` 后未再触发。
