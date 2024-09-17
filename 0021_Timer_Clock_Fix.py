from Pico_Wear import PicoWear
import math
import time

pico = PicoWear()
display = pico.display
rtc = pico.rtc

def draw_clock():
    # 清空显示
    display.fill(0)
    
    # 绘制时钟外圈
    display.draw_circle(64, 64, 62, 1)
    
     # 绘制刻度和数字
    for i in range(12):
        angle = (i - 3) * math.pi / 6  # 修改这里
        outer_x = int(64 + 58 * math.cos(angle))
        outer_y = int(64 + 58 * math.sin(angle))
        inner_x = int(64 + 52 * math.cos(angle))
        inner_y = int(64 + 52 * math.sin(angle))
        display.line(outer_x, outer_y, inner_x, inner_y, 1)
        
        # 绘制数字
        num_x = int(64 + 45 * math.cos(angle))
        num_y = int(64 + 45 * math.sin(angle))
        number = i if i != 0 else 12  # 修改这里
        display.text(str(number), num_x - 4, num_y - 4, 1)
    
    # 获取当前时间
    now = rtc.datetime()
    hours, minutes, seconds = now[4], now[5], now[6]
    
    # 计算指针角度
    hour_angle = (hours % 12 + minutes / 60) * math.pi / 6 - math.pi / 2
    minute_angle = minutes * math.pi / 30 - math.pi / 2
    second_angle = seconds * math.pi / 30 - math.pi / 2
    
    # 绘制时针
    hour_x = int(64 + 30 * math.cos(hour_angle))
    hour_y = int(64 + 30 * math.sin(hour_angle))
    display.line(64, 64, hour_x, hour_y, 1)
    display.line(64, 65, hour_x, hour_y + 1, 1)  # 加粗时针
    
    # 绘制分针
    minute_x = int(64 + 40 * math.cos(minute_angle))
    minute_y = int(64 + 40 * math.sin(minute_angle))
    display.line(64, 64, minute_x, minute_y, 1)
    
    # 绘制秒针
    second_x = int(64 + 50 * math.cos(second_angle))
    second_y = int(64 + 50 * math.sin(second_angle))
    display.line(64, 64, second_x, second_y, 1)
    
    # 更新显示
    display.show()

# 设置定时器每秒更新一次
timer = machine.Timer()
timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=lambda t:draw_clock())

# 主循环
while True:
    time.sleep(1)