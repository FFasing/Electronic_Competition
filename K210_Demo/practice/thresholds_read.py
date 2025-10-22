import sensor,image,time,lcd
from machine import Timer,UART
from Maix import GPIO
from fpioa_manager import fm
import utime

#IO注册到内部GPIO,注意高速GPIO口才有中断
fm.register(6, fm.fpioa.UART1_RX, force=True)
fm.register(7, fm.fpioa.UART1_TX, force=True)
fm.register(12, fm.fpioa.GPIO0)
fm.register(13, fm.fpioa.GPIO1)
fm.register(14, fm.fpioa.GPIO2)
fm.register(16, fm.fpioa.GPIOHS0)   # 高速GPIO

#初始化IO
LED_B   =   GPIO(GPIO.GPIO0, GPIO.OUT,value=1)
LED_G   =   GPIO(GPIO.GPIO1, GPIO.OUT,value=1)
LED_R   =   GPIO(GPIO.GPIO2, GPIO.OUT,value=1)
KEY     =   GPIO(GPIO.GPIOHS0, GPIO.IN)
uart    =   UART(UART.UART1, 115200)

#定义变量
key_state = 1
LED=[LED_B, LED_G, LED_R]
LED_show_num=0

lcd.init(freq=20000000)             # LCD初始化
lcd.clear()
lcd.rotation(2)                     # LCD翻转
sensor.reset()                      # Reset and initialize the sensor.
sensor.run(0)                       # run automatically
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.跳帧
sensor.set_brightness(-1)            # 亮度
sensor.set_vflip(0)                 # 摄像头翻转
clock = time.clock()                # Create a clock object to track the FPS.

# 颜色识别阈值 (L Min, L Max, A Min, A Max, B Min, B Max) LAB模型
thresholds = [                      # 颜色阈值thresholds[]
          (93, 100, -2, 127, 1, 127)
          (54, 100, 7, 127, 5, 127)]

uart.write('this is K210\r')
#主函数
while(True):
    clock.tick()                    # Update the FPS clock.
    img = sensor.snapshot()         # Take a picture and return the image.
    text=uart.read()                # 读取数据
    if text:                        # 如果读取到了数据
        uart_read_data = text.decode('utf-8')
        print('uart_read:'+text.decode('utf-8')) # REPL打印

    color_blobs1 = img.find_blobs([thresholds[0]],area_threshold=10)
    color_blobs2 = img.find_blobs([thresholds[1]],area_threshold=10)
    blob_max=0
    if color_blobs1:
        for b in color_blobs1:
            if(b[4]>=blob_max):
                blob_max=b[4]
                middle1=b[5]
                tmp=img.draw_rectangle(b[0:4],color=(20,20,60),thickness=2)
                print(b[4])
    blob_max=0
    if color_blobs2:
        for b in color_blobs2:
            if(b[4]>=blob_max):
                blob_max=b[4]
                middle2=b[5]
                #if(middle1-middle2)
                tmp=img.draw_rectangle(b[0:4],color=(220,20,60),thickness=2)
                print(b[4])

    lcd.display(img)                # Display on LCD
