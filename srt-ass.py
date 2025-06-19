import re

INPUT_SRT = "input.srt"
OUTPUT_ASS = "output.ass"

def to_ass_timestamp(ts):
    """Convert timestamp like 00:00:01,120 to 0:00:01.12"""
    h, m, rest = ts.split(":")
    s, ms = rest.split(",")
    return f"{int(h)}:{int(m)}:{int(s)}.{ms[:2]}"

header = """[Script Info]
Title: Word-by-Word ASS
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,36,&H0000FF00,&H00666666,&H00000000,&H00000000,-1,0,1,1,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

with open(INPUT_SRT, "r", encoding="utf-8") as f:
    srt_data = f.read()

# Split into subtitle blocks
blocks = re.split(r"\n\n+", srt_data.strip())

with open(OUTPUT_ASS, "w", encoding="utf-8") as f:
    f.write(header)

    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) < 3:
            continue

        times = lines[1]
        text = " ".join(lines[2:])

        # Extract start and end times
        match = re.match(r"(\d{2}:\d{2}:\d{2}),(\d{3}) --> (\d{2}:\d{2}:\d{2}),(\d{3})", times)
        if not match:
            continue

        start = to_ass_timestamp(match[1] + "," + match[2])
        end = to_ass_timestamp(match[3] + "," + match[4])

        # Find the highlighted word inside <font> tags
        highlighted = re.search(r'<font color="#00ff00">(.*?)</font>', text)
        if highlighted:
            word = highlighted.group(1)
            # Remove HTML tags from full line
            cleaned_text = re.sub(r'<font color="#00ff00">(.*?)</font>', r'\1', text)
            # Replace the word with a karaoke tag
            parts = cleaned_text.split()
            karaoke_line = ""
            for w in parts:
                if w.strip(',.?!') == word.strip(',.?!'):
                    karaoke_line += f"{{\\k20}}{w} "
                else:
                    karaoke_line += f"{{\\k0}}{w} "
            karaoke_line = karaoke_line.strip()
        else:
            # No highlight, just write plain line
            karaoke_line = "{\\k0}" + " ".join(text.split())

        pop_in_prefix = r"{\fscx70\fscy70\t(0,500,\fscx100\fscy100)}"
        full_line = f"{pop_in_prefix}{karaoke_line}"

        f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{full_line}\n")

print("✅ ASS file created with karaoke-style word highlighting.")
