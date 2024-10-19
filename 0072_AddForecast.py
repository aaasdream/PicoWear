from Pico_Wear import PicoWear
import network
import ntptime
import utime
import urequests
import ujson

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

# 获取天气数据函数
def get_weather():
    api_key = "7f627de3cadbfddef4e401844d78dcf2"
    lat = "24.0058594"
    lon = "121.5857252"
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    
    try:
        response = urequests.get(url)
        data = ujson.loads(response.text)
        response.close()
        
        current_temp = data['list'][0]['main']['temp']
        current_humidity = data['list'][0]['main']['humidity']
        current_weather = data['list'][0]['weather'][0]['main']
        
        forecasts = []
        for item in data['list']:
            dt = utime.localtime(item['dt'])
            if dt[3] == 12:  # 只选择中午12点的数据
                forecasts.append({
                    'date': "{:02d}/{:02d}".format(dt[1], dt[2]),
                    'temp': item['main']['temp'],
                    'weather': item['weather'][0]['main']
                })
                if len(forecasts) == 5:
                    break
        
        return current_temp, current_humidity, current_weather, forecasts
    except:
        return None, None, None, None

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
    
    last_weather_update = 0
    temp, humidity, weather, forecasts = None, None, None, None
    forecast_index = 0
    
    # 主循环显示时间和天气
    while True:
        current_time = utime.time() + 8 * 3600  # 调整为 +8 时区
        local_time = utime.localtime(current_time)
        
        # 每小时更新一次天气
        if current_time - last_weather_update >= 3600:
            temp, humidity, weather, forecasts = get_weather()
            last_weather_update = current_time
        
        date_str = "{:04d}-{:02d}-{:02d}".format(local_time[0], local_time[1], local_time[2])
        time_str = "{:02d}:{:02d}:{:02d}".format(local_time[3], local_time[4], local_time[5])
        
        pico_wear.display.fill(0)
        pico_wear.display.text(date_str, 0, 0)
        pico_wear.display.text(time_str, 0, 16)
        
        if temp is not None and humidity is not None and weather is not None:
            temp_str = "T:{:.1f}C".format(temp)
            humidity_str = "H:{}%".format(humidity)
            pico_wear.display.text(temp_str, 0, 32)
            pico_wear.display.text(weather, 64, 32)  # 在第三行中间显示天气
            pico_wear.display.text(humidity_str, 0, 48)
            
            if forecasts:
                forecast = forecasts[forecast_index]
                forecast_str = "{} {:.1f}C {}".format(forecast['date'], forecast['temp'], forecast['weather'])
                pico_wear.display.text(forecast_str, 0, 64)
                forecast_index = (forecast_index + 1) % len(forecasts)
        else:
            pico_wear.display.text("Weather Error", 0, 32)
        
        pico_wear.display.show()
        
        utime.sleep(1)

if __name__ == "__main__":
    main()