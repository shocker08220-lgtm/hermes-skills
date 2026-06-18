# 预测市场 KOL 投放研究

## 搜索策略

### 竞品投放 KOL（Polymarket / Kalshi）
- 从新闻报道反向挖掘：POLITICO、Protos、NPR、Semafor 等调查报道直接点名 KOL
- 关键词组合：`"Polymarket" "paid" "influencer" OR "affiliate" OR "badge"`
- 已验证的 KOL 名单见下方

### MEXC 预测市场 KOL
- **Google 搜索无效** — X 不向 Google 开放帖子索引，`site:x.com` 被 403
- **MEXC 没有公开 badge 体系** — 不像 Polymarket/Kalshi 给 KOL 发 badge，MEXC 的 KOL 走 Affiliate Program（referral link），不公开可追踪
- **唯一有效方法**：用 Grok/X 原生搜索，或配好 xurl 直接搜 X
- MEXC Affiliate Program 联系入口：`@LeoInCrypto` (TG/X, MEXC KOL Manager)

## 平台差异

| | Polymarket | Kalshi | MEXC |
|---|---|---|---|
| KOL 投放模式 | Badge + PayPal 付款 | Badge（2026.2 已撤）| Affiliate Program（referral link）|
| 可追踪性 | 调查报道可反向挖掘 | 调查报道可反向挖掘 | 不可公开追踪 |
| 足球活动 | World Cup Winner 市场 $2B+ | AFA 合作伙伴 | Kickoff Fest 8M USDT |
| 典型报价 | ~$500/post (NPR) | ~$500/post (NPR) | 70% 佣金分成 |

## 已验证 KOL（足球/体育方向）

### Polymarket 绑定
- @nosleepjon (41.8K) — PM 足球套利策略
- @gainzy222 (329K) — PM affiliate, crypto streamer
- @PolymarketFC (206K) — 官方足球频道
- @PolymarketSport (99K) — 官方体育频道
- @AnselFang (11.5K) — PM 中文区第一人, $2.66M PnL
- @UtopiaSports (22K) — PM badge, 纯体育预测

### Kalshi 绑定
- @icobeast (68K) — Kalshi Crypto 团队
- @katexbt (30K) — Kalshi affiliate

### 足球专家（预测市场关联）
- @Tgarratt10 (191K) — Pitchside 播客联创, WC2026 专家团
- @lawrence_bury (34.6K) — TikTok 足球评论员, Sky Sports

## 粉丝数验证方法

```bash
curl -s https://api.fxtwitter.com/HANDLE | python3 -c "
import json,sys; d=json.load(sys.stdin)
u=d.get('user',{}); print(u.get('followers',0))
"
```

fxtwitter 免费、无需认证。批量命令：`for h in ...; do curl -s "https://api.fxtwitter.com/$h" | ...; done`

## 输出格式

中英双表 .xlsx，每个 KOL：名称 / handle / 链接 / 粉丝数 / 推荐平台 / 证据来源 / 证据链接 / 核心判断

证据来源优先排序：新闻报道 > 社区推荐 (PANews/Odaily) > 链上数据 > 生态绑定 (badge/bio)
