ea = [0xea];
null = [0x00];

pos_00 = 0x00
pos_01 = 0x01
pos_02 = 0x02
pos_03 = 0x03
pos_04 = 0x04
pos_05 = 0x05
pos_06 = 0x06
pos_07 = 0x07
pos_08 = 0x08
pos_09 = 0x09
pos_10 = 0x0a
pos_11 = 0x0b
pos_12 = 0x0c
pos_13 = 0x0d
pos_14 = 0x0e
pos_15 = 0x0f
pos_16 = 0x00
pos_17 = 0x10
pos_18 = 0x20
pos_19 = 0x30
pos_20 = 0x40
pos_21 = 0x50
pos_22 = 0x60
pos_23 = 0x70
pos_24 = 0x80
pos_25 = 0x90
pos_26 = 0xa0
pos_27 = 0xb0
pos_28 = 0xc0
pos_29 = 0xd0
pos_30 = 0xe0
pos_31 = 0xf0


rom = bytearray(null * 32768)

rom[0]  = pos_00
rom[1]  = pos_01
rom[2]  = pos_02
rom[3]  = pos_03
rom[4]  = pos_04
rom[5]  = pos_05
rom[6]  = pos_06
rom[7]  = pos_07
rom[8]  = pos_08
rom[9]  = pos_09
rom[10] = pos_10
rom[11] = pos_11
rom[12] = pos_12
rom[13] = pos_13
rom[14] = pos_14
rom[15] = pos_15
rom[16]  = pos_16
rom[17]  = pos_17
rom[18]  = pos_18
rom[19]  = pos_19
rom[20]  = pos_20
rom[21]  = pos_21
rom[22]  = pos_22
rom[23]  = pos_23
rom[24]  = pos_24
rom[25]  = pos_25
rom[26] = pos_26
rom[27] = pos_27
rom[28] = pos_28
rom[29] = pos_29
rom[30] = pos_30
rom[31] = pos_31


with open("left_rom.bin", "wb") as out_file:
    out_file.write(rom);
