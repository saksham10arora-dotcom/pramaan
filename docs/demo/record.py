"""Drive the running app, record it, lay the narration over it. Start the app on port 8517 first.
A second pass takes sharp screenshots for the slides."""
import json
import shutil
import sqlite3
import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
IMG = HERE.parent / "slides" / "img"
URL = "http://localhost:8517"
W, H = 1440, 810
CARD = """<script>let n=0;setInterval(()=>document.title=n++,33);setInterval(()=>document.body.style.outlineColor=n%2?'#17335C':'#17335D',33)</script><body style="outline:1px solid;outline-offset:-1px;margin:0;height:100vh;display:flex;flex-direction:column;justify-content:center;padding:0 110px;
background:#17335C;color:#fff;font-family:Georgia,serif"><div style="font:600 22px Arial;color:#9DB7DA;letter-spacing:2px">{kicker}</div>
<div style="font-size:96px;font-weight:700;margin:18px 0">Pramaan</div><div style="font-size:32px;line-height:1.4;max-width:1050px">{line}</div>
<div style="font:20px Arial;color:#9DB7DA;margin-top:44px">{foot}</div></body>"""


# the recorder drops frames on a still page, which puts picture and voice out of step; this keeps it painting
TICK = """addEventListener('DOMContentLoaded', () => { const d = document.createElement('div');
d.style.cssText = 'position:fixed;right:0;bottom:0;width:2px;height:2px;z-index:99999;pointer-events:none';
document.documentElement.appendChild(d); let n = 0; setInterval(() => { d.style.background = n++ % 2 ? '#fefefe' : '#fdfdfd'; }, 33); });"""


def seconds(name):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(HERE / "audio" / f"{name}.mp3")], capture_output=True, text=True).stdout
    return float(out)


def pick(page, label):
    page.get_by_text(label, exact=True).first.click()
    page.get_by_text("Running...").first.wait_for(state="hidden", timeout=20000)
    page.wait_for_timeout(1500)


def glide(page, top, ms=1800):
    page.evaluate("""([top, ms]) => { const m = document.querySelector('[data-testid="stMain"]'); const s = m.scrollTop, t0 = performance.now();
        const go = n => { const k = Math.min(1, (n - t0) / ms); m.scrollTop = s + (top - s) * (k * (2 - k)); if (k < 1) requestAnimationFrame(go); }; requestAnimationFrame(go); }""", [top, ms])
    page.wait_for_timeout(ms + 100)


def clear_registry():
    """Both passes must start from an empty record, as a fresh demo does."""
    db = sqlite3.connect(HERE.parent.parent / "data" / "pramaan.db")
    for table in ("applications", "documents", "faculty"):
        db.execute(f"DELETE FROM {table}")
    db.commit()
    db.close()


def run(page, shot=None, hold=True):
    """Each scene does its actions, then waits until its narration has finished."""
    marks = {}

    def scene(name, body):
        marks[name] = time.time()
        body()
        if hold:
            page.wait_for_timeout(max(0, (seconds(name) + 0.7 - (time.time() - marks[name])) * 1000))

    def intro():
        page.set_content(CARD.format(kicker="SMART INDIA HACKATHON 2026 · SIH26261 · AICTE",
                                     line="AI-powered application validation, document authentication and compliance verification",
                                     foot="All institutions and people in this demo are fictional."))

    def clean():
        page.goto(URL)
        page.get_by_text("or load a demo application").wait_for()
        pick(page, "clean")
        page.wait_for_timeout(5000)
        if shot: shot("app_clean")
        page.get_by_text("student to faculty ratio", exact=False).first.click()
        page.wait_for_timeout(1500)
        page.get_by_text("built-up area", exact=False).first.click()
        page.wait_for_timeout(1500)
        if shot: shot("app_evidence")
        glide(page, 330, 3000)

    def forged():
        glide(page, 0, 500)
        pick(page, "forged")
        page.wait_for_timeout(5500)
        if shot: shot("app_forged")
        page.locator('[data-testid="stMain"] img').first.evaluate("e => e.scrollIntoView({behavior: 'smooth', block: 'center'})")
        page.wait_for_timeout(3500)
        if shot: shot("app_whitebox")

    def forged_scan():
        glide(page, 0, 800)
        pick(page, "forged_scan")
        if shot: shot("app_qr")

    def ghost():
        pick(page, "ghost")
        if shot: shot("app_ghost")

    def queue():
        page.get_by_role("tab", name="Reviewer queue").click()
        page.wait_for_timeout(1500)
        if shot: shot("app_queue")

    def close():
        page.set_content(CARD.format(kicker="EVERY VERDICT, WITH PROOF",
                                     line="AI proposes. Code verifies. Anything uncertain goes to a human, with the reason.",
                                     foot="28 automated tests · 7 document types · AICTE Approval Process Handbook 2024-27"))

    for name, body in [("intro", intro), ("clean", clean), ("forged", forged), ("forged_scan", forged_scan),
                       ("ghost", ghost), ("queue", queue), ("close", close)]:
        scene(name, body)
    return marks


with sync_playwright() as p:
    browser = p.chromium.launch()

    IMG.mkdir(parents=True, exist_ok=True)
    clear_registry()
    ctx = browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=2)
    page = ctx.new_page()
    run(page, shot=lambda n: page.screenshot(path=str(IMG / f"{n}.png")), hold=False)
    ctx.close()

    clear_registry()
    raw = HERE / "raw"
    shutil.rmtree(raw, ignore_errors=True)
    ctx = browser.new_context(viewport={"width": W, "height": H}, record_video_dir=str(raw),
                              record_video_size={"width": W, "height": H})
    ctx.add_init_script(TICK)
    page = ctx.new_page()
    page.goto("about:blank")
    t0 = time.time()
    marks = run(page)
    path = Path(page.video.path())
    ctx.close()
    browser.close()

offsets = {k: v - t0 for k, v in marks.items()}
json.dump(offsets, open(HERE / "offsets.json", "w"), indent=1)
inputs, filters = ["-i", str(path)], []
for i, (name, at) in enumerate(offsets.items(), 1):
    inputs += ["-i", str(HERE / "audio" / f"{name}.mp3")]
    filters.append(f"[{i}:a]adelay={int((at + 0.2) * 1000)}:all=1[a{i}]")
mix = "".join(f"[a{i}]" for i in range(1, len(offsets) + 1)) + f"amix=inputs={len(offsets)}:normalize=0[a]"
subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(filters + [mix]), "-map", "0:v", "-map", "[a]",
                "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
                str(HERE / "pramaan_demo.mp4")], check=True)
shutil.rmtree(raw, ignore_errors=True)
print(offsets)
