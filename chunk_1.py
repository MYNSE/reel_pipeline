def read_srt_blocks():
    with open("input.srt", "r", encoding="utf-8") as file, open("output.srt", "w", encoding="utf-8") as out_file:
        start = 0
        chunk_by = 2
        while True:
            line1 = file.readline()
            if not line1:
                break  # end of file
            line2 = file.readline()
            line3 = file.readline().strip()

            if line3.lstrip().startswith('<font color="'):
                start = 0  # reset

            
            words = line3.strip().split()
            length = start % chunk_by

            out_file.write(line1)
            out_file.write(line2)
            out_file.write(line3 + "\n\n")  # Add an empty line after each block

            print("Start:", start, length)
            print("Content:", line3)
            print("Current Word:", words)
            
            start += 1
            file.readline()  # skip the blank line
      
       

read_srt_blocks()