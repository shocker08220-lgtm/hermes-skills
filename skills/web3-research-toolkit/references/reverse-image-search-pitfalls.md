# Reverse Image Search — Server-Side Pitfalls

## Problem

All major reverse image search services block server-side/automated requests with Cloudflare:

| Service | Blocked? | Notes |
|---------|:-------:|-------|
| Google Lens | ✅ Login required | `lens.google.com/upload` needs account; URL-based `uploadbyurl` works but Cloudflare blocks bot |
| SauceNAO | ✅ Cloudflare | API requires key; web endpoint under CF challenge |
| TinEye | ✅ Cloudflare | Full CF browser check |
| ascii2d.net | ✅ Cloudflare | CF blocks all automated requests |
| Yandex Images | ⚠️ Minimal UI | Web interface loads but upload flow not accessible via accessibility tree |
| IQDB | ✅ Open | No CF, but anime/doujin-focused; often returns "No relevant matches" for non-anime content |

## IQDB — The Only Unblocked Option

```bash
# Upload and search (no API key needed)
curl -s -X POST "https://iqdb.org/" \
  -F "file=@image.jpg" \
  --connect-timeout 15

# Or by URL (image must be publicly accessible)
curl -s "https://iqdb.org/?url=https://example.com/image.jpg"
```

Parses HTML results. IQDB also generates convenient links to other engines:
- `https://iqdb.org/thu/thu_XXXXX.jpg` — thumbnail URL usable as input for Lens/SauceNAO/etc.

## What Works

The method from the X article works ONLY when the user manually operates from:
- Phone: Google Lens (built into Google App) → upload screenshot → instant results
- Desktop: images.google.com → camera icon → upload → results

Server-side automation is effectively dead for this use case. Don't waste time trying to bypass Cloudflare — tell the user to do it on their own device.
