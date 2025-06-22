def read_srt_blocks():
    with open("input.srt", "r", encoding="utf-8") as file, open("output.srt", "w", encoding="utf-8") as out_file:
        start = 0
        chunk_by = 2
        buffer = False
        while True:
            line1 = file.readline()
            if not line1:
                break  # end of file
            line2 = file.readline()
            line3 = file.readline().strip()

            if line3.lstrip().startswith('<font color="'):
                start = 0  # reset
                line3 = r"{\fscx70\fscy70\t(0,500,\fscx100\fscy100)}" + line3
    
            words = line3.strip().split()
            has_font = '<font color="' in line3
            length = start % chunk_by

            if has_font:
                words = words[start-length:start-length+chunk_by+1]
            else: 
                words = words[start-length:start-length+chunk_by]

            words = ' '.join(words)
            #print("Start:", start, length)
            #print("Content:", line3)
            #print("Current Word:", words)

            out_file.write(line1)
            out_file.write(line2)
            if (words.startswith('<font color="') or not has_font) and not buffer: # if (words.startswith('<font color="') or not has_font) and not buffer:
                buffer = True
                out_file.write(r"{\fscx80\fscy80\t(0,500,\fscx100\fscy100)}" + words + "\n\n")

            else:
                buffer = False
                out_file.write(words + "\n\n")  # Add an empty line after each block

            
            if has_font:    # checks in case there's a pause with no font
                start += 1
            file.readline()  # skip the blank line

read_srt_blocks()