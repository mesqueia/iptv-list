#!/usr/bin/env python3
import re
import subprocess
from pathlib import Path

PLAYLIST = Path("cat-spa.m3u")
CHANNEL_PAGE = "https://www.youtube.com/@gerardromerotv/live"
START = "# >>> YOUTUBE LIVE: GERARD ROMERO >>>"
END = "# <<< YOUTUBE LIVE: GERARD ROMERO <<<"

def resolve_live_url():
    cmd = [
        "yt-dlp",
        "--no-warnings",
        "--no-playlist",
        "-f", "best[protocol^=m3u8]/best",
        "--get-url",
        CHANNEL_PAGE,
    ]
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT, timeout=120).strip()
        # yt-dlp can occasionally print more than one URL; prefer an HLS URL.
        urls = [line.strip() for line in out.splitlines() if line.startswith("http")]
        for url in urls:
            if ".m3u8" in url:
                return url
        return urls[0] if urls else None
    except Exception as e:
        print(f"No live stream resolved: {e}")
        return None

text = PLAYLIST.read_text(encoding="utf-8")
stream_url = resolve_live_url()

# Keep the channel visible even when offline. When live, replace this fallback
# with the fresh direct stream URL.
target_url = stream_url or CHANNEL_PAGE
status = "EN DIRECTE" if stream_url else "OFFLINE"

block = f"""{START}
#EXTINF:-1 tvg-name="Gerard Romero" tvg-language="Spanish" group-title="YouTube",Gerard Romero ({status})
{target_url}
{END}"""

pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
if pattern.search(text):
    new_text = pattern.sub(block, text)
else:
    new_text = text.rstrip() + "\n\n" + block + "\n"

if new_text != text:
    PLAYLIST.write_text(new_text, encoding="utf-8")
    print("Playlist updated.")
else:
    print("No changes needed.")
