"""Give every scene in tour.json a time from its word count, and write AUTO_DEMO.md from the same text."""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
PATH = ROOT / "public" / "tour.json"
WORDS_PER_SECOND = 2.5  # normal spoken Hinglish
scenes = json.loads(PATH.read_text())
for x in scenes:
    x["ms"] = round((len(x["say"].split()) / WORDS_PER_SECOND + 1) * 1000, -2)
PATH.write_text(json.dumps(scenes, ensure_ascii=False, indent=0))

total = sum(x["ms"] for x in scenes) / 1000
out = [f"""# Auto-demo: 5 speakers, {total / 60:.0f} minutes

Page khud chalta hai. Har speaker apni lines bolta hai.

**Screen ke neeche right me scene number dikhta hai (jaise 7/{len(scenes)}), wahi number yahan hai.** Number ke upar ki patli line bhar jaaye toh agli line. Atak jao toh **Space** dabao, demo ruk jaayega; dobara Space se chalega.

| Speaker | Naam | Scenes | Time |
|---|---|---|---|"""]
for s in range(1, 6):
    mine = [i for i, x in enumerate(scenes, 1) if x["s"] == s]
    secs = sum(scenes[i - 1]["ms"] for i in mine) / 1000
    out.append(f"| {s} | _____ | {mine[0]} to {mine[-1]} | {secs / 60:.1f} min |")
out.append("""
## Record karne ke steps

1. Ek baar practice karo. Speed dekhne ke liye page poora chala lo.
2. Chrome me kholo: https://pramaan-teal.vercel.app/?tour=1
3. Chrome full screen karo (Ctrl + Cmd + F).
4. **Cmd + Shift + 5**, Record Entire Screen, Options me mic select karo, Record dabao.
5. Page pe **Start demo** dabao aur Speaker 1 shuru kare.
6. Aakhri card pe 2 second ruk ke menu bar me Stop dabao.

Paanchon ek hi laptop ke paas baitho aur mic ke paas aake bolo. Alag jagah ho toh Google Meet pe aao, ek banda screen share kare aur Meet record ho.
""")
titles = {1: "Problem aur idea", 2: "Clean application aur forgery ki shuruaat", 3: "Forgery pakadna", 4: "Ghost faculty, queue aur andar ka system", 5: "AI, feasibility, limits, close"}
for s in range(1, 6):
    out.append(f"## Speaker {s}: {titles[s]}\n\n| Scene | Sec | Bolo |\n|---|---|---|")
    out += [f"| {i} | {x['ms'] / 1000:.0f} | {x['say']} |" for i, x in enumerate(scenes, 1) if x["s"] == s]
    out.append("")
(ROOT / "docs" / "pitch" / "AUTO_DEMO.md").write_text("\n".join(out))
print(f"{total:.0f} s, {len(scenes)} scenes", {s: round(sum(x['ms'] for x in scenes if x['s'] == s) / 1000) for s in range(1, 6)})
