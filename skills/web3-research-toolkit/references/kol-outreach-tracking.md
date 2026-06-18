# KOL 外联追踪工作流

当 Ian 有 KOL 名单需要管理报价、状态、追踪时，优先用 Google Sheets 直连编辑。

## 数据结构（Renee 表为例）

| 列 | 含义 | 说明 |
|----|------|------|
| A: 链接 | X/TG 链接 | 用于定位 KOL 身份 |
| B: 名称 | 显示名 / @handle | 匹配主键 |
| C: 类别 | KOC / KOL | 分类筛选 |
| D: 进度 | 待回复 / 已回复 / 同意 / 拒绝 | 状态流水 |
| E: 价格USDT | 报价 | 更新频率最高 |
| F: 备注 | 原始报价详情 + 状态标签 | 追加式更新 |

## 批量更新流程

1. **读源表** — Ian 从 TG/Excel 发来已完成的报价信息
2. **读目标表** — `$GAPI sheets get SID "'SheetName'!A1:F60"` 获取当前数据
3. **名称匹配** — 按 B 列（名称/ @handle）跨表匹配行号
4. **逐行更新** — `$GAPI sheets update SID "'Sheet'!D{r}:F{r}" --values '[[进度, 价格, 备注+【已更新】]]'`
5. **关键 pitfall**: `sheets update` 是原子替换，不是追加。要在备注末尾加标签，**必须先读当前备注内容，再拼接新值**。

## 更新规则（Ian 约定）

- 进度：`待回复` → `已回复`
- 价格：填入 Ian 发来的最新报价
- 备注：末尾追加 `【已更新】`（保留原有内容）
- 不改动的行：不动

## 跨平台同步

- Ian 发 xlsx → 用 openpyxl 读取 → 匹配名称 → 写入 Google Sheets
- Ian 发 TG 消息 → 解析 @handle + 报价 → 写入 Google Sheets
- 多条批量更新 → 用 Python subprocess 循环调用 `$GAPI sheets update`，每行一次

## 已验证的 Google Sheets API 命令

```bash
GAPI="python3 ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py"
SID="18ZKaoVgnuzV6LvCjxnG6bASDls4wWs9QEbvwiMay9c0"

# 读取
$GAPI sheets get $SID "'Renee'!A1:F60"

# 更新单行（D/E/F 列）
$GAPI sheets update $SID "'Renee'!D17:F17" \
  --values '[["已回复", "Price: Quote $70", "old note\n【已更新】"]]'
```

## 粉丝数验证

所有 X 账号粉丝数通过 fxtwitter API 实时验证，不依赖 Google 搜索结果：

```bash
curl -s https://api.fxtwitter.com/HANDLE | python3 -c "
import json,sys
d=json.load(sys.stdin)
u=d.get('user',{})
print(f'followers:{u.get(\"followers\",0)} name:{u.get(\"name\",\"?\")}')
"
```

fxtwitter 免费、无需认证、实时数据。优先于任何第三方统计网站。
