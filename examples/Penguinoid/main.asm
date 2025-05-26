  INCLUDE "hardware.inc"
  SECTION "Header", ROM0[$100]
  jp PenguinEntry
  ds $150 - @, 0 ; Make room for the header
PenguinEntry:
  ld sp, $DFFF
  ld a, 0
  ld [wCurKeys], a
  ld [wNewKeys], a
  ; include binary hooked to below footer
  ; include binary hooked to below footer
  ; include binary hooked to below footer
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
  ld b, 5
  ld a, b
  ld hl, 49168
  ld [hl], a
  ld b, 6
  ld a, b
  ld hl, 49169
  ld [hl], a
  ld b, 8
  ld a, b
  ld hl, 49170
  ld [hl], a
  ld b, 7
  ld a, b
  ld hl, 49171
  ld [hl], a
  ld b, 4
  ld a, b
  ld hl, 49172
  ld [hl], a
  ld b, 9
  ld a, b
  ld hl, 49173
  ld [hl], a
  ld b, 1
  ld a, b
  ld hl, 49174
  ld [hl], a
  ld b, 0
  ld a, b
  ld hl, 49175
  ld [hl], a
  ld b, 2
  ld a, b
  ld hl, 49176
  ld [hl], a
  ld b, 16
  ld a, b
  ld hl, 49177
  ld [hl], a
  ld b, 145
  ld a, b
  ld hl, 49178
  ld [hl], a
  ld b, 25
  ld a, b
  ld hl, 49179
  ld [hl], a
  ld b, 100
  ld a, b
  ld hl, 49180
  ld [hl], a
  ld b, 0
  ld a, b
  ld hl, 49181
  ld [hl], a
L0:
  ld hl, 49181
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
  ld hl, 49181
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
  ld hl, 49181
  ld a, [hl]
  ld b, a
  ld c, 1
  ld a, b
  add a, c
  ld b, a
  ld a, b
  ld hl, 49181
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
  ld hl, 49177
  ld a, [hl]
  ld b, a
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
loop6:
  srl e
  jp nc, no_add5
  add hl, bc
no_add5:
  sla c
  rl b
  dec d
  jp nz, loop6
  ld bc, 65025
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
  ld hl, 49178
  ld a, [hl]
  ld b, a
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
loop8:
  srl e
  jp nc, no_add7
  add hl, bc
no_add7:
  sla c
  rl b
  dec d
  jp nz, loop8
  ld bc, 65024
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
loop10:
  srl e
  jp nc, no_add9
  add hl, bc
no_add9:
  sla c
  rl b
  dec d
  jp nz, loop10
  ld bc, 65026
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
  ld hl, 49179
  ld a, [hl]
  ld b, a
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
loop12:
  srl e
  jp nc, no_add11
  add hl, bc
no_add11:
  sla c
  rl b
  dec d
  jp nz, loop12
  ld bc, 65025
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
  ld hl, 49180
  ld a, [hl]
  ld b, a
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
loop14:
  srl e
  jp nc, no_add13
  add hl, bc
no_add13:
  sla c
  rl b
  dec d
  jp nz, loop14
  ld bc, 65024
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
  ld b, 0
  ld a, b
  ld hl, 49182
  ld [hl], a
  ld b, 0
  ld a, b
  ld hl, 49183
  ld [hl], a
  ld b, 1
  ld a, b
  ld hl, 49184
  ld [hl], a
  ld b, 2
  ld a, b
  ld hl, 49185
  ld [hl], a
  ld b, 0
  ld a, b
  ld hl, 49186
  ld [hl], a
  ld b, 0
  ld a, b
  ld hl, 49187
  ld [hl], a
  ld b, 0
  ld a, b
  ld hl, 49188
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
LabelhandleWallCollision:
  ld hl, 49186
  ld a, [hl]
  ld b, a
  ld hl, 49172
  ld a, [hl]
  ld c, a
  ld a, b
  cp c
  ld b, 0
  jp z, EQ_TRUE_15
  jp EQ_END_15
EQ_TRUE_15:
  ld b, 1
EQ_END_15:
  ld hl, 49186
  ld a, [hl]
  ld c, a
  ld hl, 49171
  ld a, [hl]
  ld d, a
  ld a, c
  cp d
  ld c, 0
  jp z, EQ_TRUE_16
  jp EQ_END_16
EQ_TRUE_16:
  ld c, 1
EQ_END_16:
  ld a, b   ; load left
  cp 0   ; compare left to 0
  jp nz, OR_TRUE_17   ; if nonzero, set true
  ld a, c   ; load right
  cp 0   ; compare right to 0
  jp nz, OR_TRUE_17   ; if nonzero, set true
  ld b, 0   ; set false
  jp OR_END_17
OR_TRUE_17:
  ld b, 1   ; set true
OR_END_17:
  ld hl, 49186
  ld a, [hl]
  ld c, a
  ld hl, 49176
  ld a, [hl]
  ld d, a
  ld a, c
  cp d
  ld c, 0
  jp z, EQ_TRUE_18
  jp EQ_END_18
EQ_TRUE_18:
  ld c, 1
EQ_END_18:
  ld a, b   ; load left
  cp 0   ; compare left to 0
  jp nz, OR_TRUE_19   ; if nonzero, set true
  ld a, c   ; load right
  cp 0   ; compare right to 0
  jp nz, OR_TRUE_19   ; if nonzero, set true
  ld b, 0   ; set false
  jp OR_END_19
OR_TRUE_19:
  ld b, 1   ; set true
OR_END_19:
  ld hl, 49186
  ld a, [hl]
  ld c, a
  ld hl, 49175
  ld a, [hl]
  ld d, a
  ld a, c
  cp d
  ld c, 0
  jp z, EQ_TRUE_20
  jp EQ_END_20
EQ_TRUE_20:
  ld c, 1
EQ_END_20:
  ld a, b   ; load left
  cp 0   ; compare left to 0
  jp nz, OR_TRUE_21   ; if nonzero, set true
  ld a, c   ; load right
  cp 0   ; compare right to 0
  jp nz, OR_TRUE_21   ; if nonzero, set true
  ld b, 0   ; set false
  jp OR_END_21
OR_TRUE_21:
  ld b, 1   ; set true
OR_END_21:
  ld a, b
  cp 0
  jp nz, L3
  jp L4
L3:
  ld hl, 49184
  ld a, [hl]
  ld b, a
  ld c, 1
  ld a, b
  cp c
  ld b, 0
  jp z, EQ_TRUE_22
  jp EQ_END_22
EQ_TRUE_22:
  ld b, 1
EQ_END_22:
  ld a, b
  cp 0
  jp nz, L5
  jp L7
  jp L7
L5:
  ld b, 2
  ld a, b
  ld hl, 49184
  ld [hl], a
  jp L6
L7:
  ld b, 1
  ld a, b
  ld hl, 49184
  ld [hl], a
L6:
L4:
  ld hl, 49186
  ld a, [hl]
  ld b, a
  ld hl, 49174
  ld a, [hl]
  ld c, a
  ld a, b
  cp c
  ld b, 0
  jp z, EQ_TRUE_23
  jp EQ_END_23
EQ_TRUE_23:
  ld b, 1
EQ_END_23:
  ld hl, 49186
  ld a, [hl]
  ld c, a
  ld hl, 49173
  ld a, [hl]
  ld d, a
  ld a, c
  cp d
  ld c, 0
  jp z, EQ_TRUE_24
  jp EQ_END_24
EQ_TRUE_24:
  ld c, 1
EQ_END_24:
  ld a, b   ; load left
  cp 0   ; compare left to 0
  jp nz, OR_TRUE_25   ; if nonzero, set true
  ld a, c   ; load right
  cp 0   ; compare right to 0
  jp nz, OR_TRUE_25   ; if nonzero, set true
  ld b, 0   ; set false
  jp OR_END_25
OR_TRUE_25:
  ld b, 1   ; set true
OR_END_25:
  ld a, b
  cp 0
  jp nz, L8
  jp L9
L8:
  ld hl, 49185
  ld a, [hl]
  ld b, a
  ld c, 1
  ld a, b
  cp c
  ld b, 0
  jp z, EQ_TRUE_26
  jp EQ_END_26
EQ_TRUE_26:
  ld b, 1
EQ_END_26:
  ld a, b
  cp 0
  jp nz, L10
  jp L12
  jp L12
L10:
  ld b, 2
  ld a, b
  ld hl, 49185
  ld [hl], a
  jp L11
L12:
  ld b, 1
  ld a, b
  ld hl, 49185
  ld [hl], a
L11:
L9:
  ret
LabelhandleBrickCollision:
  ld hl, 49186
  ld a, [hl]
  ld b, a
  ld hl, 49168
  ld a, [hl]
  ld c, a
  ld a, b
  cp c
  ld b, 0
  jp z, EQ_TRUE_27
  jp EQ_END_27
EQ_TRUE_27:
  ld b, 1
EQ_END_27:
  ld hl, 49186
  ld a, [hl]
  ld c, a
  ld hl, 49169
  ld a, [hl]
  ld d, a
  ld a, c
  cp d
  ld c, 0
  jp z, EQ_TRUE_28
  jp EQ_END_28
EQ_TRUE_28:
  ld c, 1
EQ_END_28:
  ld a, b   ; load left
  cp 0   ; compare left to 0
  jp nz, OR_TRUE_29   ; if nonzero, set true
  ld a, c   ; load right
  cp 0   ; compare right to 0
  jp nz, OR_TRUE_29   ; if nonzero, set true
  ld b, 0   ; set false
  jp OR_END_29
OR_TRUE_29:
  ld b, 1   ; set true
OR_END_29:
  ld a, b
  cp 0
  jp nz, L13
  jp L14
L13:
  ld hl, 49170
  ld a, [hl]
  ld b, a
  ld hl, 49182
  ld a, [hl]
  ld c, a
  ld hl, 49183
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
loop31:
  srl e
  jp nc, no_add30
  add hl, bc
no_add30:
  sla c
  rl b
  dec d
  jp nz, loop31
  ld bc, $9800
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
  ld hl, 49185
  ld a, [hl]
  ld b, a
  ld c, 1
  ld a, b
  cp c
  ld b, 0
  jp z, EQ_TRUE_32
  jp EQ_END_32
EQ_TRUE_32:
  ld b, 1
EQ_END_32:
  ld a, b
  cp 0
  jp nz, L15
  jp L17
  jp L17
L15:
  ld b, 2
  ld a, b
  ld hl, 49185
  ld [hl], a
  jp L16
L17:
  ld b, 1
  ld a, b
  ld hl, 49185
  ld [hl], a
L16:
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
  ld hl, 49186
  ld a, [hl]
  ld b, a
  ld hl, 49168
  ld a, [hl]
  ld c, a
  ld a, b
  cp c
  ld b, 0
  jp z, EQ_TRUE_33
  jp EQ_END_33
EQ_TRUE_33:
  ld b, 1
EQ_END_33:
  ld a, b
  cp 0
  jp nz, L18
  jp L20
  jp L20
L18:
  ld hl, 49170
  ld a, [hl]
  ld b, a
  ld hl, 49182
  ld a, [hl]
  ld c, a
  ld d, 1
  ld a, c
  add a, d
  ld c, a
  ld hl, 49183
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
loop35:
  srl e
  jp nc, no_add34
  add hl, bc
no_add34:
  sla c
  rl b
  dec d
  jp nz, loop35
  ld bc, $9800
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
  jp L19
L20:
  ld hl, 49170
  ld a, [hl]
  ld b, a
  ld hl, 49182
  ld a, [hl]
  ld c, a
  ld d, 1
  ld a, c
  sub a, d
  ld c, a
  ld hl, 49183
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
loop37:
  srl e
  jp nc, no_add36
  add hl, bc
no_add36:
  sla c
  rl b
  dec d
  jp nz, loop37
  ld bc, $9800
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
L19:
L14:
  ret
LabelhandlePaddleCollision:
  ld hl, 49179
  ld a, [hl]
  ld b, a
  ld hl, 49177
  ld a, [hl]
  ld c, a
  ld d, 8
  ld a, c
  add a, d
  ld c, a
  ld a, b
  cp c
  ld b, 0
  jp c, LE_TRUE_38
  jp z, LE_TRUE_38
  jp LE_END_38
LE_TRUE_38:
  ld b, 1
LE_END_38:
  ld a, b
  cp 0
  jp nz, L21
  jp L22
L21:
  ld hl, 49179
  ld a, [hl]
  ld b, a
  ld hl, 49177
  ld a, [hl]
  ld c, a
  ld d, 8
  ld a, c
  sub a, d
  ld c, a
  ld a, b
  cp c
  ld b, 0
  jp z, GE_TRUE_39
  jp nc, GE_TRUE_39
  jp GE_END_39
GE_TRUE_39:
  ld b, 1
GE_END_39:
  ld a, b
  cp 0
  jp nz, L23
  jp L24
L23:
  ld hl, 49180
  ld a, [hl]
  ld b, a
  ld c, 5
  ld a, b
  add a, c
  ld b, a
  ld c, 145
  ld a, b
  cp c
  ld b, 0
  jp z, GE_TRUE_40
  jp nc, GE_TRUE_40
  jp GE_END_40
GE_TRUE_40:
  ld b, 1
GE_END_40:
  ld a, b
  cp 0
  jp nz, L25
  jp L26
L25:
  ld hl, 49180
  ld a, [hl]
  ld b, a
  ld c, 3
  ld a, b
  add a, c
  ld b, a
  ld c, 145
  ld a, b
  cp c
  ld b, 0
  jp c, LE_TRUE_41
  jp z, LE_TRUE_41
  jp LE_END_41
LE_TRUE_41:
  ld b, 1
LE_END_41:
  ld a, b
  cp 0
  jp nz, L27
  jp L28
L27:
  ld hl, 49185
  ld a, [hl]
  ld b, a
  ld c, 1
  ld a, b
  cp c
  ld b, 0
  jp z, EQ_TRUE_42
  jp EQ_END_42
EQ_TRUE_42:
  ld b, 1
EQ_END_42:
  ld a, b
  cp 0
  jp nz, L29
  jp L30
L29:
  ld b, 2
  ld a, b
  ld hl, 49185
  ld [hl], a
L30:
L28:
L26:
  ld hl, 49180
  ld a, [hl]
  ld b, a
  ld c, 145
  ld a, b
  cp c
  ld b, 0
  jp z, GE_TRUE_43
  jp nc, GE_TRUE_43
  jp GE_END_43
GE_TRUE_43:
  ld b, 1
GE_END_43:
  ld a, b
  cp 0
  jp nz, L31
  jp L32
L31:
  ld hl, 49180
  ld a, [hl]
  ld b, a
  ld c, 3
  ld a, b
  sub a, c
  ld b, a
  ld c, 145
  ld a, b
  cp c
  ld b, 0
  jp c, LE_TRUE_44
  jp z, LE_TRUE_44
  jp LE_END_44
LE_TRUE_44:
  ld b, 1
LE_END_44:
  ld a, b
  cp 0
  jp nz, L33
  jp L34
L33:
  ld hl, 49185
  ld a, [hl]
  ld b, a
  ld c, 2
  ld a, b
  cp c
  ld b, 0
  jp z, EQ_TRUE_45
  jp EQ_END_45
EQ_TRUE_45:
  ld b, 1
EQ_END_45:
  ld a, b
  cp 0
  jp nz, L35
  jp L36
L35:
  ld b, 1
  ld a, b
  ld hl, 49185
  ld [hl], a
L36:
L34:
L32:
L24:
L22:
  ret
LabelupdateBallPosition:
  ld hl, 49184
  ld a, [hl]
  ld b, a
  ld c, 1
  ld a, b
  cp c
  ld b, 0
  jp z, EQ_TRUE_46
  jp EQ_END_46
EQ_TRUE_46:
  ld b, 1
EQ_END_46:
  ld a, b
  cp 0
  jp nz, L37
  jp L39
  jp L39
L37:
  ld hl, 49179
  ld a, [hl]
  ld b, a
  ld c, 2
  ld a, b
  add a, c
  ld b, a
  ld a, b
  ld hl, 49179
  ld [hl], a
  jp L38
L39:
  ld hl, 49179
  ld a, [hl]
  ld b, a
  ld c, 2
  ld a, b
  sub a, c
  ld b, a
  ld a, b
  ld hl, 49179
  ld [hl], a
L38:
  ld hl, 49185
  ld a, [hl]
  ld b, a
  ld c, 1
  ld a, b
  cp c
  ld b, 0
  jp z, EQ_TRUE_47
  jp EQ_END_47
EQ_TRUE_47:
  ld b, 1
EQ_END_47:
  ld a, b
  cp 0
  jp nz, L40
  jp L42
  jp L42
L40:
  ld hl, 49180
  ld a, [hl]
  ld b, a
  ld c, 2
  ld a, b
  add a, c
  ld b, a
  ld a, b
  ld hl, 49180
  ld [hl], a
  jp L41
L42:
  ld hl, 49180
  ld a, [hl]
  ld b, a
  ld c, 2
  ld a, b
  sub a, c
  ld b, a
  ld a, b
  ld hl, 49180
  ld [hl], a
L41:
  ret
LabelsetBallAndPaddlePosition:
  ld hl, 49187
  ld a, [hl]
  ld b, a
  ld a, b
  cp 0
  jp nz, L43
  jp L44
L43:
  ld hl, 49177
  ld a, [hl]
  ld b, a
  ld c, 16
  ld a, b
  cp c
  ld b, 0
  jp c, GT_END_48
  jp z, GT_END_48
GT_TRUE_48:
  ld b, 1
GT_END_48:
  ld a, b
  cp 0
  jp nz, L45
  jp L46
L45:
  ld hl, 49177
  ld a, [hl]
  ld b, a
  ld c, 2
  ld a, b
  sub a, c
  ld b, a
  ld a, b
  ld hl, 49177
  ld [hl], a
L46:
L44:
  ld hl, 49188
  ld a, [hl]
  ld b, a
  ld a, b
  cp 0
  jp nz, L47
  jp L48
L47:
  ld hl, 49177
  ld a, [hl]
  ld b, a
  ld c, 104
  ld a, b
  cp c
  ld b, 0
  jp c, LT_TRUE_49
  jp LT_END_49
LT_TRUE_49:
  ld b, 1
LT_END_49:
  ld a, b
  cp 0
  jp nz, L49
  jp L50
L49:
  ld hl, 49177
  ld a, [hl]
  ld b, a
  ld c, 2
  ld a, b
  add a, c
  ld b, a
  ld a, b
  ld hl, 49177
  ld [hl], a
L50:
L48:
  ld hl, 49179
  ld a, [hl]
  ld b, a
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
loop51:
  srl e
  jp nc, no_add50
  add hl, bc
no_add50:
  sla c
  rl b
  dec d
  jp nz, loop51
  ld bc, 65025
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
  ld hl, 49180
  ld a, [hl]
  ld b, a
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
loop53:
  srl e
  jp nc, no_add52
  add hl, bc
no_add52:
  sla c
  rl b
  dec d
  jp nz, loop53
  ld bc, 65024
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
  ld hl, 49177
  ld a, [hl]
  ld b, a
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
loop55:
  srl e
  jp nc, no_add54
  add hl, bc
no_add54:
  sla c
  rl b
  dec d
  jp nz, loop55
  ld bc, 65025
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
  ld b, 145
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
loop57:
  srl e
  jp nc, no_add56
  add hl, bc
no_add56:
  sla c
  rl b
  dec d
  jp nz, loop57
  ld bc, 65024
  add hl, bc
  ld [hl], a
  pop hl
  pop de
  pop bc
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
L51:
  ld c, 1
  ld a, c
  cp 0
  jp nz, L52
  jp L53
L52:
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
  jp z, EQ_TRUE_58
  jp EQ_END_58
EQ_TRUE_58:
  ld c, 1
EQ_END_58:
  ld a, c
  cp 0
  jp nz, L54
  jp L56
  jp L56
L54:
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
  ld hl, 49187
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
  ld hl, 49188
  ld [hl], a
  push bc
  push de
  push hl
  call LabelupdateBallPosition
  pop hl
  pop de
  pop bc
  ld hl, 49179
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
SHR_LOOP_59:
  srl a
  dec b
  jp nz, SHR_LOOP_59
  pop bc
  ld c, a
  ld a, c
  ld hl, 49182
  ld [hl], a
  ld hl, 49180
  ld a, [hl]
  ld c, a
  ld d, 18
  ld a, c
  sub a, d
  ld c, a
  ld d, 3
  ld a, c
  push bc
  ld b, d
SHR_LOOP_60:
  srl a
  dec b
  jp nz, SHR_LOOP_60
  pop bc
  ld c, a
  ld a, c
  ld hl, 49183
  ld [hl], a
  ld hl, 49182
  ld a, [hl]
  ld c, a
  ld hl, 49183
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
loop62:
  srl e
  jp nc, no_add61
  add hl, bc
no_add61:
  sla c
  rl b
  dec d
  jp nz, loop62
  ld bc, $9800
  add hl, bc
  pop bc
  pop de
  ld c, [hl]
  pop hl
  ld a, c
  ld hl, 49186
  ld [hl], a
  push bc
  push de
  push hl
  call LabelhandleBrickCollision
  pop hl
  pop de
  pop bc
  push bc
  push de
  push hl
  call LabelhandleWallCollision
  pop hl
  pop de
  pop bc
  push bc
  push de
  push hl
  call LabelhandlePaddleCollision
  pop hl
  pop de
  pop bc
  ld c, 1
  ld b, c
  jp L55
L56:
  ld c, 1
  ld a, b
  cp c
  ld c, 0
  jp z, EQ_TRUE_63
  jp EQ_END_63
EQ_TRUE_63:
  ld c, 1
EQ_END_63:
  ld a, c
  cp 0
  jp nz, L57
  jp L58
L57:
  push bc
  push de
  push hl
  call LabelsetBallAndPaddlePosition
  pop hl
  pop de
  pop bc
  ld c, 0
  ld b, c
L58:
L55:
  jp L51
L53:
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