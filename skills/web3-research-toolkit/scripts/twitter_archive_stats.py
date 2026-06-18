#!/usr/bin/env python3
"""
Twitter archive analyzer — parse Twitter data export and print stats.

Usage:
  python3 twitter_archive_stats.py /path/to/twitter_data/data/

Reads tweets.js, account.js, profile.js, following.js, follower.js from a
Twitter data export directory and prints:
  - Account handle, tweet count, date range
  - Total impressions, likes, RTs, replies
  - Average engagement per tweet
  - Top tweets by likes and impressions
  - Content mix (% with media, links, replies, quotes, RTs)
  - Posting hours and days distribution (UTC)

Assumes standard Twitter archive format:
  window.YTD.tweets.part0 = [{ ... }]
"""

import json, re, sys
from collections import Counter
from datetime import datetime

def parse_js(path):
    """Strip JS wrapper and parse as JSON."""
    with open(path) as f:
        raw = f.read()
    # Find the JSON array after "window.YTD.xxx.part0 = "
    json_str = re.sub(r'^window\.YTD\.\w+\.part\d*\s*=\s*', '', raw.strip())
    return json.loads(json_str)

def analyze(data_dir):
    tweets = parse_js(f'{data_dir}/tweets.js')
    account = parse_js(f'{data_dir}/account.js')
    handle = account[0]['account'].get('username', '?')
    
    print(f"=== @{handle} Twitter Archive Analysis ===\n")
    print(f"Total tweets: {len(tweets)}")
    
    # Engagement stats
    imp = likes = rts = replies = 0
    dates = []
    for t in tweets:
        tw = t.get('tweet', t)
        v = tw.get('views', {})
        if isinstance(v, dict): imp += int(v.get('count', '0'))
        likes += int(tw.get('favorite_count', 0))
        rts += int(tw.get('retweet_count', 0))
        replies += int(tw.get('reply_count', 0))
        d = tw.get('created_at', '')
        if d: dates.append(d)
    
    n = len(tweets)
    if dates:
        print(f"Date range: {dates[-1]} → {dates[0]}")
    print(f"Impressions: {imp:,}  |  Likes: {likes:,}  |  RTs: {rts:,}  |  Replies: {replies:,}")
    print(f"Avg likes/tweet: {likes/n:.1f}  |  Avg impressions/tweet: {imp/n:.0f}\n")
    
    # Content mix
    has_media = sum(1 for t in tweets if t.get('tweet',t).get('extended_entities'))
    has_link  = sum(1 for t in tweets if 'https://t.co/' in t.get('tweet',t).get('full_text',''))
    is_reply  = sum(1 for t in tweets if t.get('tweet',t).get('in_reply_to_status_id'))
    is_quote  = sum(1 for t in tweets if t.get('tweet',t).get('quoted_status_id'))
    is_rt     = sum(1 for t in tweets if t.get('tweet',t).get('retweeted_status_id'))
    
    print("--- Content Mix ---")
    print(f"Original: {n-is_reply-is_rt-is_quote} ({ (n-is_reply-is_rt-is_quote)/n*100:.0f}%)")
    print(f"Replies:  {is_reply} ({is_reply/n*100:.0f}%)")
    print(f"With media: {has_media} ({has_media/n*100:.0f}%)")
    print(f"With links: {has_link} ({has_link/n*100:.0f}%)\n")
    
    # Top tweets
    by_likes = sorted(tweets, key=lambda t: int(t.get('tweet',t).get('favorite_count',0)), reverse=True)
    print("--- Top 5 by Likes ---")
    for i, t in enumerate(by_likes[:5]):
        tw = t.get('tweet', t)
        print(f"{i+1}. ❤️{tw.get('favorite_count',0)} 🔄{tw.get('retweet_count',0)} | {tw.get('created_at','?')}")
        print(f"   {tw.get('full_text','')[:200]}\n")
    
    # Posting time
    hours, days = Counter(), Counter()
    for t in tweets:
        d = t.get('tweet',t).get('created_at','')
        if d:
            try:
                dt = datetime.strptime(d, '%a %b %d %H:%M:%S %z %Y')
                hours[dt.hour] += 1
                days[dt.strftime('%A')] += 1
            except: pass
    
    print("--- Posting Hours (UTC) ---")
    for h in sorted(hours.keys()):
        print(f"  {h:02d}:00  {'█' * min(hours[h], 50)} {hours[h]}")
    
    print("\n--- Posting Days ---")
    for d in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']:
        print(f"  {d}: {days.get(d, 0)}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 twitter_archive_stats.py <twitter_data_dir>")
        sys.exit(1)
    analyze(sys.argv[1])
