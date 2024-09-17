import TimeToDo
from machine import Pin, I2C, RTC,Timer
    
import utime as time
import math
import gc
import sh1107
from Mpu6050_mahony import MPU6050
import micropython
import rp2
from machine import mem32
import network
import time
#====================PICO WEAR Init====================================
# OLED 的電源
PAD_CONTROL_REGISTER = 0x4001c024
mem32[PAD_CONTROL_REGISTER] = mem32[PAD_CONTROL_REGISTER] | 0b0110000

# 設定 GP9 為輸出，並設置輸出(GND), GP8 為輸出，並設置輸出 1
pin9 = Pin(9, Pin.OUT, value=0)
pin8 = Pin(8, Pin.OUT, value=0)
time.sleep(1)
pin8 = Pin(8, Pin.OUT, value=1)

# mpu6050 的電源
PAD_CONTROL_REGISTER = 0x4001c05c
mem32[PAD_CONTROL_REGISTER] = mem32[PAD_CONTROL_REGISTER] | 0b0110000

# GP22 為輸出，並設置輸出 1
pin22 = Pin(22, Pin.OUT, value=0)
time.sleep(1)
pin22 = Pin(22, Pin.OUT, value=1)
time.sleep(1)
# 初始化I2C
i2c0 = I2C(0, scl=Pin(21), sda=Pin(20), freq=400000)
i2c1 = I2C(1, scl=Pin(7), sda=Pin(6), freq=400000)
display = sh1107.SH1107_I2C(128, 128, i2c1, None, 0x3c)

# 清空顯示屏
display.fill(0)
display.show()

# 初始化MPU6050
mpu = MPU6050(i2c0)

#====================PICO WARE Init End====================================
update_timer = TimeToDo.TimeToDo(50)  # 60 FPS
OnTiltAnglesTimeTo = TimeToDo.TimeToDo(10) #每秒100次

# 遊戲常量
PADDLE_WIDTH = const(20)
PADDLE_HEIGHT = const(5)
BALL_SIZE = const(3)
BRICK_WIDTH = const(16)
BRICK_HEIGHT = const(10)
BRICK_ROWS = const(3)
BRICK_COLS = const(8)

# 遊戲變量
paddle_x = 64 - PADDLE_WIDTH // 2
ball_x = 64
ball_y = 100
ball_dx = 2
ball_dy = -2
bricks = []
ball_speed = 1
game_over = False
game_won = False
# 更新陀螺儀數據
def update_gyro_data():
    mpu.update_mahony()
# 初始化磚塊
def init_bricks():
    global bricks
    bricks = []
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            brick = {
                'x': col * (BRICK_WIDTH + 2) + 4,
                'y': row * (BRICK_HEIGHT + 2) + 10,
                'w': BRICK_WIDTH,
                'h': BRICK_HEIGHT,
                'visible': True
            }
            bricks.append(brick)

# 更新遊戲狀態
def update_game():
    global paddle_x, ball_x, ball_y, ball_dx, ball_dy ,ball_speed,game_over,game_won

    # 更新球拍位置
    roll, _, _ = mpu.get_angles()
    paddle_x = int(64 + (roll / 30) * 64) - PADDLE_WIDTH // 2
    paddle_x = max(0, min(128 - PADDLE_WIDTH, paddle_x))

    # 更新球的位置
    ball_x += ball_dx * ball_speed
    ball_y += ball_dy * ball_speed
    ball_speed += 0.001 

    # 檢查邊界碰撞
    if ball_x <= 0 or ball_x >= 127:
        ball_dx = -ball_dx
    if ball_y <= 0:
        ball_dy = -ball_dy

    # 檢查球拍碰撞
    if ball_y >= 120 - PADDLE_HEIGHT and paddle_x <= ball_x <= paddle_x + PADDLE_WIDTH:
        ball_dy = -ball_dy

    # 檢查磚塊碰撞
    for brick in bricks:
        if brick['visible']:
            if (brick['x'] <= ball_x <= brick['x'] + brick['w'] and
                brick['y'] <= ball_y <= brick['y'] + brick['h']):
                brick['visible'] = False
                ball_dy = -ball_dy
                ball_y = brick['y'] + brick['h']
                break

    # Check for win condition
    if all(not brick['visible'] for brick in bricks):
        game_won = True
     # Game over condition
    if ball_y > 128:
        game_over = True

    if (game_over == True):
        draw_game_over()
    elif(game_won == True):
        draw_win_screen()
    else:
        draw_game()
# 繪製遊戲畫面
def draw_game():
    display.fill(0)
    
    # 繪製球拍
    display.fill_rect(paddle_x, 120, PADDLE_WIDTH, PADDLE_HEIGHT, 1)
    
    # 繪製球
    display.fill_rect(int(ball_x) - BALL_SIZE // 2, int(ball_y) - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE, 1)
    
    # 繪製磚塊
    for brick in bricks:
        if brick['visible']:
            display.rect(brick['x'], brick['y'], brick['w'], brick['h'], 1)
    
    display.show()

def draw_win_screen():
    display.fill(0)
    display.text("YOU WIN", 30, 60, 1)
    display.show()
def draw_game_over():
    display.fill(0)
    display.text("GAME OVER", 28, 60, 1)
    display.show()
# 初始化遊戲
def init_game():
    global paddle_x, ball_x, ball_y, ball_dx, ball_dy,game_over,game_won
    paddle_x = 64 - PADDLE_WIDTH // 2
    game_over = False
    game_won = False
    ball_x = 64
    ball_y = 100
    ball_dx = 2
    ball_dy = -2
    ball_speed = 1
    init_bricks()
    
    
def CalButton():
    #按鈕按一下進行校正
    button = rp2.bootsel_button()
    if button == 1:
        # 只按一下
        while button == 1:
            button = rp2.bootsel_button()
        time.sleep(0.5)#等待手的抖動停止才校正
        init_game()
        
# 主遊戲循環
def main():
    init_game()
    
    while True:
        OnTiltAnglesTimeTo.Do(update_gyro_data)
        update_timer.Do(update_game)
        CalButton()

if __name__ == '__main__':
    main()
        