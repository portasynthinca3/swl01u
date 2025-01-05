start:
    # copy task struct into ram
    ldr r0, new_task_struct
    ldr r1, fw_task_list
    mov r2, #36
    ldr r3, memcpy
    mov lr, pc
    bx r3

    # copy task func list into ram
    ldr r0, new_task_func_list
    ldr r1, fw_func_list
    mov r2, #256
    ldr r3, memcpy
    mov lr, pc
    bx r3

    # fix pointer to task func list in new task struct
    ldr r0, new_task_struct
    ldr r1, new_task_func_list
    str r1, [r0, #0x14]

    # tell the rom to use the new task struct
    ldr r1, task_def_struct
    str r0, [r1]

    # override task func pointers
    ldr r0, new_task_func_list
    ldr r1, idle_func
    # disable lcd updates
    str r1, [r0, #(12*4)]
    # set our cli handler
    adr r1, cli_handler
    str r1, [r0, #(3*4)]

    # clear display
    ldr r4, lcd_write
    mov r0, #1
    # mov lr, pc
    # bx r4
    bl delay
    bl thumb_wrap

    # display CG RAM chars
    mov r0, #0x80
    # mov lr, pc
    # bx r4
    bl delay
    bl thumb_wrap
    ldr r0, data_flag
    cgram_print_loop:
        push {r0}
        # mov lr, pc
        bl thumb_wrap
        pop {r0}
        bl delay
        add r0, r0, #1
        tst r0, #8
        beq cgram_print_loop

    # reset CG RAM addr
    mov r0, #0x40
    # mov lr, pc
    # bx r4
    bl delay
    bl thumb_wrap

    # continue normal operation
    ldr r0, return
    bx r0

cli_handler:
    push {lr}
    push {r4, r5, r6}

    ldr r6, data_flag
    consume_loop:
        ldr r0, shell_input_buf_r
        ldr r1, shell_input_buf_w
        ldrh r2, [r0]
        ldrh r1, [r1]
        cmp r2, r1
        beq consume_loop_exit

        ldr r3, shell_input_buf
        add r3, r3, r2
        ldrb r3, [r3]

        ldr r1, input_q
        lsl r1, r1, #8
        orr r1, r1, r3
        ldr r4, input_q_len
        add r4, r4, #8

        write_display_loop:
            cmp r4, #5
            bcc no_write_display
            sub r4, r4, #5
            lsr r5, r1, r4
            and r5, r5, #0x1f
            orr r5, r5, r6

            push {r0-r4}
            mov r0, r5
            ldr r4, lcd_write
            # mov lr, pc
            # bx r4
            bl thumb_wrap
            pop {r0-r4}
            # bl short_delay
            b write_display_loop
        no_write_display:

        str r4, input_q_len
        str r1, input_q

        add r2, r2, #1
        and r2, r2, #0xff
        ldr r0, shell_input_buf_r
        strh r2, [r0]

        b consume_loop
    consume_loop_exit:

    mov r0, #0x91
    bx r0

    pop {r4, r5, r6}
    pop {r3}
    bx r3

thumb_wrap:
    push {lr}
    mov lr, pc
    bx r4
    .thumb
    pop {r0}
    bx r0
    .code 32

delay:
    push {r0}
    ldr r0, delay_amt
    del_loop:
        sub r0, r0, #1
        cmp r0, #0
        bne del_loop
    pop {r0}
    bx lr

# short_delay:
#     ldr r0, short_delay_amt
#     s_del_loop:
#         sub r0, r0, #1
#         cmp r0, #0
#         bne s_del_loop
#     bx lr

delay_amt: .word 0x200
# short_delay_amt: .word 0x10
return: .word 0x0202207d
memcpy: .word 0x020b9209
# lcd_write: .word 0x02020ac9
lcd_write: .word 0x02086bb5
fw_task_list: .word 0x020bd9d4
fw_func_list: .word 0x020bdaf8
idle_func: .word 0x020203d9
task_def_struct: .word 0x0100fdf0
shell_input_buf_r: .word 0x060075e0
shell_input_buf_w: .word 0x060075e2
shell_input_buf: .word 0x060075e4
input_q: .word 0
input_q_len: .word 0
data_flag: .word 0x4000
new_task_struct: .word 0x06002d00
new_task_func_list: .word 0x06002e00
