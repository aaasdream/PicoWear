from Pico_Wear import PicoWear
import time
import math
import random

# ========== 全域變數 ==========
pico_wear = None
plane_x, plane_y = 0, 20
supply_x, supply_y = 0, 20
ship_x, ship_y = 110, 100
sea_level = 110
is_dropping = False
animation_step = 0
result = ""
# =============================

def reset_animation():
    global plane_x, plane_y, supply_x, supply_y, is_dropping, animation_step, result
    plane_x, plane_y = 0, 20
    supply_x, supply_y = 0, 20
    is_dropping = False
    animation_step = 0
    result = ""

def button_callback():
    reset_animation()

def update_animation():
    global plane_x, plane_y, supply_x, supply_y, is_dropping, animation_step, result
    
    if animation_step < 50:
        plane_x += 2
        if not is_dropping and plane_x > 40:
            is_dropping = True
            supply_x, supply_y = plane_x, plane_y
    
    if is_dropping:
        supply_x += 2
        supply_y += animation_step // 5
        
        # 打印關鍵參數
        print(f"Step: {animation_step}, Supply X: {supply_x}, Supply Y: {supply_y}")
        
        if supply_y >= sea_level:
            if abs(supply_x - ship_x) < 10:
                result = "Success"
            else:
                result = "Fail"
            # 打印最終結果
            print(f"Final result: {result}")
            print(f"Final Supply X: {supply_x}, Final Supply Y: {supply_y}")
            print(f"Ship X: {ship_x}, Ship Y: {ship_y}")
    
    animation_step += 1
    if animation_step >= 100:
        reset_animation()

def draw_scene():
    pico_wear.display.fill(0)
    
    # Draw sea
    pico_wear.display.fill_rectangle(0, sea_level, 128, 18, 1)
    
    # Draw ship
    pico_wear.display.fill_rectangle(ship_x-5, ship_y-10, 10, 10, 1)
    
    # Draw plane
    pico_wear.display.fill_rectangle(plane_x, plane_y, 10, 5, 1)
    
    # Draw supply
    if is_dropping:
        pico_wear.display.fill_rectangle(supply_x, supply_y, 3, 3, 1)
    
    # Draw result
    if result:
        pico_wear.display.text(result, 40, 60, 1)
    
    pico_wear.display.show()

def main():
    global pico_wear
    pico_wear = PicoWear()
    print('完成 Pico Wear 的初始化')
    
    pico_wear.register_button_callback(button_callback)
    
    while True:
        update_animation()
        draw_scene()
        time.sleep(0.1)

if __name__ == '__main__':
    main()