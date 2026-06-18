"""回测模板 v6 — 1H主方向 + 4H确认 + 15m波段 + 1H出场
使用方法: ~/.pyenv/versions/3.12.3/bin/python3 backtest_template.py

策略逻辑（v6 已验证，跨币种 163 笔 +33.38%）：
  大方向 = 1H MACD金叉+零轴上 + 4H MACD金叉 + 1H Boll中轨向上
  方向锁定后只做一个方向，方向改变强制平仓
  方向=None 不交易
  入场 = 15m MACD金叉事件 + MA多头排列 + 放量
  出场 = 1H MACD反转 或 1%止损
"""

import ccxt, pandas as pd, numpy as np
from datetime import datetime, timezone, timedelta

exchange = ccxt.binance({"enableRateLimit": True})

# ========== 参数 ==========
SYMBOL = "BTC/USDT"
DAYS = 60
SL = 0.01
COMM = 0.0004

def fetch(tf, days):
    since = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp() * 1000)
    all_candles = []
    while True:
        c = exchange.fetch_ohlcv(SYMBOL, tf, since=since, limit=1000)
        if not c: break
        all_candles.extend(c)
        since = c[-1][0] + 1
        if len(c) < 1000: break
    df = pd.DataFrame(all_candles, columns=["ts","open","high","low","close","volume"])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    return df.set_index("ts").drop_duplicates()

def add_i(df):
    for p in [5,10,20]: df[f"ma{p}"] = df["close"].rolling(p).mean()
    e_fast = df["close"].ewm(span=7, adjust=False).mean()
    e_slow = df["close"].ewm(span=14, adjust=False).mean()
    df["macd_line"] = e_fast - e_slow
    df["macd_signal"] = df["macd_line"].ewm(span=9, adjust=False).mean()
    df["macd_golden"] = df["macd_line"] > df["macd_signal"]
    df["macd_above_zero"] = (df["macd_line"] > 0) & (e_slow > 0)
    df["cross_up"] = df["macd_golden"] & (~df["macd_golden"].shift(1).fillna(False))
    df["cross_down"] = (~df["macd_golden"]) & (df["macd_golden"].shift(1).fillna(False))
    df["boll_mid"] = df["close"].rolling(20).mean()
    df["boll_up"] = df["boll_mid"].diff(3) > 0
    df["vol_ma5"] = df["volume"].rolling(5).mean()
    df["vol_sig"] = df["volume"] >= df["vol_ma5"] * 1.5
    ma5, ma10, ma20 = df["ma5"], df["ma10"], df["ma20"]
    df["align"] = (ma5 > ma10) & (ma10 > ma20)

def big_direction(ts, df1, df4):
    """v6: 1H主方向 + 4H确认，砍12H"""
    try:
        h1 = df1[df1.index <= ts].iloc[-1]
        h4 = df4[df4.index <= ts].iloc[-1]
    except: return None
    long_ok = (h1["macd_golden"] and h1["macd_above_zero"] and
               h4["macd_golden"] and h1["boll_up"])
    short_ok = (not h1["macd_golden"] and not h1["macd_above_zero"] and
                not h4["macd_golden"] and not h1["boll_up"])
    if long_ok: return "long"
    if short_ok: return "short"
    return None

def run_backtest(symbol=SYMBOL, days=DAYS):
    print(f"回测 {symbol} ({days}天)")
    df15 = fetch("15m", days); add_i(df15); print(f"  15m:{len(df15)}")
    df1 = fetch("1h", days); add_i(df1); print(f"  1h:{len(df1)}")
    df4 = fetch("4h", days+30); add_i(df4); print(f"  4h:{len(df4)}")

    trades = []; pos = None

    for i in range(50, len(df15)):
        ts = df15.index[i]
        price = df15.iloc[i]["close"]
        row = df15.iloc[i]
        cur_dir = big_direction(ts, df1, df4)

        if pos is not None and cur_dir != pos["dir"]:
            pnl = (price - pos["entry"]) / pos["entry"]
            if pos["type"] == "short": pnl = -pnl
            net = pnl - COMM * 2
            trades.append({"type":pos["type"],"entry_t":str(pos["time"]),"exit_t":str(ts),
                           "entry_p":round(pos["entry"],2),"exit_p":round(price,2),
                           "pnl%":round(net*100,2),"reason":"dir_change","bars":i-pos["idx"]})
            pos = None

        if pos is None:
            if cur_dir == "long":
                if row["cross_up"] and row["align"] and row["vol_sig"]:
                    pos = {"type":"long","dir":"long","entry":price,"time":ts,"idx":i}
            elif cur_dir == "short":
                if row["cross_down"] and not row["align"] and row["vol_sig"]:
                    pos = {"type":"short","dir":"short","entry":price,"time":ts,"idx":i}
        else:
            pnl = (price - pos["entry"]) / pos["entry"]
            if pos["type"] == "short": pnl = -pnl
            net = pnl - COMM * 2
            reason = None
            if net <= -SL: reason = "sl"
            else:
                try:
                    h1_now = df1[df1.index <= ts].iloc[-1]
                    if pos["type"]=="long" and not h1_now["macd_golden"]: reason = "1h_dead"
                    elif pos["type"]=="short" and h1_now["macd_golden"]: reason = "1h_golden"
                except: pass
            if reason:
                trades.append({"type":pos["type"],"entry_t":str(pos["time"]),"exit_t":str(ts),
                               "entry_p":round(pos["entry"],2),"exit_p":round(price,2),
                               "pnl%":round(net*100,2),"reason":reason,"bars":i-pos["idx"]})
                pos = None

    return pd.DataFrame(trades)

def report(df):
    if len(df) == 0: print("⚠️ 无交易"); return
    total = len(df)
    wins = df[df["pnl%"]>0]; losses = df[df["pnl%"]<=0]
    longs = df[df["type"]=="long"]
    wr = len(wins)/total*100
    rr = abs(wins["pnl%"].mean()/losses["pnl%"].mean()) if len(losses)>0 else float("inf")
    print(f"\n总交易:{total} 胜率:{wr:.1f}% 盈亏比:{rr:.2f}")
    print(f"做多:{len(longs)} 做空:{total-len(longs)}")
    print(f"均盈:{wins['pnl%'].mean():.2f}% 均亏:{losses['pnl%'].mean():.2f}%")
    print(f"最大盈:{df['pnl%'].max():.2f}% 最大亏:{df['pnl%'].min():.2f}%")
    print(f"累计:{df['pnl%'].sum():.2f}% 均持仓:{df['bars'].mean():.0f}根15m({df['bars'].mean()*15/60:.1f}h)")
    print(f"\n出场原因:")
    for r in df["reason"].unique():
        sub = df[df["reason"]==r]
        w = (sub["pnl%"]>0).sum()/len(sub)*100
        print(f"  {r}:{len(sub)}笔 胜率{w:.0f}% 均{sub['pnl%'].mean():.2f}% 累计{sub['pnl%'].sum():.2f}%")
    print(f"\n最近5笔:")
    print(df.tail(5)[["type","entry_t","pnl%","reason","bars"]].to_string(index=False))

if __name__ == "__main__":
    trades = run_backtest()
    report(trades)
