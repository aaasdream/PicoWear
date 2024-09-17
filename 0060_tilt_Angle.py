from Pico_Wear import PicoWear
import math
import utime

# 初始化 PicoWear
pico = PicoWear()

# 圆心和半径
CENTER_X, CENTER_Y = 64, 64
RADIUS = 60

def draw_background():
    # 绘制圆形
    pico.display.draw_circle(CENTER_X, CENTER_Y, RADIUS, 1)
    
    # 绘制刻度线和角度标注
    for angle in range(0, 361, 10):
        radian = math.radians(angle - 90)  # 修正：将0度调整到右侧
        x1 = int(CENTER_X + RADIUS * math.cos(radian))
        y1 = int(CENTER_Y + RADIUS * math.sin(radian))
        x2 = int(CENTER_X + (RADIUS - 5) * math.cos(radian))
        y2 = int(CENTER_Y + (RADIUS - 5) * math.sin(radian))
        pico.display.line(x1, y1, x2, y2, 1)
        
        if angle % 30 == 0:
            label = str(min(angle, 360 - angle))
            x = int(CENTER_X + (RADIUS - 15) * math.cos(radian)) - 4
            y = int(CENTER_Y + (RADIUS - 15) * math.sin(radian)) - 4
            pico.display.text(label, x, y, 1)

def draw_angle_line(angle):
    radian = math.radians(angle)  # 修正：直接使用负角度
    x = int(CENTER_X + RADIUS * math.cos(radian))
    y = int(CENTER_Y + RADIUS * math.sin(radian))
    pico.display.line(CENTER_X, CENTER_Y, x, y, 1)

def on_button_click():
    print("执行 tilt 校准")
    pico.mpu.calibrate_tilt()

# 注册按钮回调函数
pico.register_button_callback(on_button_click)

# 确保 MPU 初始化完成
utime.sleep_ms(100)

# 主循环
while True:
    try:
        # 更新 MPU 数据
        pico.mpu.calculate_tilt_angle()
        
        # 清除显示
        pico.display.fill(0)
        
        # 绘制背景
        draw_background()
        
        # 获取当前 tilt 角度
        angle = pico.mpu.Get_tilt_angle()
        
        # 绘制角度线
        draw_angle_line(angle)
        
        # 显示角度值
        angle_text = f"{abs(angle):.1f}"
        pico.display.text(angle_text, 40, 64, 1)
        
        # 更新显示
        pico.display.show()
        
        # 短暂延时
        utime.sleep_ms(10)
        
    except KeyboardInterrupt:
        print("程序终止")
        break

# 清理资源
for timer in pico.timers:
    timer.deinit()