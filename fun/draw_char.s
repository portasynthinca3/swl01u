push {r4, r5, r6}
ldr r4, lcd_write

mov r0, #0x40
mov lr, pc
bx r4

mov r5, #0
ldr r6, data_flag
loop:
    ldr r0, delay_amt
    del_loop:
        sub r0, r0, #1
        cmp r0, #0
        bne del_loop

    adr r0, data
    add r0, r0, r5
    ldrb r0, [r0]
    orr r0, r0, r6

    mov lr, pc
    bx r4
    
    add r5, r5, #1
    cmp r5, #63
    ble loop

pop {r4, r5, r6}
ldr r0, return
bx r0

return: .word 0x0202207d
lcd_write: .word 0x02020ac9
data_flag: .word 0x4000
delay_amt: .word 0x2ff
data: #64 bytes
