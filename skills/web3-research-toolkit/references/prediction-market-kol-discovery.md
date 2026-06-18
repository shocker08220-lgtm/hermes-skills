# 预测市场 KOL 发现方法论

当 Ian 需要找预测市场（Polymarket/Kalshi/MEXC 等）的投放 KOL 时，按此流程执行。

## 核心发现

### MEXC 预测市场没有公开 KOL badge 体系
- MEXC 不走 Polymarket/Kalshi 那种「给 KOL 发 badge → KOL 把赔率包装成新闻」的模式
- MEXC 靠：自有账号 + PR 通稿 + 大奖池活动（Kickoff Fest 8M USDT）+ Affiliate Program（referral link，非 badge）
- 所以 Google/X 搜不到 "MEXC prediction market KOL" 是正常的——不存在这种公开投放关系
- MEXC KOL 入口：Affiliate Program（最高 70% 佣金）+ KOL manager @LeoInCrypto（TG/X）

### Polymarket/Kalshi KOL 发现路径
1. 新闻调查报道（POLITICO/Protos/Popular Info/NPR）— 点名了被支付的 KOL
2. Badge 体系 — Polymarket Sports/Trader/FC badge 持有者可追踪
3. 链上数据 — PolyZig/PANews 推荐的聪明钱地址 + 关联 X 账号
4. 预测市场官方频道 — @PolymarketFC/@PolymarketSport 的互动/转发账号反向挖掘

## 搜索限制

- **Google 不索引 X 帖子** — `site:x.com` 搜不到，拿不到具体推文 URL
- **fxtwitter API（免费）** — 可以拉用户 profile（粉丝数）、按 ID 读帖，但**不能搜索**
- **xurl（需要 OAuth）** — 可以搜 X 帖子，但需要配 X API 认证
- **fxtwitter 比 vanlett/socialpruf 更适合批量查粉丝数** — 后者经常被 Cloudflare 挡

## 表格要素

KOL 表格标准列：
- KOL / X 账号 / Twitter 链接 / 粉丝数 / 联系方式 / 推荐平台 / 证据来源 / 证据链接 / 核心判断

粉丝数用 fxtwitter API 验证：`curl -s "https://api.fxtwitter.com/<handle>" | python3 -c "..."`

## 中英文 KOL 分开搜索

中文 KOL 搜索词：预测市场 足球 世界杯 KOL 推特 Polymarket 聪明钱 地址
英文 KOL 搜索词：prediction market football soccer KOL Polymarket Kalshi analyst World Cup
