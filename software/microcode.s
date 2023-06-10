    # Hello
    /*
    test   */

    # comment
    ldi r0, 0x00
    ldi r1, 0x01
    ldi r2, 0x02
    ldi r3, 0x03
    ldi r4, 0x04
    ldi r5, 0x05
    ldi r6, 0x06
    #ldi r0, 0x00
    #mv r1, r0
    #mv r2, r1
    #mv r3, r2
    #mv r4, r3
    #mv r5, r4
    #mv r6, r5
    #ldi r0, 0x01
    #ldi r1, 0x02
    #ldi r2, 0x04
    #ldi r3, 0x08
    #ldi r4, 0x10
    #ldi r5, 0x20
    #ldi r6, 0x40
    #ldi r5, 0x00
    #ldi r6, 0x00
    #ldi r0, 0x11
    #ldi r1, 0x12
    #ldi r2, 0x14
    #ldi r3, 0x18
    #ldi r4, 0x21
    #ldi r5, 0x22
    #ldi r6, 0x24
    #ldi r5, 0x28
    #ldi r6, 0x30
    #ldi r0, 0x01
    #ldi r1, 0x02
    #ldi r2, 0x04
    #ldi r3, 0x08
    #ldi r4, 0x10
    #ldi r5, 0x20
    #ldi r6, 0x40
    #
    ldi r5, 0x10 
    ldi r6, 0x00
    jabsr r5r6 # 0x00

.org 0x20
    ldi r0, 0xF0
    ldi r1, 0x55
    ldi r2, 0xAA
    ldi r3, 0x0F
    ldi r4, 0x81
    ldi r5, 0x04
    ldi r6, 0x02
    ldi r5, 0x00
    ldi r6, 0x00
    jabsr r5r6 # 0x00
