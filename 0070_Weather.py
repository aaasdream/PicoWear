from Pico_Wear import PicoWear
import time
import ntptime
import urequests
import json

# 初始化 PicoWear 对象
pico = PicoWear()

# Wi-Fi 设置
SSID = "HINET1"
PASSWORD = "12345678"

# OpenWeatherMap 设置
API_KEY = "7f627de3cadbfddef4e401844d78dcf2"
LAT = "23.33152"
LON = "121.3091451"
WEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
FORECAST_URL = f"http://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"

# 全局变量存储天气信息
weather_info = {"temp": 0, "humidity": 0, "icon": "01d"}
forecast_info = []

# 加载天气图标
def load_weather_icon(icon):
    if icon.endswith('n'):
        icon = icon[:-1] + 'd'
    filename = f"/WeatherImage/{icon}.bmp"
    return pico.display.read_bmp_mono(filename)

# 连接 Wi-Fi 并显示状态
def connect_wifi():
    pico.display.fill(0)
    pico.display.text("Connecting to", 0, 0, 1)
    pico.display.text("Wi-Fi...", 0, 10, 1)
    pico.display.show()
    
    pico.wifi.connect(SSID, PASSWORD)
    
    retry = 0
    while not pico.wifi.isconnected() and retry < 20:
        time.sleep(1)
        retry += 1
    
    if pico.wifi.isconnected():
        ip_address = pico.wifi.ifconfig()[0]
        pico.display.fill(0)
        pico.display.text("Connected!", 0, 0, 1)
        pico.display.text("IP:", 0, 10, 1)
        pico.display.text(ip_address, 0, 20, 1)
        pico.display.show()
        time.sleep(3)
        return True
    else:
        pico.display.fill(0)
        pico.display.text("Connection", 0, 0, 1)
        pico.display.text("failed!", 0, 10, 1)
        pico.display.show()
        return False

# 设置时间
def set_time():
    retry = 0
    while retry < 3:
        try:
            ntptime.settime()
            break
        except:
            retry += 1
            time.sleep(1)
    
    # 调整时区 (+8 小时)
    rtc = machine.RTC()
    current_time = list(time.localtime())
    current_time[3] = (current_time[3] + 8) % 24  # 调整小时
    rtc.datetime((current_time[0], current_time[1], current_time[2], current_time[6] + 1,
                  current_time[3], current_time[4], current_time[5], 0))


# 获取当前天气信息
def get_weather():
    global weather_info
    try:
        response = urequests.get(WEATHER_URL)
        data = json.loads(response.text)
        weather_info["temp"] = round(data["main"]["temp"])
        weather_info["humidity"] = data["main"]["humidity"]
        weather_info["icon"] = data["weather"][0]["icon"]
        response.close()
    except:
        print("Failed to get weather info")

# 获取5天天气预报
def get_forecast():
    global forecast_info
    try:
        response = urequests.get(FORECAST_URL)
        data = json.loads(response.text)
        forecast_info = []
        for item in data["list"]:
            dt = time.localtime(item["dt"])
            if dt[3] == 12:  # 只取中午12点的数据
                forecast_info.append({
                    "date": "{:02d}/{:02d}".format(dt[1], dt[2]),
                    "temp": round(item["main"]["temp"]),
                    "icon": item["weather"][0]["icon"]
                })
            if len(forecast_info) == 4:  # 只取4天的预报
                break
        response.close()
    except:
        print("Failed to get forecast info")

# 显示日期、时间、当前天气和未来天气
def display_info():
    last_weather_update = 0
    while True:
        now = time.localtime()
        current_time = time.time()
        
        # 每小时更新一次天气
        if current_time - last_weather_update >= 3600:
            get_weather()
            get_forecast()
            last_weather_update = current_time
        
        date_str = "{:04d}/{:02d}/{:02d}".format(now[0], now[1], now[2])
        time_str = "{:02d}:{:02d}:{:02d}".format(now[3], now[4], now[5])
        temp_str = "T:{:d}C".format(weather_info["temp"])
        humidity_str = "H:{:d}%".format(weather_info["humidity"])
        
        pico.display.fill(0)
        pico.display.text(date_str, 0, 0, 1)
        pico.display.text(time_str, 0, 10, 1)
        
        # 显示当前天气图标和温度
        current_icon = load_weather_icon(weather_info["icon"])
        pico.display.drawBitmap(current_icon, 0, 20)
        pico.display.text(temp_str, 40, 30, 1)
        pico.display.text(humidity_str, 40, 40, 1)
        
        # 显示未来4天天气预报
        for i, forecast in enumerate(forecast_info):
            x = i * 32
            y = 60
            icon = load_weather_icon(forecast["icon"])
            pico.display.drawBitmap(icon, x, y)
            pico.display.text("{:d}C".format(forecast["temp"]), x, y + 32, 1)
        
        pico.display.show()
        time.sleep(1)

# 主程序
def main():
    if connect_wifi():
        set_time()
        get_weather()  # 初始获取天气信息
        get_forecast()  # 初始获取天气预报
        display_info()

if __name__ == "__main__":
    main()