'''
TimeToDoFile.py
此類別允許使用者設定一個函數，並根據初始化時指定的頻率（以每秒幀數或次數表示）定時執行該函數。

方法
__init__(self, FPS)

功能：初始化TimeToDo物件。
參數：
FPS：每秒幀數（次數），用於計算兩次函數呼叫之間的時間間隔。
描述：此建構函式設定每次呼叫之間的時間間隔（以微秒為單位），並記錄最後一次呼叫時間。
Do(self, func, *args, **kwargs)

功能：檢查是否到了應該執行函數的時間，如果是，則執行函數。
參數：
func：要執行的函數。
args： 提供func的位置參數。
kwargs： 提交給func的關鍵字參數。
描述：此方法檢查自上次執行以來是否已經過了足夠的時間（根據FPS設定的間隔）。
使用範例
以下是如何使用TimeToDo類別來定時執行一個簡單的列印任務：
from TimeToDoFile import TimeToDo
def test_function():
    print("Task is being executed.")

if __name__ == '__main__':
    scheduler = TimeToDo(1)  # 每秒執行一次
    while True:
        scheduler.Do(test_function)
'''


import utime as time

class TimeToDo:
    def __init__(self, FPS): 
        """
        初始化TimeToDo對象。
        :param FPS: 每秒幾張（次）。
        """
        self.interval =  1000000 / FPS
        self.last_time = time.ticks_us()

    def Do(self, func, *args, **kwargs):
        """
        檢查是否應該執行指定的函數，如果時間到則執行。        
        :param func: 要執行的函數。
        :param args: 函數的參數。
        :param kwargs: 函數的關鍵字參數。
        """
        current_time = time.ticks_us()
        if time.ticks_diff(current_time, self.last_time) >= self.interval:
            self.last_time = current_time
            func(*args, **kwargs)
            
def TestDo():
    print("Doing")
    
    
if __name__ == '__main__':
    TimeTo_Test = TimeToDo(1) #一秒1次
    while True:
        TimeTo_Test.Do(TestDo)