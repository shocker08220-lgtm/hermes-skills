"""v6 策略回测模板 — 1H主方向 + 4H确认 + 15m入场 + 1%止损"""
import ccxt, pandas as pd, numpy as np
from datetime import datetime, timezone, timedelta

exchange = ccxt.binance({"enableRateLimit": True})
SYMBOLS = ["BTC/USDT"]  # 可扩展到更多币种
DAYS = 60
SL = 0.01
COMM = 0.0004

def fetch(sym, tf, days):
    since = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp() * 1000)
    all_c = []
    while True:
        c = exchange.fetch_ohlcv(sym, tf, since=since, limit=1000)
        if not c: break
        all_c.extend(c)
        since = c[-1][0] + 1
        if len(c) < 1000: break
    df = pd.DataFrame(all_c, columns=["ts","open","high","low","close","volume"])
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

def backtest(sym):
    df5 = fetch(sym, "5m", DAYS); add_i(df5)
    df15 = fetch(sym, "15m", DAYS); add_i(df15)
    df1 = fetch(sym, "1h", DAYS); add_i(df1)
    df4 = fetch(sym, "4h", DAYS+30); add_i(df4)

    def big_dir(ts):
        try:
            h1 = df1[df1.index <= ts].iloc[-1]
            h4 = df4[df4.index <= ts].iloc[-1]
        except: return None
        long_ok = (h1["macd_golden"] and h1["macd_above_zero"] and h4["macd_golden"] and h1["boll_up"])
        short_ok = (not h1["macd_golden"] and not h1["macd_above_zero"] and not h4["macd_golden"] and not h1["boll_up"])
        if long_ok: return "long"
        if short_ok: return "short"
        return None

    trades = []
    pos = None
    for i in range(50, len(df15)):
        ts = df15.index[i]
        price = df15.iloc[i]["close"]
        row = df15.iloc[i]
        cur_dir = big_dir(ts)

        if pos is not None and cur_dir != pos["dir"]:
            pnl = (price - pos["entry"]) / pos["entry"]
            if pos["type"] == "short": pnl = -pnl
            trades.append({"sym":sym,"type":pos["type"],"pnl%":round((pnl-COMM*2)*100,2),
                           "reason":"dir_change","bars":i-pos["idx"]})
            pos = None

        if pos is None:
            if cur_dir == "long" and row["cross_up"] and row["align"] and row["vol_sig"]:
                pos = {"type":"long","dir":"long","entry":price,"idx":i}
            elif cur_dir == "short" and row["cross_down"] and not row["align"] and row["vol_sig"]:
                pos = {"type":"short","dir":"short","entry":price,"idx":i}
        else:
            pnl = (price - pos["entry"]) / pos["entry"]
            if pos["type"] == "short": pnl = -pnl
            net = pnl - COMM * 2
            reason = None
            if net <= -SL:
                reason = "sl"
            else:
                try:
                    h1_now = df1[df1.index <= ts].iloc[-1]
                    if pos["type"] == "long" and not h1_now["macd_golden"]: reason = "1h_dead"
                    elif pos["type"] == "short" and h1_now["macd_golden"]: reason = "1h_golden"
                except: pass
            if reason:
                trades.append({"sym":sym,"type":pos["type"],"pnl%":round(net*100,2),
                               "reason":reason,"bars":i-pos["idx"]})
                pos = None
    return trades

if __name__ == "__main__":
    all_trades = []
    for sym in SYMBOLS:
        all_trades.extend(backtest(sym))
    df = pd.DataFrame(all_trades)
    if len(df) > 0:
        wins = df[df["pnl%"] > 0]
        losses = df[df["pnl%"] <= 0]
        print(f"总交易: {len(df)}  胜率: {len(wins)/len(df)*100:.1f}%")
        print(f"盈亏比: {abs(wins['pnl%'].mean()/losses['pnl%'].mean()):.2f}" if len(losses)>0 else "")
        print(f"累计: {df['pnl%'].sum():.2f}%")
