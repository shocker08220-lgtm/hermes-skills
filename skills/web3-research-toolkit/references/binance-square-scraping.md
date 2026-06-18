# Binance Square 内容抓取经验

## 平台特性
- 币安 Square 页面使用 React + CSS-in-JS（emotion/styled-components）
- 可访问性树几乎为空，传统 browser_snapshot 无法提取内容
- 页面加载后 innerText 被 CSS 规则污染，直接 `el.innerText` 会得到大量 `.css-xxx{...}` 噪音
- browser_vision 截图超时率高（页面渲染开销大，30s 超时）

## 有效提取方案

通过 browser_console 执行 JS，**定位特定链接模式**而非通用选择器：

```javascript
// 定位帖子链接（而非通用元素）
var posts = document.querySelectorAll('a[href*="/square/post/"]');

// 从最近的容器提取文本
posts.forEach(a => {
  var container = a.closest('div[class]');
  var text = container.innerText;
  // 去掉 CSS-in-JS 噪音
  text = text.replace(/\.css-\w+\{[^}]+\}/g, '');
});
```

## 关键教训
- **不要用 `[class*="post"]` 之类泛选择器** — 会命中无关元素
- **页面标题可直接从 `document.title` 获取** — "XXX的个人资料 | 币安广场"
- **Camofox 的 tab 容易变 stale** — 每次导航前建议创建新 tab
- **binance.com/bapi/** 所有公开 API 端点均返回 404** — API 已锁死，只能走浏览器

## fxtwitter 替代方案（仅适用于 X/Twitter）
- `api.fxtwitter.com` 可抓取 X Article 的完整内容块（JSON 格式）
- 支持 article content blocks、inline styles、header levels
- 不需要认证
