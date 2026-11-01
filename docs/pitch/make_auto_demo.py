"""Give every scene in tour.json a time from its word count, and write AUTO_DEMO.md from the same text."""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
PATH = ROOT / "public" / "tour.json"
WORDS_PER_SECOND = 2.5  # clear spoken English, 150 words a minute
scenes = json.loads(PATH.read_text())
for x in scenes:
    x["ms"] = round((len(x["say"].split()) / WORDS_PER_SECOND + 1) * 1000, -2)
PATH.write_text(json.dumps(scenes, ensure_ascii=False, indent=0))

total = sum(x["ms"] for x in scenes) / 1000
out = [f"""# Auto-demo: 5 speakers, {total / 60:.0f} minutes

The page plays by itself. Each speaker reads their own lines.

**The scene number shows at the bottom right of the screen (like 7/{len(scenes)}), and it matches the number here.** When the thin line above the caption fills up, move to the next line. If someone gets stuck, press **Space** to pause, and Space again to continue.

| Speaker | Name | Scenes | Time |
|---|---|---|---|"""]
for s in range(1, 6):
    mine = [i for i, x in enumerate(scenes, 1) if x["s"] == s]
    secs = sum(scenes[i - 1]["ms"] for i in mine) / 1000
    out.append(f"| {s} | _____ | {mine[0]} to {mine[-1]} | {secs / 60:.1f} min |")
out.append("""
## How to record

1. Do one practice run first, to check your speed.
2. Open in Chrome: https://pramaan-teal.vercel.app/?tour=1
3. Make Chrome full screen (Ctrl + Cmd + F).
4. Press **Cmd + Shift + 5**, choose Record Entire Screen, select your mic under Options, and press Record.
5. Press **Start demo** on the page. Speaker 1 begins.
6. On the last card, wait 2 seconds, then press Stop in the menu bar.

Sit around one laptop and move close to the mic to speak. If you are in different places, join a Google Meet, have one person share the screen, and record the Meet.
""")
titles = {1: "Problem and idea", 2: "Clean application, start of the forgery", 3: "Catching the forgery", 4: "Ghost faculty, queue, how it works", 5: "AI, feasibility, limits, close"}
for s in range(1, 6):
    out.append(f"## Speaker {s}: {titles[s]}\n\n| Scene | Sec | Say |\n|---|---|---|")
    out += [f"| {i} | {x['ms'] / 1000:.0f} | {x['say']} |" for i, x in enumerate(scenes, 1) if x["s"] == s]
    out.append("")
(ROOT / "docs" / "pitch" / "AUTO_DEMO.md").write_text("\n".join(out))
print(f"{total:.0f} s, {len(scenes)} scenes", {s: round(sum(x['ms'] for x in scenes if x['s'] == s) / 1000) for s in range(1, 6)})
