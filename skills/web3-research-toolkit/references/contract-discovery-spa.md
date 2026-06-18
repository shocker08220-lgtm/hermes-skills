# Finding Smart Contract Addresses in SPA dApps

Modern Web3 dApps (Next.js, React) are SPAs that load contract addresses dynamically
in JavaScript — they won't appear in `curl` output or page HTML. Here's the
multi-pronged approach to find them.

## Approach 1: JS Bundle Analysis (most reliable)

```
1. Fetch the page HTML to identify JS chunk URLs
2. Download each chunk and grep for 0x addresses
3. Filter out known false positives (0x0000..., 0xfffff..., bytecode fragments)
4. Cross-reference candidates on the block explorer
```

Python example:
```python
import urllib.request, re

# Step 1: Get chunk URLs
html = urllib.request.urlopen(url).read().decode()
chunks = set(re.findall(r'/_next/static/chunks/[^\"]+\.js', html))

# Step 2: Extract addresses from each chunk
for chunk in chunks:
    js = urllib.request.urlopen(f'https://{domain}{chunk}').read().decode()
    addrs = set(re.findall(r'0x[a-fA-F0-9]{40}', js))
    # Filter bytecode patterns (starts with 0x60806040, 0x6492..., etc.)
    real_addrs = {a for a in addrs if not a.startswith(('0x6080','0x6492','0x8010','0xca11','0xeeee','0xffff','0x0000'))}
```

**Common false positives to filter:**
- `0x0000000000000000000000000000000000000000` — zero address
- `0xffffffffffffffffffffffffffffffffffffffff` — max uint256
- `0x60806040...` — EVM bytecode fragments
- `0xeeeeeeee...` — native ETH placeholder
- `0xca11bde0...` — multicall contract
- `0x64926492...` — bytecode pattern

## Approach 2: Token Holder Analysis

If the dApp involves token staking, the staking contract is likely a top holder:
1. Go to the token page on the block explorer (e.g. `basescan.org/token/<addr>`)
2. Check the "Holders" tab — the contract holding the most tokens is usually the staking contract
3. Verify by checking if the address is a verified contract ("Contract" tab)

## Approach 3: Browser DevTools (Camofox)

When using a headless browser (Camofox):
1. `browser_navigate` to the dApp page
2. Use `browser_console` to inspect JS state:
   - Check `localStorage` for wagmi store: `localStorage.getItem('wagmi.store')`
   - Search `window` object: iterate `Object.keys(window)` for contract-related keys
   - Look for `POST` requests to RPC endpoints in network traffic
3. Many dApps initialize contract instances in module scope — the addresses
   are in the JS bundles but may not be visible in runtime state

## Approach 4: Web Search

For well-known projects, search engines may have indexed the contract:
```
"<project> staking contract address 0x"
```

## Block Explorer API Pitfalls

- **Basescan/etherscan V1 API is deprecated**: Returns `"You are using a deprecated V1 endpoint, switch to Etherscan API V2"`
- **V2 API may 404**: The documented V2 endpoints may not work yet on all chains. Fall back to the web UI or use Dune instead.
- **Dune is preferred for token analytics**: Use `dex.trades` table with contract address filtering — no API key needed for public dashboards.

## XTTA / xstaking.io Case Study

xstaking.io is a Next.js SPA with ~28 stake vaults, each 1M XTTA cap, 9% monthly,
30-day lock. The staking contract was NOT found via JS bundle analysis (addresses
were scattered across 24 chunks with no single obvious staking contract). The
likely architecture is a factory contract that deploys per-vault contracts — to
find it, search the XTTA token's top holders for a contract that holds ~14M+ XTTA.
