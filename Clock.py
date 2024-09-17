import sh1107
import Pico_Wear
import math
import time
from TimeToDo import TimeToDo

display, mpu = Pico_Wear.Pico_Wear_Init()

# 定義時鐘參數
CENTER_X, CENTER_Y = 64, 64
RADIUS = 60
HOUR_HAND_LENGTH = 30
MINUTE_HAND_LENGTH = 45
SECOND_HAND_LENGTH = 55

def draw_clock_face():
    # 畫圓形外框
    display.draw_circle(CENTER_X, CENTER_Y, RADIUS, 1)
    
    # 畫刻度和數字
    for i in range(12):
        angle = i * math.pi / 6 - math.pi / 2
        outer_x = int(CENTER_X + RADIUS * math.cos(angle))
        outer_y = int(CENTER_Y + RADIUS * math.sin(angle))
        inner_x = int(CENTER_X + (RADIUS - 5) * math.cos(angle))
        inner_y = int(CENTER_Y + (RADIUS - 5) * math.sin(angle))
        display.line(outer_x, outer_y, inner_x, inner_y, 1)
        
        # 添加數字，修正位置計算
        num_x = int(CENTER_X + (RADIUS - 15) * math.cos(angle))
        num_y = int(CENTER_Y + (RADIUS - 15) * math.sin(angle))
        num = i if i != 0 else 12  # 將0改為12
        display.text(str(num), num_x - 4, num_y - 4, 1)

def draw_hand(length, angle, width):
    x = int(CENTER_X + length * math.cos(angle))
    y = int(CENTER_Y + length * math.sin(angle))
    if width == 1:
        display.line(CENTER_X, CENTER_Y, x, y, 1)
    else:
        for i in range(-width//2, width//2 + 1):
            display.line(CENTER_X + i, CENTER_Y, x + i, y, 1)

def update_clock():
    # 獲取當前時間
    current_time = time.localtime()
    hours, minutes, seconds = current_time[3], current_time[4], current_time[5]
    
    # 計算指針角度
    second_angle = seconds * math.pi / 30 - math.pi / 2
    minute_angle = (minutes + seconds / 60) * math.pi / 30 - math.pi / 2
    hour_angle = (hours % 12 + minutes / 60) * math.pi / 6 - math.pi / 2
    
    # 清除顯示
    display.fill(0)
    
    # 繪製時鐘面
    draw_clock_face()
    
    # 繪製指針
    draw_hand(HOUR_HAND_LENGTH, hour_angle, 3)  # 時針
    draw_hand(MINUTE_HAND_LENGTH, minute_angle, 2)  # 分針
    draw_hand(SECOND_HAND_LENGTH, second_angle, 1)  # 秒針
    
    # 更新顯示
    display.show()

# 創建TimeToDo對象，每秒更新一次
clock_updater = TimeToDo(1000)

# 主循環
while True:
    clock_updater.Do(update_clock)