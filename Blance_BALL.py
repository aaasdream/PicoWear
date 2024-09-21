
from machine import Pin, I2C, RTC,Timer
from TimeToDoFile import TimeToDo
import utime as time
import math
import gc

from Mpu6050_mahony import MPU6050
import micropython
import rp2
from machine import mem32
import network
import time
from Pico_Wear import PicoWear
#====================PICO WEAR Init====================================
pico = PicoWear()

#====================PICO WARE Init End====================================
OnUpdateScreenTimeTo = TimeToDo(60) #每秒60張
OnTiltAnglesTimeTo = TimeToDo(100) #每秒100次


        
def CalButton():
    #按鈕按一下進行校正
    button = rp2.bootsel_button()
    if button == 1:
        # 只按一下
        while button == 1:
            button = rp2.bootsel_button()
      
        

# 更新陀螺儀數據
def update_gyro_data():
    pico.mpu.update_mahony()
    
# 畫圓球函數
def draw_ball():
    
    roll, pitch , yaw = pico.mpu.get_angles()
    pico.display.fill(0)
    # 計算圓球的位置
    x = int(64 + (roll / 45) * 64)
    y = int(64 - (-pitch / 45) * 64)
    
    # 保證圓球在螢幕內
    x = max(0, min(127, x))
    y = max(0, min(127, y))
    
    # 畫出連接圓球的線
    pico.display.line(64, 64, x, y, 1)
    
    # 畫出圓球
    pico.display.fill_circle(x, y, 5, 1)
    
    # 顯示結果
    pico.display.show()


if __name__ == '__main__':
    while True:
        CalButton()
        OnTiltAnglesTimeTo.Do(update_gyro_data)
        OnUpdateScreenTimeTo.Do(draw_ball)
        