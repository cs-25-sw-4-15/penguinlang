  INCLUDE "hardware.inc"
  SECTION "Header", ROM0[$100]
  jp PenguinEntry
  ds $150 - @, 0 ; Make room for the header
PenguinEntry:
  ld sp, $DFFF
  ld a, 0
  ld [wCurKeys], a
  ld [wNewKeys], a
  push bc
  push de
  push hl
  call Labelcontrol_waitVBlankStart
  pop hl
  pop de
  pop bc
  push bc
  push de
  push hl
  call Labelcontrol_LCDoff
  pop hl
  pop de
  pop bc
  push bc
  push de
  push hl
  ld de, Labeltileset_block_0Start
  ld hl, $8000
  ld bc, Labeltileset_block_0End - Labeltileset_block_0Start
  call PenguinMemCopy
  pop hl
  pop de
  pop bc
  push bc
  push de
  push hl
  ld de, Labeltileset_block_2Start
  ld hl, $9000
  ld bc, Labeltileset_block_2End - Labeltileset_block_2Start
  call PenguinMemCopy
  pop hl
  pop de
  pop bc
  push bc
  push de
  push hl
  ld de, Labeltilemap0Start
  ld hl, $9800
  ld bc, Labeltilemap0End - Labeltilemap0Start
  call PenguinMemCopy
  pop hl
  pop de
  pop bc
  ld b, 16
  ld a, b
  ld hl, 49168
  ld [hl], a
  ld b, 25
  ld a, b
  ld hl, 49169
  ld [hl], a
  ld b, 100
  ld a, b
  ld hl, 49170
  ld [hl], a
  ld b, 0
  ld a, b
  ld hl, 49171
  ld [hl], a
L0:
  ld hl, 49171
  ld a, [hl]
  ld b, a
  ld c, 40
  ld a, b
  cp c
  ld b, 0
  jp c, LT_TRUE_0
  jp LT_END_0
LT_TRUE_0:
  ld b, 1
LT_END_0:
  ld a, b
  cp 0
  jp nz, L1
  jp L2
L1:
  ld b, 0
  ld hl, 49171
  ld a, [hl]
  ld c, a
  push bc
  push de
  push hl
  ld a, b
  ld e, 4
  ld c, c
  ld b, 0
  ld d, 8
  ld hl, 0
loop2:
  srl e
  jp nc, no_add1
  add hl, bc
no_add1:
  sla c
  rl b
  dec d
  jp nz, loop2
  ld bc, 65024
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
  ld hl, 49171
  ld a, [hl]
  ld b, a
  ld c, 1
  ld a, b
  add a, c
  ld b, a
  ld a, b
  ld hl, 49171
  ld [hl], a
  jp L0
L2:
  ld b, 10
  ld c, 0
  push bc
  push de
  push hl
  ld a, b
  ld e, 4
  ld c, c
  ld b, 0
  ld d, 8
  ld hl, 0
loop4:
  srl e
  jp nc, no_add3
  add hl, bc
no_add3:
  sla c
  rl b
  dec d
  jp nz, loop4
  ld bc, 65026
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
  ld b, 11
  ld c, 1
  push bc
  push de
  push hl
  ld a, b
  ld e, 4
  ld c, c
  ld b, 0
  ld d, 8
  ld hl, 0
loop6:
  srl e
  jp nc, no_add5
  add hl, bc
no_add5:
  sla c
  rl b
  dec d
  jp nz, loop6
  ld bc, 65026
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
  ld b, 0
  ld a, b
  ld hl, 49172
  ld [hl], a
  ld b, 0
  ld a, b
  ld hl, 49173
  ld [hl], a
  ld b, 1
  ld a, b
  ld hl, 49174
  ld [hl], a
  ld b, 1
  ld a, b
  ld hl, 49175
  ld [hl], a
  ld b, 0
  ld a, b
  ld hl, 49176
  ld [hl], a
  ld b, 0
  ld a, b
  ld hl, 49177
  ld [hl], a
  ld b, 0
  ld a, b
  ld hl, 49178
  ld [hl], a
  push bc
  push de
  push hl
  call Labelmain
  pop hl
  pop de
  pop bc
  jp PenguinDone
Labelcontrol_checkUp:
Labelcontrol_checkDown:
Labelcontrol_checkA:
Labelcontrol_checkB:
Labelcontrol_checkStart:
Labelcontrol_checkSelect:
LabelhandleBrickCollision:
  ld hl, 49176
  ld a, [hl]
  ld b, a
  ld c, 5
  ld a, b
  cp c
  ld b, 0
  jp z, EQ_TRUE_7
  jp EQ_END_7
EQ_TRUE_7:
  ld b, 1
EQ_END_7:
  ld hl, 49176
  ld a, [hl]
  ld c, a
  ld d, 6
  ld a, c
  cp d
  ld c, 0
  jp z, EQ_TRUE_8
  jp EQ_END_8
EQ_TRUE_8:
  ld c, 1
EQ_END_8:
  ld a, b   ; load left
  cp 0   ; compare left to 0
  jp nz, OR_TRUE_9   ; if nonzero, set true
  ld a, c   ; load right
  cp 0   ; compare right to 0
  jp nz, OR_TRUE_9   ; if nonzero, set true
  ld b, 0   ; set false
  jp OR_END_9
OR_TRUE_9:
  ld b, 1   ; set true
OR_END_9:
  ld a, b
  cp 0
  jp nz, L3
  jp L4
L3:
  ld b, 8
  ld hl, 49172
  ld a, [hl]
  ld c, a
  ld hl, 49173
  ld a, [hl]
  ld d, a
  push bc
  push de
  push hl
  ld a, b
  ld l, c
  ld e, 32
  ld c, d
  ld b, 0
  ld d, 8
  ld h, 0
loop11:
  srl e
  jp nc, no_add10
  add hl, bc
no_add10:
  sla c
  rl b
  dec d
  jp nz, loop11
  ld bc, $9800
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
  ld hl, 49175
  ld a, [hl]
  ld b, a
  ld a, b
  cpl
  ld b, a
  ld c, 1
  ld a, b   ; load left into A
  or c
  ld b, a   ; store
  ld a, b
  ld hl, 49175
  ld [hl], a
  ld hl, 49176
  ld a, [hl]
  ld b, a
  ld c, 5
  ld a, b
  cp c
  ld b, 0
  jp z, EQ_TRUE_12
  jp EQ_END_12
EQ_TRUE_12:
  ld b, 1
EQ_END_12:
  ld a, b
  cp 0
  jp nz, L5
  jp L7
  jp L7
L5:
  ld b, 8
  ld hl, 49172
  ld a, [hl]
  ld c, a
  ld d, 1
  ld a, c
  add a, d
  ld c, a
  ld hl, 49173
  ld a, [hl]
  ld d, a
  push bc
  push de
  push hl
  ld a, b
  ld l, c
  ld e, 32
  ld c, d
  ld b, 0
  ld d, 8
  ld h, 0
loop14:
  srl e
  jp nc, no_add13
  add hl, bc
no_add13:
  sla c
  rl b
  dec d
  jp nz, loop14
  ld bc, $9800
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
  jp L6
L7:
  ld b, 8
  ld hl, 49172
  ld a, [hl]
  ld c, a
  ld d, 1
  ld a, c
  sub a, d
  ld c, a
  ld hl, 49173
  ld a, [hl]
  ld d, a
  push bc
  push de
  push hl
  ld a, b
  ld l, c
  ld e, 32
  ld c, d
  ld b, 0
  ld d, 8
  ld h, 0
loop16:
  srl e
  jp nc, no_add15
  add hl, bc
no_add15:
  sla c
  rl b
  dec d
  jp nz, loop16
  ld bc, $9800
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
L6:
L4:
  ret
Labelmain:
  ld b, 0
  push bc
  push de
  push hl
  call Labelcontrol_LCDon
  pop hl
  pop de
  pop bc
  push bc
  push de
  push hl
  call Labelcontrol_initDisplayRegs
  pop hl
  pop de
  pop bc
  push bc
  push de
  push hl
  call Labelcontrol_initPalette
  pop hl
  pop de
  pop bc
L8:
  ld c, 1
  ld a, c
  cp 0
  jp nz, L9
  jp L10
L9:
  push bc
  push de
  push hl
  call Labelcontrol_waitVBlankOver
  pop hl
  pop de
  pop bc
  push bc
  push de
  push hl
  call Labelcontrol_waitVBlankStart
  pop hl
  pop de
  pop bc
  ld c, 0
  ld a, b
  cp c
  ld c, 0
  jp z, EQ_TRUE_17
  jp EQ_END_17
EQ_TRUE_17:
  ld c, 1
EQ_END_17:
  ld a, c
  cp 0
  jp nz, L11
  jp L13
  jp L13
L11:
  push bc
  push de
  push hl
  call Labelcontrol_updateInput
  pop hl
  pop de
  pop bc
  push bc
  push de
  push hl
  call Labelcontrol_checkLeft
  pop hl
  pop de
  pop bc
  ld c, a
  ld a, c
  ld hl, 49177
  ld [hl], a
  push bc
  push de
  push hl
  call Labelcontrol_checkRight
  pop hl
  pop de
  pop bc
  ld c, a
  ld a, c
  ld hl, 49178
  ld [hl], a
  ld hl, 49169
  ld a, [hl]
  ld c, a
  ld hl, 49174
  ld a, [hl]
  ld d, a
  ld e, 2
  push bc
  push de
  push hl
  ld b, d
  ld c, e
  call PenguinMult
  pop hl
  pop de
  pop bc
  ld d, a
  ld a, c
  add a, d
  ld c, a
  ld a, c
  ld hl, 49169
  ld [hl], a
  ld hl, 49170
  ld a, [hl]
  ld c, a
  ld hl, 49175
  ld a, [hl]
  ld d, a
  ld e, 2
  push bc
  push de
  push hl
  ld b, d
  ld c, e
  call PenguinMult
  pop hl
  pop de
  pop bc
  ld d, a
  ld a, c
  add a, d
  ld c, a
  ld a, c
  ld hl, 49170
  ld [hl], a
  ld hl, 49169
  ld a, [hl]
  ld c, a
  ld d, 9
  ld a, c
  sub a, d
  ld c, a
  ld d, 3
  ld a, c
  push bc
  ld b, d
SHR_LOOP_18:
  srl a
  dec b
  jp nz, SHR_LOOP_18
  pop bc
  ld c, a
  ld a, c
  ld hl, 49172
  ld [hl], a
  ld hl, 49170
  ld a, [hl]
  ld c, a
  ld d, 16
  ld a, c
  sub a, d
  ld c, a
  ld d, 3
  ld a, c
  push bc
  ld b, d
SHR_LOOP_19:
  srl a
  dec b
  jp nz, SHR_LOOP_19
  pop bc
  ld c, a
  ld a, c
  ld hl, 49173
  ld [hl], a
  ld hl, 49172
  ld a, [hl]
  ld c, a
  ld hl, 49173
  ld a, [hl]
  ld d, a
  push hl
  push de
  push bc
  ld l, c
  ld e, 32
  ld c, d
  ld b, 0
  ld d, 8
  ld h, 0
loop21:
  srl e
  jp nc, no_add20
  add hl, bc
no_add20:
  sla c
  rl b
  dec d
  jp nz, loop21
  ld bc, $9800
  add hl, bc
  pop bc
  pop de
  ld c, [hl]
  pop hl
  ld a, c
  ld hl, 49176
  ld [hl], a
  push bc
  push de
  push hl
  call LabelhandleBrickCollision
  pop hl
  pop de
  pop bc
  ld hl, 49176
  ld a, [hl]
  ld c, a
  ld d, 4
  ld a, c
  cp d
  ld c, 0
  jp z, EQ_TRUE_22
  jp EQ_END_22
EQ_TRUE_22:
  ld c, 1
EQ_END_22:
  ld hl, 49176
  ld a, [hl]
  ld d, a
  ld e, 7
  ld a, d
  cp e
  ld d, 0
  jp z, EQ_TRUE_23
  jp EQ_END_23
EQ_TRUE_23:
  ld d, 1
EQ_END_23:
  ld a, c   ; load left
  cp 0   ; compare left to 0
  jp nz, OR_TRUE_24   ; if nonzero, set true
  ld a, d   ; load right
  cp 0   ; compare right to 0
  jp nz, OR_TRUE_24   ; if nonzero, set true
  ld c, 0   ; set false
  jp OR_END_24
OR_TRUE_24:
  ld c, 1   ; set true
OR_END_24:
  ld hl, 49176
  ld a, [hl]
  ld d, a
  ld e, 2
  ld a, d
  cp e
  ld d, 0
  jp z, EQ_TRUE_25
  jp EQ_END_25
EQ_TRUE_25:
  ld d, 1
EQ_END_25:
  ld a, c   ; load left
  cp 0   ; compare left to 0
  jp nz, OR_TRUE_26   ; if nonzero, set true
  ld a, d   ; load right
  cp 0   ; compare right to 0
  jp nz, OR_TRUE_26   ; if nonzero, set true
  ld c, 0   ; set false
  jp OR_END_26
OR_TRUE_26:
  ld c, 1   ; set true
OR_END_26:
  ld hl, 49176
  ld a, [hl]
  ld d, a
  ld e, 10
  ld a, d
  cp e
  ld d, 0
  jp z, EQ_TRUE_27
  jp EQ_END_27
EQ_TRUE_27:
  ld d, 1
EQ_END_27:
  ld a, c   ; load left
  cp 0   ; compare left to 0
  jp nz, OR_TRUE_28   ; if nonzero, set true
  ld a, d   ; load right
  cp 0   ; compare right to 0
  jp nz, OR_TRUE_28   ; if nonzero, set true
  ld c, 0   ; set false
  jp OR_END_28
OR_TRUE_28:
  ld c, 1   ; set true
OR_END_28:
  ld a, c
  cp 0
  jp nz, L14
  jp L15
L14:
  ld hl, 49174
  ld a, [hl]
  ld c, a
  ld a, c
  cpl
  ld c, a
  ld d, 1
  ld a, c   ; load left into A
  or d
  ld c, a   ; store
  ld a, c
  ld hl, 49174
  ld [hl], a
L15:
  ld hl, 49176
  ld a, [hl]
  ld c, a
  ld d, 1
  ld a, c
  cp d
  ld c, 0
  jp z, EQ_TRUE_29
  jp EQ_END_29
EQ_TRUE_29:
  ld c, 1
EQ_END_29:
  ld hl, 49176
  ld a, [hl]
  ld d, a
  ld e, 9
  ld a, d
  cp e
  ld d, 0
  jp z, EQ_TRUE_30
  jp EQ_END_30
EQ_TRUE_30:
  ld d, 1
EQ_END_30:
  ld a, c   ; load left
  cp 0   ; compare left to 0
  jp nz, OR_TRUE_31   ; if nonzero, set true
  ld a, d   ; load right
  cp 0   ; compare right to 0
  jp nz, OR_TRUE_31   ; if nonzero, set true
  ld c, 0   ; set false
  jp OR_END_31
OR_TRUE_31:
  ld c, 1   ; set true
OR_END_31:
  ld a, c
  cp 0
  jp nz, L16
  jp L17
L16:
  ld hl, 49175
  ld a, [hl]
  ld c, a
  ld a, c
  cpl
  ld c, a
  ld d, 1
  ld a, c   ; load left into A
  or d
  ld c, a   ; store
  ld a, c
  ld hl, 49175
  ld [hl], a
L17:
  ld hl, 49169
  ld a, [hl]
  ld c, a
  ld hl, 49168
  ld a, [hl]
  ld d, a
  ld e, 8
  ld a, d
  add a, e
  ld d, a
  ld a, c
  cp d
  ld c, 0
  jp c, LE_TRUE_32
  jp z, LE_TRUE_32
  jp LE_END_32
LE_TRUE_32:
  ld c, 1
LE_END_32:
  ld a, c
  cp 0
  jp nz, L18
  jp L19
L18:
  ld hl, 49169
  ld a, [hl]
  ld c, a
  ld hl, 49168
  ld a, [hl]
  ld d, a
  ld e, 8
  ld a, d
  sub a, e
  ld d, a
  ld a, c
  cp d
  ld c, 0
  jp z, GE_TRUE_33
  jp nc, GE_TRUE_33
  jp GE_END_33
GE_TRUE_33:
  ld c, 1
GE_END_33:
  ld a, c
  cp 0
  jp nz, L20
  jp L21
L20:
  ld hl, 49170
  ld a, [hl]
  ld c, a
  ld d, 5
  ld a, c
  add a, d
  ld c, a
  ld d, 145
  ld a, c
  cp d
  ld c, 0
  jp z, GE_TRUE_34
  jp nc, GE_TRUE_34
  jp GE_END_34
GE_TRUE_34:
  ld c, 1
GE_END_34:
  ld a, c
  cp 0
  jp nz, L22
  jp L23
L22:
  ld hl, 49170
  ld a, [hl]
  ld c, a
  ld d, 3
  ld a, c
  add a, d
  ld c, a
  ld d, 145
  ld a, c
  cp d
  ld c, 0
  jp c, LE_TRUE_35
  jp z, LE_TRUE_35
  jp LE_END_35
LE_TRUE_35:
  ld c, 1
LE_END_35:
  ld a, c
  cp 0
  jp nz, L24
  jp L25
L24:
  ld hl, 49175
  ld a, [hl]
  ld c, a
  ld d, 1
  ld a, c
  cp d
  ld c, 0
  jp z, EQ_TRUE_36
  jp EQ_END_36
EQ_TRUE_36:
  ld c, 1
EQ_END_36:
  ld a, c
  cp 0
  jp nz, L26
  jp L27
L26:
  ld c, 255
  ld a, c
  ld hl, 49175
  ld [hl], a
L27:
L25:
L23:
  ld hl, 49170
  ld a, [hl]
  ld c, a
  ld d, 145
  ld a, c
  cp d
  ld c, 0
  jp z, GE_TRUE_37
  jp nc, GE_TRUE_37
  jp GE_END_37
GE_TRUE_37:
  ld c, 1
GE_END_37:
  ld a, c
  cp 0
  jp nz, L28
  jp L29
L28:
  ld hl, 49170
  ld a, [hl]
  ld c, a
  ld d, 3
  ld a, c
  sub a, d
  ld c, a
  ld d, 145
  ld a, c
  cp d
  ld c, 0
  jp c, LE_TRUE_38
  jp z, LE_TRUE_38
  jp LE_END_38
LE_TRUE_38:
  ld c, 1
LE_END_38:
  ld a, c
  cp 0
  jp nz, L30
  jp L31
L30:
  ld hl, 49175
  ld a, [hl]
  ld c, a
  ld d, 255
  ld a, c
  cp d
  ld c, 0
  jp z, EQ_TRUE_39
  jp EQ_END_39
EQ_TRUE_39:
  ld c, 1
EQ_END_39:
  ld a, c
  cp 0
  jp nz, L32
  jp L33
L32:
  ld c, 1
  ld a, c
  ld hl, 49175
  ld [hl], a
L33:
L31:
L29:
L21:
L19:
  ld c, 1
  ld b, c
  jp L12
L13:
  ld c, 1
  ld a, b
  cp c
  ld c, 0
  jp z, EQ_TRUE_40
  jp EQ_END_40
EQ_TRUE_40:
  ld c, 1
EQ_END_40:
  ld a, c
  cp 0
  jp nz, L34
  jp L35
L34:
  ld hl, 49177
  ld a, [hl]
  ld c, a
  ld a, c
  cp 0
  jp nz, L36
  jp L37
L36:
  ld hl, 49168
  ld a, [hl]
  ld c, a
  ld d, 16
  ld a, c
  cp d
  ld c, 0
  jp c, GT_END_41
  jp z, GT_END_41
GT_TRUE_41:
  ld c, 1
GT_END_41:
  ld a, c
  cp 0
  jp nz, L38
  jp L39
L38:
  ld hl, 49168
  ld a, [hl]
  ld c, a
  ld d, 2
  ld a, c
  sub a, d
  ld c, a
  ld a, c
  ld hl, 49168
  ld [hl], a
L39:
L37:
  ld hl, 49178
  ld a, [hl]
  ld c, a
  ld a, c
  cp 0
  jp nz, L40
  jp L41
L40:
  ld hl, 49168
  ld a, [hl]
  ld c, a
  ld d, 104
  ld a, c
  cp d
  ld c, 0
  jp c, LT_TRUE_42
  jp LT_END_42
LT_TRUE_42:
  ld c, 1
LT_END_42:
  ld a, c
  cp 0
  jp nz, L42
  jp L43
L42:
  ld hl, 49168
  ld a, [hl]
  ld c, a
  ld d, 2
  ld a, c
  add a, d
  ld c, a
  ld a, c
  ld hl, 49168
  ld [hl], a
L43:
L41:
  ld hl, 49169
  ld a, [hl]
  ld c, a
  ld d, 1
  push bc
  push de
  push hl
  ld a, c
  ld e, 4
  ld c, d
  ld b, 0
  ld d, 8
  ld hl, 0
loop44:
  srl e
  jp nc, no_add43
  add hl, bc
no_add43:
  sla c
  rl b
  dec d
  jp nz, loop44
  ld bc, 65025
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
  ld hl, 49170
  ld a, [hl]
  ld c, a
  ld d, 1
  push bc
  push de
  push hl
  ld a, c
  ld e, 4
  ld c, d
  ld b, 0
  ld d, 8
  ld hl, 0
loop46:
  srl e
  jp nc, no_add45
  add hl, bc
no_add45:
  sla c
  rl b
  dec d
  jp nz, loop46
  ld bc, 65024
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
  ld hl, 49168
  ld a, [hl]
  ld c, a
  ld d, 0
  push bc
  push de
  push hl
  ld a, c
  ld e, 4
  ld c, d
  ld b, 0
  ld d, 8
  ld hl, 0
loop48:
  srl e
  jp nc, no_add47
  add hl, bc
no_add47:
  sla c
  rl b
  dec d
  jp nz, loop48
  ld bc, 65025
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
  ld c, 145
  ld d, 0
  push bc
  push de
  push hl
  ld a, c
  ld e, 4
  ld c, d
  ld b, 0
  ld d, 8
  ld hl, 0
loop50:
  srl e
  jp nc, no_add49
  add hl, bc
no_add49:
  sla c
  rl b
  dec d
  jp nz, loop50
  ld bc, 65024
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
  ld c, 0
  ld b, c
L35:
L12:
  jp L8
L10:
  ret
PenguinDone:
  nop
  jp PenguinDone
PenguinMult:
  ld a, 0
  ld d, 8
.loop:
  srl b
  jp nc, .no_add
  add a, c
.no_add:
  sla c
  dec d
  jp nz, .loop
  ret
PenguinMemCopy:
  ld a, [de]
  ld [hli], a
  inc de
  dec bc
  ld a, b
  or a, c
  jp nz, PenguinMemCopy
  ret
Labelcontrol_LCDon:
  ld a, LCDCF_ON | LCDCF_BGON | LCDCF_OBJON
  ld [rLCDC], a
  ret
Labelcontrol_LCDoff:
  ld a, 0
  ld [rLCDC], a
  ret
Labelcontrol_waitVBlankStart:
  ld a, [rLY]
  cp 144
  jp c, Labelcontrol_waitVBlankStart
  ret
Labelcontrol_waitVBlankOver:
  ld a, [rLY]
  cp 144
  jp nc, Labelcontrol_waitVBlankOver
  ret
Labelcontrol_initPalette:
  ld a, 0b11100100
  ld [rBGP], a
  ld [$FF48], a
  ld [$FF49], a
  ret
Labelcontrol_initDisplayRegs:
  ld a, %11100100
  ld [rBGP], a
  ld a, %11100100
  ld [rOBP0], a
  ret
Labelcontrol_updateInput:
  ld a, P1F_GET_BTN
  call .onenibble
  ld b, a
  ld a, P1F_GET_DPAD
  call .onenibble
  swap a
  xor a, b
  ld b, a
  ld a, P1F_GET_NONE
  ldh [rP1], a
  ld a, [wCurKeys]
  xor a, b
  and a, b
  ld [wNewKeys], a
  ld a, b
  ld [wCurKeys], a
  ret
  .onenibble
  ldh [rP1], a
  call .knownret
  ldh a, [rP1]
  ldh a, [rP1]
  ldh a, [rP1]
  or a, $F0
  .knownret
  ret
Labelcontrol_checkLeft:
  ld a, [wCurKeys]
  and a, PADF_LEFT
  ret
Labelcontrol_checkRight:
  ld a, [wCurKeys]
  and a, PADF_RIGHT
  ret
Labeltileset_block_0Start:
  INCBIN "penguinoid_tileset.2bpp"
Labeltileset_block_0End:
Labeltileset_block_2Start:
  INCBIN "penguinoid_tileset.2bpp"
Labeltileset_block_2End:
Labeltilemap0Start:
  INCBIN "penguinoid_tilemap.bin"
Labeltilemap0End:
  SECTION "Input Variables", WRAM0
  wCurKeys: db
  wNewKeys: db