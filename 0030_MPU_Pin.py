from Pico_Wear import PicoWear
from machine import Timer

pico = PicoWear()

# 球的初始位置和大小
ball_x = 64
ball_y = 64
ball_radius = 5

# 更新MPU数据的定时器
def update_mpu(timer):
    pico.mpu.update_mahony()

# 绘制屏幕的定时器
def update_display(timer):
    global ball_x, ball_y
    
    # 获取Roll和Pitch角度
    roll, pitch, _ = pico.mpu.get_angles()
    
    # 将角度映射到屏幕坐标
    ball_x = int(64 + (roll / 60) * 64)
    ball_y = int(64 + (pitch / 60) * 64)
    
    # 限制球的位置在屏幕范围内
    ball_x = max(ball_radius, min(127 - ball_radius, ball_x))
    ball_y = max(ball_radius, min(127 - ball_radius, ball_y))
    
    # 清空屏幕
    pico.display.fill(0)
    
    # 绘制中心线
    pico.display.line(64, 64, ball_x, ball_y, 1)
    
    # 绘制小球
    pico.display.fill_circle(ball_x, ball_y, ball_radius, 1)
    
    # 更新显示
    pico.display.show()

# 设置定时器
Timer(period=10, mode=Timer.PERIODIC, callback=update_mpu)
Timer(period=50, mode=Timer.PERIODIC, callback=update_display)

# 主循环
try:
    while True:
        pass
except KeyboardInterrupt:
    print("程序已停止")
finally:
    # 清理定时器
    for timer in Timer.timers():
        timer.deinit()