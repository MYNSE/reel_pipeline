import re

def convert_srt_to_ass(input_file='output.srt', output_file='output.ass', fontname="Arial", fontsize=16, alignment=2):
    def srt_time_to_ass(t: str) -> str:
        h, m, s_ms = t.split(":")
        s, ms = s_ms.split(",")
        return f"{int(h)}:{m}:{s}.{int(ms)//10:02d}"

    def convert_line(line: str) -> str:
        return re.sub(r'<font color="#00ff00">(.*?)</font>', r'{\\c&HFF00&}\1{\\c}', line)

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 384
PlayResY: 288
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{fontname},{fontsize},&Hffffff,&Hffffff,&H0,&H0,0,0,0,0,100,100,0,0,1,1,0,{alignment},10,10,10,0

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.read().strip().split("\n")

    ass_lines = []
    i = 0
    while i < len(lines):
        if "-->" in lines[i]:
            start, end = lines[i].split(" --> ")
            start_ass = srt_time_to_ass(start.strip())
            end_ass = srt_time_to_ass(end.strip())
            text = convert_line(lines[i+1].strip())
            ass_lines.append(f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{text}")
            i += 2
        else:
            i += 1

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(ass_lines))
