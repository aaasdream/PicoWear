from Pico_Wear import PicoWear
import network
import ntptime
import utime

# 初始化 PicoWear 对象
pico_wear = PicoWear()

# Wi-Fi 连接函数
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        pico_wear.display.fill(0)
        pico_wear.display.text("Connecting to", 0, 0)
        pico_wear.display.text("Wi-Fi...", 0, 16)
        pico_wear.display.show()
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    pico_wear.display.fill(0)
    pico_wear.display.text("Wi-Fi connected", 0, 0)
    pico_wear.display.text("IP:" + wlan.ifconfig()[0], 0, 16)
    pico_wear.display.show()
    utime.sleep(2)
    return wlan

# NTP 时间同步函数
def sync_ntp():
    for _ in range(3):  # 尝试 3 次
        try:
            ntptime.settime()
            return True
        except:
            utime.sleep(1)
    return False

# 主函数
def main():
    # 连接 Wi-Fi
    wlan = connect_wifi("hlc", "hlc8462860")
    
    # 同步 NTP 时间
    if sync_ntp():
        pico_wear.display.fill(0)
        pico_wear.display.text("Time synced", 0, 0)
        pico_wear.display.show()
    else:
        pico_wear.display.fill(0)
        pico_wear.display.text("Time sync failed", 0, 0)
        pico_wear.display.show()
    utime.sleep(2)
    
    # 主循环显示时间
    while True:
        current_time = utime.localtime(utime.time() + 8 * 3600)  # 调整为 +8 时区
        date_str = "{:04d}-{:02d}-{:02d}".format(current_time[0], current_time[1], current_time[2])
        time_str = "{:02d}:{:02d}:{:02d}".format(current_time[3], current_time[4], current_time[5])
        
        pico_wear.display.fill(0)
        pico_wear.display.text(date_str, 0, 0)
        pico_wear.display.text(time_str, 0, 16)
        pico_wear.display.show()
        
        utime.sleep(1)

if __name__ == "__main__":
    main()