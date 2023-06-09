    # Hello
    /*
    test   */

    # comment
    ldi r0, 0x00
    ldi r0, 0x00
    nop
    ldi r0, 0x00 # load immediate value into r0
    mv r1, r0
    mv r2, r1
    mv r3, r2
    mv r4, r3
    mv r5, r4
    mv r6, r5
    jreli +18  # 0x0020

.org 0x100
    # load some interessig pattern;Setup interrupt table
    ldi r0, 0xF0
    ldi r1, 0x55
    ldi r2, 0xAA
    ldi r3, 0x0F
    ldi r4, 0x81
    ldi r5, 0x04
    ldi r6, 0x02
    ldi r0, 0x80
    ldi r1, 0x40
    ldi r2, 0x20
    ldi r3, 0x10
    ldi r4, 0x08
    ldi r5, 0x04
    ldi r6, 0x02
    jrelr r0 # 0xF040
    nop
    jreli -32

    # Test 16 bit jump
    ldi r0, 0x40
    ldi r1, 0xF0
    jabsr r0r1 # 0xf040
    halt # never reached

.org 0xF040