/**
 * file test.S
 * brief Microcode Test Code
 *
 * Test microcode
 *
 * author Samuel Fitzsimons (rainbain)
 * date 2025
 */

#include "cpu.h"

    NOP

    DAR $ar0
    DAR $ar1
    DAR $ar2
    DAR $ar3
demo_label_1:

    IAR $ar0
    IAR $ar1
    IAR $ar2
    IAR $ar3

    SUBARN $ar0
    SUBARN $ar1
    SUBARN $ar2
    SUBARN $ar3

    ADDARN $ar3, $ix2
    ADDARN $ar1, $ix1
    ADDARN $ar0, $ix3
    ADDARN $ar2, $ix0

    HALT

    LOOP $0
    LOOP $1
    LOOP $2
    LOOP $4
    LOOP $8
    LOOP $10

    BLOOP $0, 0x44d8 << 1
    BLOOP $1, 0x931a << 1
    BLOOP $2, 0x475a << 1
    BLOOP $4, demo_label_1
    BLOOP $8, 0x3ae3 << 1
    BLOOP $10, 0xda30 << 1

    LRI $0, 0b0000110110010011
    LRI $1, 0b1110001111100110
    LRI $2, 0b1111101000000001
    LRI $4, 0b0100010110101001
    LRI $8, 0b1011011101010101
    LRI $10, 0b1010001000100000

    LR $0, 37940 << 1
    LR $1, demo_label_2
    LR $2, 4044 << 1
    LR $4, demo_label_2
    LR $8, 39494 << 1
demo_label_2:    LR $10, 33111 << 1

    SR 0x7381 << 1, $0
    SR 0xe057 << 1, $1
    SR demo_label_3, $2
    SR 0x204a << 1, $4
    SR 0x7fa5 << 1, $8
demo_label_3:    SR 0x5fff << 1, $10

    SRR $ar3, $0
    SRR $ar2, $1
    SRR $ar2, $2
    SRR $ar1, $4
    SRR $ar0, $8
    SRR $ar3, $10

    ifcc CC_GE
    ifcc CC_LT
    ifcc CC_GT
    ifcc CC_LE
    ifcc CC_NZ
    ifcc CC_Z
    ifcc CC_NC
    ifcc CC_C
    ifcc CC_NLZ
    ifcc CC_LZ
    ifcc CC_V
    ifcc CC_AL

    jcc 0X47a1 << 1, CC_GE
    jcc 0Xb48c << 1, CC_LT
    jcc 0Xd636 << 1, CC_GT
    jcc 0Xfce4 << 1, CC_LE
    jcc 0X2f8b << 1, CC_NZ
    jcc 0Xd252 << 1, CC_Z
    jcc 0X5929 << 1, CC_NC
    jcc 0X9ec8 << 1, CC_C
    jcc 0X93ce << 1, CC_NLZ
    jcc 0X5218 << 1, CC_LZ
    jcc 0Xa0e4 << 1, CC_V
    jcc 0X07af << 1, CC_AL

    callcc 0x0fb3 << 1, CC_GE
    callcc 0x29b4 << 1, CC_LT
    callcc 0x64a7 << 1, CC_GT
    callcc 0xad06 << 1, CC_LE
    callcc 0xcfe7 << 1, CC_NZ
    callcc 0xe494 << 1, CC_Z
    callcc 0xed97 << 1, CC_NC
    callcc 0xbea0 << 1, CC_C
    callcc 0x4f52 << 1, CC_NLZ
    callcc 0x96c5 << 1, CC_LZ
    callcc 0x6c00 << 1, CC_V
    callcc 0x1673 << 1, CC_AL

    retcc CC_GE
    retcc CC_LT
    retcc CC_GT
    retcc CC_LE
    retcc CC_NZ
    retcc CC_Z
    retcc CC_NC
    retcc CC_C
    retcc CC_NLZ
    retcc CC_LZ
    retcc CC_V
    retcc CC_AL

    rticc CC_GE
    rticc CC_LT
    rticc CC_GT
    rticc CC_LE
    rticc CC_NZ
    rticc CC_Z
    rticc CC_NC
    rticc CC_C
    rticc CC_NLZ
    rticc CC_LZ
    rticc CC_V
    rticc CC_AL

    addi $ac0.m, 0x328d
    addi $ac0.m, 0xCD72
    addi $ac1.m, 0x328d
    addi $ac1.m, 0xCD72

    xori $ac0.m, 0xaff4
    xori $ac0.m, 0x500B
    xori $ac1.m, 0xaff4
    xori $ac1.m, 0x500B

    andi $ac0.m, 0xF0DB
    andi $ac0.m, 0x0f24
    andi $ac1.m, 0xF0DB
    andi $ac1.m, 0x0f24

    ori $ac0.m, 0xfb10
    ori $ac0.m, 0x4EF
    ori $ac1.m, 0xfb10
    ori $ac1.m, 0x4EF

    cmpi $ac0.m, 0x328d
    cmpi $ac0.m, 0xCD72
    cmpi $ac1.m, 0x328d
    cmpi $ac1.m, 0xCD72

    andf $ac0.m, 0xcd
    andf $ac0.m, 0xFF32
    andf $ac1.m, 0xcd
    andf $ac1.m, 0xFF32

    andcf $ac0.m, 0x4dcc
    andcf $ac0.m, 0xB233
    andcf $ac1.m, 0x4dcc
    andcf $ac1.m, 0xB233

    lsrn
    asrn

    ilrr $ac0.m, $ar0
    ilrr $ac1.m, $ar1
    ilrr $ac1.m, $ar2
    ilrr $ac0.m, $ar3

    ilrrd $ac0.m, $ar0
    ilrrd $ac1.m, $ar1
    ilrrd $ac1.m, $ar2
    ilrrd $ac0.m, $ar3

    ilrri $ac0.m, $ar0
    ilrri $ac1.m, $ar1
    ilrri $ac1.m, $ar2
    ilrri $ac0.m, $ar3

    ilrrn $ac0.m, $ar0
    ilrrn $ac1.m, $ar1
    ilrrn $ac1.m, $ar2
    ilrrn $ac0.m, $ar3

    addis $ac0.m, 69
    addis $ac0.m, -128
    addis $ac1.m, -69
    addis $ac1.m, 112

    cmpis $ac0.m, 69
    cmpis $ac0.m, -128
    cmpis $ac1.m, -69
    cmpis $ac1.m, 112

    lris $ax0.L, 0x09
    lris $ax1.L, 0xf5
    lris $ax0.H, 0x54
    lris $ax1.H, 0x94
    lris $ac0.L, 0x78
    lris $ac1.L, 0xb0
    lris $ac0.M, 0x69
    lris $ac1.M, 0xbd

    loopi 0x00
    loopi 0x01
    loopi 0x02
    loopi 0x04
    loopi 0x08
    loopi 0x10
    loopi 0x20
    loopi 0x40
    loopi 0x80

test_label_3:
    bloopi 0x00, test_label_3
    bloopi 0x01, 0x42aa << 1
    bloopi 0x02, 0x39a7 << 1
    bloopi 0x04, 0xfbd6 << 1
    bloopi 0x08, 0xb0c6 << 1
    bloopi 0x10, 0xa252 << 1
    bloopi 0x20, 0x7d85 << 1
    bloopi 0x40, 0xee5e << 1
    bloopi 0x80, 0xfd66 << 1

    SBCLR 0
    SBCLR 1
    SBCLR 2
    SBCLR 4

    SBSET 0
    SBSET 1
    SBSET 2
    SBSET 4

    LSL $ac0, 0x00
    LSL $ac0, 0x01
    LSL $ac0, 0x02
    LSL $ac0, 0x04
    LSL $ac0, 0x08
    LSL $ac0, 0x10
    LSL $ac0, -0x20

    LSR $ac0, -0x00
    LSR $ac0, -0x01
    LSR $ac0, -0x02
    LSR $ac0, -0x04
    LSR $ac0, -0x08
    LSR $ac0, -0x10
    LSR $ac0, 0x20

    LSL $ac1, 0x00
    LSL $ac1, 0x01
    LSL $ac1, 0x02
    LSL $ac1, 0x04
    LSL $ac1, 0x08
    LSL $ac1, 0x10
    LSL $ac1, -0x20

    LSR $ac1, -0x00
    LSR $ac1, -0x01
    LSR $ac1, -0x02
    LSR $ac1, -0x04
    LSR $ac1, -0x08
    LSR $ac1, -0x10
    LSR $ac1, 0x20

    ASL $ac0, 0x00
    ASL $ac0, 0x01
    ASL $ac0, 0x02
    ASL $ac0, 0x04
    ASL $ac0, 0x08
    ASL $ac0, 0x10
    ASL $ac0, -0x20

    ASR $ac0, -0x00
    ASR $ac0, -0x01
    ASR $ac0, -0x02
    ASR $ac0, -0x04
    ASR $ac0, -0x08
    ASR $ac0, -0x10
    ASR $ac0, 0x20

    ASL $ac1, 0x00
    ASL $ac1, 0x01
    ASL $ac1, 0x02
    ASL $ac1, 0x04
    ASL $ac1, 0x08
    ASL $ac1, 0x10
    ASL $ac1, -0x20

    ASR $ac1, -0x00
    ASR $ac1, -0x01
    ASR $ac1, -0x02
    ASR $ac1, -0x04
    ASR $ac1, -0x08
    ASR $ac1, -0x10
    ASR $ac1, 0x20

    SI 0x7f << 1, 0xdc26

    jrcc $0, CC_GE
    jrcc $1, CC_LT
    jrcc $2, CC_GT
    jrcc $4, CC_LE
    jrcc $0, CC_NZ
    jrcc $1, CC_Z
    jrcc $2, CC_NC
    jrcc $3, CC_C
    jrcc $4, CC_NLZ
    jrcc $5, CC_LZ
    jrcc $6, CC_V
    jrcc $7, CC_AL

    callrcc $0, CC_GE
    callrcc $1, CC_LT
    callrcc $2, CC_GT
    callrcc $4, CC_LE
    callrcc $0, CC_NZ
    callrcc $1, CC_Z
    callrcc $2, CC_NC
    callrcc $3, CC_C
    callrcc $4, CC_NLZ
    callrcc $5, CC_LZ
    callrcc $6, CC_V
    callrcc $7, CC_AL

    lrr $0, $ar1
    lrr $1, $ar0
    lrr $2, $ar3
    lrr $4, $ar2
    lrr $8, $ar1
    lrr $10, $ar0

    lrrd $0, $ar1
    lrrd $1, $ar0
    lrrd $2, $ar3
    lrrd $4, $ar2
    lrrd $8, $ar1
    lrrd $10, $ar0

    lrri $0, $ar1
    lrri $1, $ar0
    lrri $2, $ar3
    lrri $4, $ar2
    lrri $8, $ar1
    lrri $10, $ar0

    lrrn $0, $ar1
    lrrn $1, $ar0
    lrrn $2, $ar3
    lrrn $4, $ar2
    lrrn $8, $ar1
    lrrn $10, $ar0

    srr $ar1, $0
    srr $ar0, $1
    srr $ar3, $2
    srr $ar2, $4
    srr $ar1, $8
    srr $ar0, $10

    srrd $ar1, $0
    srrd $ar0, $1
    srrd $ar3, $2
    srrd $ar2, $4
    srrd $ar1, $8
    srrd $ar0, $10

    srri $ar1, $0
    srri $ar0, $1
    srri $ar3, $2
    srri $ar2, $4
    srri $ar1, $8
    srri $ar0, $10

    srrn $ar1, $0
    srrn $ar0, $1
    srrn $ar3, $2
    srrn $ar2, $4
    srrn $ar1, $8
    srrn $ar0, $10

    mrr $0, $13
    mrr $1, $00
    mrr $2, $10
    mrr $4, $14
    mrr $8, $9
    mrr $10, $00

    lrs $24, 0x70 << 1
    lrs $25, 0x6b << 1
    lrs $26, 0x52 << 1
    lrs $27, 0x24 << 1
    lrs $28, 0x2e << 1
    lrs $29, 0x2d << 1
    lrs $30, 0x76 << 1
    lrs $31, 0x51 << 1

    srsh 0x70 << 1, $ac0.h
    srsh 0x0f << 1, $ac0.h
    srsh 0x70 << 1, $ac1.h
    srsh 0x0f << 1, $ac1.h

    srs 0x70 << 1, $28
    srs 0x6b << 1, $29
    srs 0x76 << 1, $30
    srs 0x2e << 1, $31

    xorr'dr $ac0.m, $ax0.h : $ar0
    xorr'dr $ac1.m, $ax0.h : $ar1
    xorr'dr $ac0.m, $ax1.h : $ar2
    xorr'dr $ac1.m, $ax1.h : $ar3

    andr'ir $ac0.m, $ax0.h : $ar0
    andr'ir $ac1.m, $ax0.h : $ar1
    andr'ir $ac0.m, $ax1.h : $ar2
    andr'ir $ac1.m, $ax1.h : $ar3

    orr'nr $ac0.m, $ax0.h : $ar0
    orr'nr $ac1.m, $ax0.h : $ar1
    orr'nr $ac0.m, $ax1.h : $ar2
    orr'nr $ac1.m, $ax1.h : $ar3

    andc'mv $ac0.m : $24, $28
    andc'mv $ac1.m : $25, $30

    orc'mv $ac0.m  : $26, $29
    orc'mv $ac1.m : $27, $31

    xorc's $ac0.m : $ar0, $28
    xorc's $ac1.m : $ar1, $29

    not's $ac0.m : $ar2, $30
    not's $ac1.m : $ar3, $31

    LSRNRX'sn $ac0, $ax0.h : $ar0, $28
    LSRNRX'sn $ac1, $ax0.h : $ar1, $29
    LSRNRX'sn $ac0, $ax1.h : $ar2, $30
    LSRNRX'sn $ac1, $ax1.h : $ar3, $31

    ASRNRX'dr $ac0, $ax0.h : $ar0
    ASRNRX'dr $ac1, $ax0.h : $ar0
    ASRNRX'dr $ac0, $ax1.h : $ar0
    ASRNRX'dr $ac1, $ax1.h : $ar0

    LSRNR'l $ac0 : $24, $ar0
    LSRNR'l $ac1 : $25, $ar1

    ASRNR'l $ac0 : $26, $ar2
    ASRNR'l $ac1 : $28, $ar3

    ADDR'ln $ac0, $24 : $24, $ar0
    ADDR'ln $ac1, $25 : $25, $ar1
    ADDR'ln $ac1, $26 : $26, $ar2
    ADDR'ln $ac0, $27 : $28, $ar3

    ADDAX $ac0, $ax0
    ADDAX'ls $ac1, $ax0 : $24, $ac1.m
    ADDAX $ac0, $ax1
    ADDAX $ac1, $ax1

    ADD $ac0
    ADD'ls $ac1 : $25, $ac0.m

    ADDP'ls $ac0 : $26, $ac0.m
    ADDP $ac1

    SUBR'ls $ac0, $24 : $27, $ac1.m
    SUBR'sl $ac1, $25 : $ac1.m, $24
    SUBR'sl $ac1, $26 : $ac0.m, $25
    SUBR'sl $ac0, $27 : $ac0.m, $26

    SUBAX $ac0, $ax0
    SUBAX'sl $ac1, $ax0 : $ac1.m, $27
    SUBAX $ac0, $ax1
    SUBAX $ac1, $ax1

    SUB'lsn $ac0 : $24, $ac0.m
    SUB $ac1

    SUBP $ac0
    SUBP'lsn $ac1 : $25, $ac1.m

    MOVR'lsn $ac0, $24 : $26, $ac0.m
    MOVR'lsn $ac1, $25 : $27, $ac1.m
    MOVR'sln $ac1, $26 : $ac0.m, $24
    MOVR'sln $ac0, $27 : $ac1.m, $25

    MOVAX $ac0, $ax0
    MOVAX $ac1, $ax0
    MOVAX'sln $ac0, $ax1 : $ac1.m, $26
    MOVAX $ac1, $ax1

    MOV'sln $ac0 : $ac0.m, $27
    MOV $ac1

    MOVP $ac0
    MOVP'lsm $ac1 : $24, $ac0.m

    ADDAXL'lsm $ac0, $ax0.l : $24, $ac0.m
    ADDAXL'lsm $ac1, $ax0.l : $25, $ac1.m
    ADDAXL'lsm $ac0, $ax1.l : $26, $ac1.m
    ADDAXL'slm $ac1, $ax1.l : $ac1.m, $24

    INCM'slm $ac0.m : $ac1.m, $25
    INCM $ac1.m

    INC $ac0
    INC'slm $ac1 : $ac0.m, $26

    DECM'slm $ac0.m : $ac0.m, $27
    DECM $ac1.m
    
    DEC $ac0
    DEC'lsnm $ac1 : $24, $ac1.m

    NEG'lsnm $ac0 : $25, $ac0.m
    NEG $ac1

    MOVNP'lsnm $ac0 : $26, $ac1.m
    MOVNP $ac1

    NX
    NX'lsnm : $27, $ac0.m

    CLR'slnm $ac0 : $ac1.m, $24
    CLR'dr $ac1 : $ar0

    CMP'slnm : $ac0.m, $25

    MULAXH'slnm : $ac0.m, $26

    CLRP'slnm : $ac1.m, $27

    TSTPROD'ld : $ax0.l, $ax1.l, $ar1

    TSTAXH'ld $ax0.h : $ax0.h, $ax1.l, $ar0
    TSTAXH'ld $ax1.h : $ax0.l, $ax1.h, $ar2

    m2'ld : $ax0.h, $ax1.h, $ar3

    m0'ld : $ax0.l, $ax1.l, $ar1

    clr15'ld : $ax0.h, $ax1.l, $ar1

    set15'ld : $ax0.l, $ax1.h, $ar2

    set16'ld : $ax0.h, $ax1.h, $ar3

    set40'ldax : $ax0, $ar0

    mul'ldax $ax0: $ax1, $ar1
    mul'ldax $ax1: $ax1, $ar2
    mul'ldax $ax1: $ax0, $ar3
    mul'ldn $ax1: $ax0.l, $ax1.l, $ar0

    asr16 $ac0
    asr16'ldn $ac1: $ax0.h, $ax1.h, $ar1

    MULMVZ'ldn $ax1, $ac1 : $ax0.l, $ax1.h, $ar2
    MULMVZ $ax1, $ac1
    MULMVZ'ldn $ax1, $ac0 : $ax0.h, $ax1.l, $ar3
    MULMVZ $ax1, $ac0

    MULAC'LDAXN $ax1, $ac1 : $ax0, $ar0
    MULAC $ax1, $ac1
    MULAC'LDAXN $ax1, $ac0 : $ax0, $ar1
    MULAC $ax1, $ac0

    MULXMV $ax0.h, $ax1.l, $ac0
    MULXMV'LDAXN $ax0.l, $ax1.l, $ac0  : $ax1, $ar0
    MULXMV $ax0.h, $ax1.h, $ac0
    MULXMV $ax0.l, $ax1.h, $ac0
    MULXMV'LDAXN $ax0.h, $ax1.l, $ac1  : $ax1, $ar1
    MULXMV $ax0.l, $ax1.l, $ac1
    MULXMV $ax0.h, $ax1.h, $ac1
    MULXMV $ax0.l, $ax1.h, $ac1

    MULC $ac0.m, $ax0.h
    MULC'LDM $ac1.m, $ax0.h : $ax0.h, $ax1.l, $ar0
    MULC'LDM $ac0.m, $ax1.h : $ax0.l, $ax1.h, $ar1
    MULC $ac1.m, $ax1.h

    CMPAXH $ac0, $ax0.h
    CMPAXH'LDM $ac1, $ax0.h : $ax0.l, $ax1.l, $ar2
    CMPAXH'LDM $ac0, $ax1.h : $ax0.h, $ax1.h, $ar3
    CMPAXH $ac1, $ax1.h

    MULCMVZ'LDAXM $ac0.m, $ax0.h, $ac0 : $ax0, $ar0
    MULCMVZ $ac1.m, $ax0.h, $ac0
    MULCMVZ $ac0.m, $ax1.h, $ac0
    MULCMVZ $ac1.m, $ax1.h, $ac0
    MULCMVZ $ac0.m, $ax0.h, $ac1
    MULCMVZ $ac1.m, $ax0.h, $ac1
    MULCMVZ'LDAXM $ac0.m, $ax1.h, $ac1 : $ax1, $ar0
    MULCMVZ'LDAXM $ac1.m, $ax1.h, $ac1 : $ax0, $ar1

    MULCAC'LDAXM $ac0.m, $ax0.h, $ac0 : $ax1, $ar1
    MULCAC $ac1.m, $ax0.h, $ac0
    MULCAC $ac0.m, $ax1.h, $ac0
    MULCAC $ac1.m, $ax1.h, $ac0
    MULCAC $ac0.m, $ax0.h, $ac1
    MULCAC $ac1.m, $ax0.h, $ac1
    MULCAC'LDNM $ac0.m, $ax1.h, $ac1 : $ax0.l, $ax1.l, $ar0
    MULCAC'LDNM $ac1.m, $ax1.h, $ac1 : $ax0.h, $ax1.l, $ar1

    MULCMV'LDNM $ac0.m, $ax0.h, $ac0 : $ax0.l, $ax1.h, $ar2
    MULCMV $ac1.m, $ax0.h, $ac0
    MULCMV $ac0.m, $ax1.h, $ac0
    MULCMV $ac1.m, $ax1.h, $ac0
    MULCMV $ac0.m, $ax0.h, $ac1
    MULCMV $ac1.m, $ax0.h, $ac1
    MULCMV'LDNM $ac0.m, $ax1.h, $ac1 : $ax0.h, $ax1.h, $ar3
    MULCMV'LDAXNM $ac1.m, $ax1.h, $ac1 : $ax0, $ar0

    MADDX'LDAXNM $24, $25 : $ax0, $ar1
    MADDX $26, $27

    MSUBX'LDAXNM $24, $25 : $ax1, $ar0
    MSUBX $26, $27

    MADDC'LDAXNM $ac0.m, $ax1.h : $ax1, $ar1
    MADDC $ac1.m, $ax1.h
    MADDC'dr $ac0.m, $ax1.h : $ar0
    MADDC $ac1.m, $ax1.h

    MSUBC'dr $ac0.m, $ax1.h : $ar0
    MSUBC $ac1.m, $ax1.h
    MSUBC'dr $ac0.m, $ax1.h : $ar0
    MSUBC $ac1.m, $ax1.h

    lsl16'dr $ac0 : $ar0
    lsl16 $ac1

    madd $ax0
    madd'dr $ax1 : $ar0

    lsr16'dr $ac0 : $ar0
    lsr16 $ac1

    msub $ax0
    msub'dr $ax1 : $ar0

    ADDPAXZ $ac1, $ax0
    ADDPAXZ'dr $ac1, $ax1 : $ar0
    ADDPAXZ $ac1, $ax0
    ADDPAXZ'dr $ac1, $ax1 : $ar0
    
    clr'dr $ac0 : $ar0
    clr $ac1

    movpz $ac0
    movpz'dr $ac1 : $ar0