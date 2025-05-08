
SECTION "Header", ROM0[$100]

    jp PenguinEntry

    ds $150 - @, 0 ; Make room for the header

PenguinEntry:
ld sp, $DFFF
Labelfoo:
ld b, 6
ld a, b
ld hl, 49152
ld [hl], a

        PenguinPush:
        push bc
        push de
        push hl
        ret

        PenguinPop:
        pop bc
        pop de
        pop hl
        ret

        PenguinMult:
        ;not implemented

        PenguinCalcOffset:

        PenguinMemCopy:
        ld a, [de]
        ld [hli], a
        inc de
        dec bc
        ld a, b
        or a, c
        jp nz, PenguinMemCopy
        ret


        control_LCDon:
        ld a, $91
        ld [$FF40], a
        ret
        