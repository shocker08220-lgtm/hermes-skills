# X (Twitter) 内容提取技术

当需要提取 X 上的长文章、帖子内容但无法登录或无 API 时使用的技术。

## fxtwitter API（推荐）

**无需认证**，直接返回结构化 JSON，包含完整文章内容。

```bash
curl -s "https://api.fxtwitter.com/{handle}/status/{tweet_id}"
```

**返回的关键字段：**
- `tweet.text` — 纯文本
- `tweet.author` — 作者信息（followers、description 等）
- `tweet.article` — X Article 长文章（如果有）
  - `article.title` — 标题
  - `article.preview_text` — 预览
  - `article.content.blocks[].text` — 逐段内容（带 inline styles）
  - `article.cover_media` — 封面图

**提取文章正文的 Python 脚本：**
```python
import json, sys
data = json.load(sys.stdin)
article = data['tweet']['article']
for block in article['content']['blocks']:
    text = block.get('text', '')
    t = block.get('type', '')
    if t == 'header-one': print(f'\n## {text}')
    elif t == 'header-two': print(f'\n### {text}')
    elif text.strip(): print(text)
```

## Binance Square 内容提取

**已知挑战：** 币安 Square 是重度 React SPA，accessibility tree 为空，Camofox 浏览器经常超时。

**可行的提取方式（Camofox browser_console）：**
```javascript
// 获取帖子链接
Array.from(document.querySelectorAll('a[href*="/square/post/"]'))

// 获取帖子内容（带文本清洗）
Array.from(document.querySelectorAll('a[href*="/square/post/"]')).slice(0,5).map(a => {
    var container = a.closest('div[class]');
    return (container?.innerText || '').replace(/\.css-\w+\{[^}]+\}/g, '').trim();
})
```

**API 端点：** 币安 Square 的公开 API 全部返回 404，前端是唯一入口。

## 注意事项

- fxtwitter 可能被限流，间隔 1-2 秒
- Binance Square 提取需要 Camofox 运行且 Tab 未过期
- Camofox Tab 在进程重启后会失效，需要先清理 stale sessions
