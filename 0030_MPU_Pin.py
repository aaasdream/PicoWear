from Pico_Wear import PicoWear
import utime
import math

# 初始化 PicoWear
pico_wear = PicoWear()
display = pico_wear.display
mpu = pico_wear.mpu

# 屏幕中心坐标
CENTER_X = 64
CENTER_Y = 64

# 小球初始位置和半径
ball_x = CENTER_X
ball_y = CENTER_Y
BALL_RADIUS = 5

# 更新 MPU 数据的定时器回调函数
def update_mpu(timer):
    mpu.update_mahony()

# 更新显示的函数
def update_display():
    global ball_x, ball_y
    
    # 获取 Roll 和 Pitch 角度
    roll, pitch, _ = mpu.get_angles()
    
    # 将角度映射到屏幕坐标
    ball_x = int(CENTER_X + (roll / 60) * CENTER_X)
    ball_y = int(CENTER_Y + (pitch / 60) * CENTER_Y)
    
    # 确保球不会超出屏幕边界
    ball_x = max(BALL_RADIUS, min(127 - BALL_RADIUS, ball_x))
    ball_y = max(BALL_RADIUS, min(127 - BALL_RADIUS, ball_y))
    
    # 清除屏幕
    display.fill(0)
    
    # 绘制中心到球的连线
    display.line(CENTER_X, CENTER_Y, ball_x, ball_y, 1)
    
    # 绘制小球
    display.fill_circle(ball_x, ball_y, BALL_RADIUS, 1)
    
    # 更新显示
    display.show()

# 设置 MPU 更新定时器
mpu_timer = machine.Timer()
mpu_timer.init(period=10, mode=machine.Timer.PERIODIC, callback=update_mpu)

try:
    while True:
        update_display()
        utime.sleep(0.02)
except KeyboardInterrupt:
    mpu_timer.deinit()
    print("程序已停止")