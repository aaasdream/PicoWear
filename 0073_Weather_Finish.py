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
        current_weather = data['list'][0]['weather'][0]['icon']
        
        forecasts = []
        for item in data['list']:
            dt = utime.localtime(item['dt'])
            if dt[3] == 12:  # 只选择中午12点的数据
                forecasts.append({
                    'date': "{:02d}/{:02d}".format(dt[1], dt[2]),
                    'temp': item['main']['temp'],
                    'icon': item['weather'][0]['icon']
                })
                if len(forecasts) == 4:  # 只取4天的预报
                    break
        
        return current_temp, current_humidity, current_weather, forecasts
    except:
        return None, None, None, None

# 加载天气图标
def load_weather_icon(icon):
    if icon.endswith('n'):
        icon = icon[:-1] + 'd'
    try:
        return pico_wear.display.read_bmp_mono(f'WeatherImage/{icon}.bmp')
    except:
        return None

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
    temp, humidity, weather_icon, forecasts = None, None, None, None
    
    # 主循环显示时间和天气
    while True:
        current_time = utime.time() + 8 * 3600  # 调整为 +8 时区
        local_time = utime.localtime(current_time)
        
        # 每小时更新一次天气
        if current_time - last_weather_update >= 3600:
            temp, humidity, weather_icon, forecasts = get_weather()
            last_weather_update = current_time
        
        date_str = "{:04d}-{:02d}-{:02d}".format(local_time[0], local_time[1], local_time[2])
        time_str = "{:02d}:{:02d}:{:02d}".format(local_time[3], local_time[4], local_time[5])
        
        pico_wear.display.fill(0)
        pico_wear.display.text(date_str, 0, 0)
        pico_wear.display.text(time_str, 0, 16)
        
        if temp is not None and humidity is not None and weather_icon is not None:
            temp_str = "{:.1f}C".format(temp)
            humidity_str = "{}%".format(humidity)
            pico_wear.display.text(temp_str, 0, 32)
            pico_wear.display.text(humidity_str, 0, 48)
            
            # 显示当前天气图标
            current_icon = load_weather_icon(weather_icon)
            if current_icon:
                pico_wear.display.drawBitmap(current_icon, 96, 32)
            
            if forecasts:
                for i, forecast in enumerate(forecasts):
                    x = i * 32
                    y = 80
                    icon = load_weather_icon(forecast['icon'])
                    if icon:
                        pico_wear.display.drawBitmap(icon, x, y)
                    pico_wear.display.text("{:.0f}".format(forecast['temp']), x, y + 32)
        else:
            pico_wear.display.text("Weather Error", 0, 32)
        
        pico_wear.display.show()
        
        utime.sleep(1)

if __name__ == "__main__":
    main()