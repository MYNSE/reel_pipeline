import re
def chunk_srt(input_file='input.srt', output_file='output.srt', chunk_by = 3, start_scale=80, end_scale=100, transition_time=0.100):
    with open(input_file, "r", encoding="utf-8") as file, open(output_file, "w", encoding="utf-8") as out_file:
        start = 0
        buffer = False
        while True:
            line1 = file.readline()
            if not line1:
                break  # end of file
            line2 = file.readline()
            line3 = file.readline().strip()

            if line3.lstrip().startswith('<font color="'):
                start = 0  # reset
                buffer = False
    
            words = line3.strip().split()
            has_font = '<font color="' in line3
            length = start % chunk_by

            if has_font:
                words = words[start-length:start-length+chunk_by+1]
            else: 
                words = words[start-length:start-length+chunk_by]
            words = ' '.join(words)
   
            out_file.write(line1)
            out_file.write(line2)

            transition_str = f"0,{transition_time}"
            
            """
            \fade (intial alpha, mid alpha, final alpha, start fade in, end fade in/start fade out, end fade out)
            
            """
            fade = True
            #if fade:
                #pop_in += f",255,255,255,0,0,{transition_time}" 
            
            pop_in = rf"{{\fscx{start_scale}\fscy{start_scale}\t({transition_str},\fscx{end_scale}\fscy{end_scale})}}"
            

            if (words.startswith('<font color="') or not has_font) and not buffer: 
                buffer = True
                out_file.write(pop_in + words + "\n\n")
                #out_file.write(r"{\fscx80\fscy80\t(0,100,\fscx100\fscy100)}" + words + "\n\n")
            else:
                buffer = False
                out_file.write(words + "\n\n")  # Add an empty line after each block
            
            if has_font:    # Checks in case there's a pause with no font
                start += 1
            file.readline()  # skip the blank line



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