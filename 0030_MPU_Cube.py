from Pico_Wear import PicoWear
from machine import Timer

# 创建PicoWear对象
pico = PicoWear()

# 定义方块的初始位置和大小
block_x = 64
block_y = 64
block_size = 10

# 定义更新MPU数据的函数
def update_mpu(timer):
    pico.mpu.update_mahony()

# 定义更新显示的函数
def update_display(timer):
    global block_x, block_y
    
    # 获取Roll和Pitch角度
    roll, pitch, _ = pico.mpu.get_angles()
    
    # 将角度映射到屏幕坐标
    block_x = int(64 + (roll / 15) * 64)
    block_y = int(64 + (pitch / 15) * 64)
    
    # 确保方块不会超出屏幕范围
    block_x = max(0, min(block_x, 127 - block_size))
    block_y = max(0, min(block_y, 127 - block_size))
    
    # 清除屏幕
    pico.display.fill(0)
    
    # 绘制方块
    pico.display.fill_rectangle(block_x, block_y, block_size, block_size, 1)
    
    # 更新显示
    pico.display.show()

# 设置定时器
mpu_timer = Timer(period=10, mode=Timer.PERIODIC, callback=update_mpu)
display_timer = Timer(period=50, mode=Timer.PERIODIC, callback=update_display)

# 主循环
try:
    while True:
        pass
except KeyboardInterrupt:
    # 停止定时器
    mpu_timer.deinit()
    display_timer.deinit()
    print("程序已停止")