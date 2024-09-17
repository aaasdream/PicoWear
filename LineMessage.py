import network
import urequests as requests  # 修改為 urequests，這是 MicroPython 使用的模組

# 如果使用 Pico W，連接到 Wi-Fi
ssid = 'HINET1'
password = '12345678'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# 等待連接 Wi-Fi
while not wlan.isconnected():
    pass

print('已連接到 Wi-Fi')

def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = 'message=' + msg
    try:
        r = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=payload)
        print("LINE Notify 已發送 (" + str(r.status_code) + ")，Wi-Fi 狀態 = " + str(wlan.status()))
        r.close()
    except Exception as e:
        print("無法連接，錯誤: " + str(e) + " (Wi-Fi 狀態 = " + str(wlan.status()) + ")")


# 請替換為您的 Line Notify 權杖
token = "1pEOrZSrSRTCDw4R7qmd57JURb5497EzQj5a3TTWlh9"
lineNotifyMessage(token, "This message from pico.")
