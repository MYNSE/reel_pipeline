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