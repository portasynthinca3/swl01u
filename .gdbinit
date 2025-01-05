set confirm off
set pagination off
set print pretty on
set print object on
set print static-members on
set print sevenbit-strings off
set disassemble-next-line on
target extended-remote :3333
#load images/rom.bin.elf 0x00000000
#load images/flash.bin.elf 0x02000000
