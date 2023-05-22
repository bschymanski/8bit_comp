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
ldi_r2 = 0b00111000
ldi_r3 = 0b01001000
ldi_r4 = 0b01011000
ldi_r5 = 0b01101000
ldi_r6 = 0b01111000
#
# move from rs to r0 or r1
mv_r0 = 0b00010000
mv_r1 = 0b00100000
mv_r2 = 0b00110000
mv_r3 = 0b01000000
mv_r4 = 0b01010000
mv_r5 = 0b01100000
mv_r6 = 0b01110000

# iiiiiiii  
# 00000001  - jrel +i Op2 is immediate

# jump relative imm
jreli = 0b00001001
#
# jump relative rs
jrelr = 0b00000001
#
# jump absolute imm
jabsi = 0b00001010
#
# jump absolute rs
jabsr =  0b00000010
jabsr0 = 0b00010010
jabsr1 = 0b00100010
jabsr2 = 0b00110010
jabsr3 = 0b01000010
jabsr4 = 0b01010010
jabsr5 = 0b01100010
jabsr6 = 0b01110010
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
rd2 = 0b00110000
rd3 = 0b01000000
rd4 = 0b01010000
rd5 = 0b01100000
rd6 = 0b01110000


rs0 = 0b00000001
rs1 = 0b00000010
rs2 = 0b00000011
rs3 = 0b00000100
rs4 = 0b00000101
rs5 = 0b00000110
rs6 = 0b00000111


# here the array with the program.
program = array.array('h', [
    # Code Address
    # Address 0 
    ldi_r0, 0x00, #1
    ldi_r1, 0x00, #2
    ldi_r2, 0x00, #3
    ldi_r3, 0x00,
    ldi_r4, 0x00,
    ldi_r5, 0x00,
    ldi_r6, 0x00,
    ldi_r0, 0x01, #4
    mv_r1, rs0,   #5
    mv_r2, rs1,   #6
    mv_r3, rs2,
    mv_r4, rs3,
    mv_r5, rs4,
    mv_r6, rs5,

    ldi_r0, 0x01, #7
    ldi_r1, 0x02,
    ldi_r2, 0x04,
    ldi_r3, 0x08,
    ldi_r4, 0x0F,
    ldi_r5, 0x10,
    ldi_r6, 0x20,
    mv_r1, rs0,   #8
    nop, 0x06,    #9
    nop, 0x07,    #10
    ldi_r0, 0x02, #11
    ldi_r1, 0x03, #11
    ldi_r2, 0x04, #12
    mv_r1, rs0,   #13
    mv_r2, rs1,   #14
    ldi_r1, 0x04, #15
    mv_r1, rs0,   #16
    nop, 0x06,    #17
    nop, 0x07,    #18
    ldi_r0, 0x00, #19
    ldi_r1, 0x00, #20
    jabsi, 0x00,
    jreli, 0xec,  #21
    jabsr, 0x00,
    
])

rom = bytearray(null * 32768)
proglength = len(program)
for i in range (0, proglength):
    rom[i] = program[i]
    print(hex(rom[i]))
    
print("-20 :")
print(bin(-20 & 0xFF))
print(hex(-20 & 0xFF))

with open("left_rom.bin", "wb") as out_file:
    out_file.write(rom);
