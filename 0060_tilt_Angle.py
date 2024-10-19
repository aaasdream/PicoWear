from Pico_Wear import PicoWear
import math
import utime

# 初始化 PicoWear
pico_wear = PicoWear()
display = pico_wear.display
mpu = pico_wear.mpu

# 常量定义
CENTER_X, CENTER_Y = 64, 64
RADIUS = 60

def draw_background():
    # 绘制圆形
    display.draw_circle(CENTER_X, CENTER_Y, RADIUS, 1)
    
    # 绘制刻度线和角度
    for angle in range(0, 360, 15):
        radian = math.radians(angle)
        start_x = int(CENTER_X + (RADIUS - 5) * math.sin(radian))
        start_y = int(CENTER_Y - (RADIUS - 5) * math.cos(radian))
        end_x = int(CENTER_X + RADIUS * math.sin(radian))
        end_y = int(CENTER_Y - RADIUS * math.cos(radian))
        display.line(start_x, start_y, end_x, end_y, 1)
        
        if angle % 30 == 0:
            label_x = int(CENTER_X + (RADIUS - 15) * math.sin(radian))
            label_y = int(CENTER_Y - (RADIUS - 15) * math.cos(radian))
            if 0 <= angle <= 180:
                display.text(str(angle), label_x - 8, label_y - 4, 1)
            else:
                display.text(str(angle - 360), label_x - 12, label_y - 4, 1)

def draw_angle_line(angle):
    radian = math.radians(angle)
    end_x = int(CENTER_X + RADIUS * math.sin(radian))
    end_y = int(CENTER_Y - RADIUS * math.cos(radian))
    display.line(CENTER_X, CENTER_Y, end_x, end_y, 1)

def update_display(angle):
    display.fill(0)
    draw_background()
    draw_angle_line(angle)
    angle_text = f"{angle:.1f}"
    display.text(angle_text, CENTER_X - len(angle_text) * 4, CENTER_Y - 4, 1)
    display.show()

def on_button_press():
    print("开始校准倾斜角度")
    mpu.calibrate_tilt()
    print("校准完成")

# 注册按钮回调
pico_wear.register_button_callback(on_button_press)

# 主循环
try:
    while True:
        mpu.calculate_tilt_angle()
        angle = mpu.Get_tilt_angle()
        update_display(angle)
        utime.sleep(0.05)
except KeyboardInterrupt:
    print("程序已停止")