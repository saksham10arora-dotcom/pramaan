"""Turn the narration column of script.md into one audio file per scene."""
import asyncio
import re
from pathlib import Path

import edge_tts

HERE = Path(__file__).parent
VOICE = "en-IN-NeerjaNeural"


async def main():
    for line in (HERE / "script.md").read_text().splitlines():
        m = re.match(r"\| (\w+) \| .*? \| (.+) \|$", line)
        if m and m.group(1) != "#":
            await edge_tts.Communicate(m.group(2), VOICE, rate="+4%").save(str(HERE / "audio" / f"{m.group(1)}.mp3"))
            print(m.group(1))


asyncio.run(main())
