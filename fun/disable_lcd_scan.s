adr r0, end+128
ldr r1, fw_task_list
mov r2, #36
ldr r3, memcpy
mov lr, pc
bx r3
adr r0, end+128+36
ldr r1, fw_func_list
mov r2, #256
ldr r3, memcpy
mov lr, pc
bx r3

adr r0, end+128
ldr r1, task_def_struct
str r0, [r1]

adr r1, end+128+36
str r1, [r0, #0x14]

adr r0, end+128+36
ldr r1, idle_func
str r1, [r0, #(12*4)]

ldr r1, lcd_write
mov r0, #1
mov lr, pc
bx r1

ldr r0, return
bx r0

return: .word 0x0202207d
memcpy: .word 0x020b9209
lcd_write: .word 0x02020ac9
fw_task_list: .word 0x020bd9d4
fw_func_list: .word 0x020bdaf8
idle_func: .word 0x020203d9
task_def_struct: .word 0x0100fdf0

end:
