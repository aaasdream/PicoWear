from TimeToDoFile import TimeToDo
from machine import Pin, I2C, RTC, Timer
import utime as time
import math
import gc
import sh1107
from Mpu6050_mahony import MPU6050
import micropython
import rp2
from machine import mem32
import network
import random  # 導入 random 模組

#====================PICO WARE Init====================================
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
snake_timer = TimeToDo(5)  # 控制蛇的移動速度 (5 FPS)
screen_update_timer = TimeToDo(15)  # 控制畫面更新速度 (約 16 FPS)
OnTiltAnglesTimeTo = TimeToDo(100)  # 設置陀螺儀更新頻率

# 遊戲常量
GRID_SIZE = const(8)
SCREEN_WIDTH = const(128)
SCREEN_HEIGHT = const(128)

# 遊戲變量
snake = [(4, 4), (4, 5), (4, 6)]  # 初始蛇身
food = (10, 10)
direction = (0, -1)  # 初始方向為上
game_over = False

# 更新陀螺儀數據
def update_gyro_data():
	mpu.update_mahony()
	global direction

	roll, pitch, _ = mpu.get_angles()
	new_direction = direction  # 初始化為當前方向

	if abs(roll) > abs(pitch):
		if roll > 10:
			new_direction = (1, 0)  # 向右
		elif roll < -10:
			new_direction = (-1, 0)  # 向左
	else:
		if pitch > 10:
			new_direction = (0, -1)  # 向上
		elif pitch < -10:
			new_direction = (0, 1)  # 向下

	# 檢查新方向是否與當前方向相反
	if (new_direction[0] != -direction[0] or new_direction[1] != -direction[1]):
		direction = new_direction

# 初始化食物
def init_food():
	global food
	while True:
		food = (random.randint(0, (SCREEN_WIDTH // GRID_SIZE) - 1),
				random.randint(0, (SCREEN_HEIGHT // GRID_SIZE) - 1))
		if food not in snake:
			break

# 更新遊戲狀態
def update_game():
	global snake, food, direction, game_over

	# 計算新的蛇頭位置
	new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

	# 檢查碰撞
	if (new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH // GRID_SIZE or
		new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT // GRID_SIZE or
		new_head in snake):
		game_over = True
		return

	# 更新蛇的位置
	snake.insert(0, new_head)

	# 檢查是否吃到食物
	if new_head == food:
		init_food()  # 生成新的食物
	else:
		snake.pop()  # 沒有吃到食物就移除蛇尾

# 繪製遊戲畫面
def draw_game():
	display.fill(0)
	
	# 繪製蛇
	for segment in snake:
		display.fill_rect(segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE, 1)
	
	# 繪製食物
	display.fill_rect(food[0] * GRID_SIZE, food[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE, 1)
	
	display.show()

def draw_game_over():
	display.fill(0)
	display.text("GAME OVER", 28, 60, 1)
	display.show()

# 初始化遊戲
def init_game():
	global snake, food, direction, game_over
	snake = [(4, 4), (4, 5), (4, 6)]  # 初始蛇身
	direction = (0, -1)  # 初始方向為上
	game_over = False
	init_food()
    
    
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
		snake_timer.Do(update_game)
		screen_update_timer.Do(draw_game)
		CalButton()

		if game_over:
			draw_game_over()
			time.sleep(2)  # 遊戲結束後暫停2秒
			init_game()

if __name__ == '__main__':
	main()
