import os
import time
from machine import I2C, Pin
import OLED_SH1107
from Mpu6050_mahony import MPU6050
from framebuf import FrameBuffer, MONO_VLSB
import rp2
from machine import mem32
import network

machine.freq(250000000)

#====================PICO WARE Init====================================
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

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
display = OLED_SH1107.SH1107_I2C(128, 128, i2c1, None, 0x3c)

# 清空顯示屏
display.fill(0)
display.show()

# 初始化MPU6050
mpu = MPU6050(i2c0)

# 取得所有py
def list_files():
	files = [f for f in os.listdir() if f.endswith(".py")]
	return files

# 显示文件列表并高亮选中的文件
def display_files(files, selected_index, scroll_offset):
	display.fill(0)
	visible_files = files[scroll_offset:scroll_offset+11]
	for i, file_name in enumerate(visible_files):
		y = i * 12
		if i + scroll_offset == selected_index:
			display.rect(0, y, 128, 12, 1)  # 绘制选中文件的方框
		display.text(file_name, 2, y + 2, 1)
	display.show()

# 获取当前的方向和倾斜角度
def get_direction():
	mpu.update_mahony()
	_, pitch, _ = mpu.get_angles()
	direction = 0
	if abs(pitch) > 5:
		direction = 1 if pitch > 0 else -1
		speed = min(max(abs(int(pitch)) - 5, 1), 5)  # 限制速度在1-5之间
	else:
		speed = 0
	return direction, speed

# 執行選中的 Python 檔案
def execute_file(file_name):
	print(f"Executing {file_name}...")
	# 使用 execfile 來執行選中的 Python 檔案
	try:
		exec(open(file_name).read())
	except Exception as e:
		print(f"Error executing {file_name}: {e}")

def main():
	files = list_files()
	if not files:
		print("No files found.")
		return
	
	selected_index = 0
	scroll_offset = 0
	display_files(files, selected_index, scroll_offset)
	
	last_update_time = time.ticks_ms()
	accumulated_movement = 0
	
	while True:
		direction, speed = get_direction()
		current_time = time.ticks_ms()
		
		if direction != 0 and time.ticks_diff(current_time, last_update_time) > 10:  # 50ms更新一次
			accumulated_movement += speed
			if accumulated_movement >= 1:
				pixels_to_move = int(accumulated_movement)
				accumulated_movement -= pixels_to_move
				
				new_index = selected_index + direction
				if 0 <= new_index < len(files):
					selected_index = new_index
					if selected_index < scroll_offset:
						scroll_offset = max(0, scroll_offset - 1)
					elif selected_index >= scroll_offset + 11:
						scroll_offset = min(len(files) - 11, scroll_offset + 1)
				
				display_files(files, selected_index, scroll_offset)
				last_update_time = current_time

		button = rp2.bootsel_button()
		if button == 1:
			while button == 1:
				button = rp2.bootsel_button()
			print(f"Selected file: {files[selected_index]}")
			execute_file(files[selected_index])
			time.sleep(0.5)

if __name__ == "__main__":
	main()
