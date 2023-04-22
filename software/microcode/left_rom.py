import array
import binascii
#print (len(program))

ea = [0xea];
null = [0x00];

# Instruction architecure
# 
# ........ ........ -- 
# ........ ......00 -- stepping mode
# ........ ......01 -- relative jump
# ........ ......10 -- absolute jump
# ........ ....0... -- 2nd operand is register
# ........ ....1... -- 2nd operand is immediate
# ........ dddd.... -- reg operand 1 ("RD")
# ....ssss ........ -- reg operand 2 ("RS")
# iiiiiiii ........ -- immediate


# instructions
# 00000000 00000000  - nop
nop = 0b00000000
#  
ldi_r0 = 0b00011000
ldi_r1 = 0b00101000
#
# move from rs to r0 or r1
mv_r0 = 0b00010000
mv_r1 = 0b00100000

# iiiiiiii  
# 00000001  - jrel +i Op2 is immediate
jrel = 0b00001001
#

# jump relative imm
jreli = 0b00001001
#
# jump relative rs
jrelr = 0b00000010
#
# jump absolute imm
jabsi = 0b00001001
#
# jump absolute rs
jabsr = 0b00000010


# aaaaaaaa
# 00000010  - jabs a Op2 is immediate
jabs = 0b00001010
#
# 00000000
# 00000001  - halt
halt = 0b00001001
#
# 00000000
# 00000010  - reset
reset = 0b00001010

# register
rd0 = 0b00010000
rd1 = 0b00100000
rs0 = 0b00000001
rs1 = 0b00000010


# here the array with the program.
program = array.array('h', [
    # Code Address
    # Address 0 
    nop, nop,
    
    # Address 1
    ldi_r0, 0x01,
    
    # Address 2
    ldi_r1, 0x02,

    # Address 3
    mv_r0, rs1,

    # Address 4
    ldi_r1, 0x04,
    
    # Address 5
    mv_r1, rs0,

    # Address 6
    nop, 0x06,

    # Address 7
    nop, 0x07,

    # Address 8
    jabs, 0x09,

    # 9
    jrel, 0xf8
])

rom = bytearray(null * 32768)
proglength = len(program)
for i in range (0, proglength):
    rom[i] = program[i]
    print(hex(rom[i]))
    
#print("-5 :")
#print(bin(-5 & 0xFF))
#print(hex(-5 & 0xFF))

with open("left_rom.bin", "wb") as out_file:
    out_file.write(rom);
