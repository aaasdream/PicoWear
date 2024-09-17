import sh1107
import Pico_Wear
import random
import time

display, mpu = Pico_Wear.Pico_Wear_Init()

def draw_text_center(text, y):
    text_width = len(text) * 8  # 假设每个字符宽度为8像素
    x = (128 - text_width) // 2
    display.text(text, x, y, 1)

def explode_text(text):
    letters = list(text)
    positions = [(64, 64) for _ in letters]  # 初始位置在屏幕中心
    velocities = [(random.randint(-5, 5), random.randint(-5, 5)) for _ in letters]
    
    start_time = time.time()
    while time.time() - start_time < 3:  # 动画持续3秒
        display.fill(0)
        for i, letter in enumerate(letters):
            x, y = positions[i]
            vx, vy = velocities[i]
            
            # 更新位置
            x += vx
            y += vy
            
            # 边界检查
            if x < 0 or x > 120:
                vx = -vx
            if y < 0 or y > 120:
                vy = -vy
            
            positions[i] = (x, y)
            velocities[i] = (vx, vy)
            
            display.text(letter, int(x), int(y), 1)
        
        display.show()
        time.sleep(0.05)

def animation_loop():
    while True:
        display.fill(0)
        draw_text_center("HELLO WORLD", 60)
        display.show()
        time.sleep(1)
        
        explode_text("HELLO WORLD")

# 开始动画循环
animation_loop()