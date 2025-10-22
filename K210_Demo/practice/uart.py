import sensor, image, time, lcd
from machine import Timer,UART
from Maix import GPIO
from fpioa_manager import fm
import utime

#IO注册到内部GPIO,注意高速GPIO口才有中断
fm.register(12, fm.fpioa.GPIO0)
fm.register(13, fm.fpioa.GPIO1)
fm.register(14, fm.fpioa.GPIO2)
fm.register(16, fm.fpioa.GPIOHS0)   #高速GPIO
fm.register(6, fm.fpioa.UART1_RX, force=True)
fm.register(7, fm.fpioa.UART1_TX, force=True)

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

lcd.init(freq=20000000)
lcd.clear()
lcd.rotation(2)                     # LCD翻转
sensor.reset()                      # Reset and initialize the sensor.
sensor.run(0)                       # run automatically
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.跳帧
sensor.set_brightness(2)            # 亮度
sensor.set_vflip(0)                 # 摄像头翻转
clock = time.clock()                # Create a clock object to track the FPS.

uart.write('Hello , this is K210\r')

def fun(KEY):                       #中断回调函数
    global key_state
    utime.sleep_ms(10)              #消除抖动
    if KEY.value()==0:              #确认按键被按下
        key_state = not key_state
        uart.write('KEY DOWN')
KEY.irq(fun, GPIO.IRQ_FALLING)      #开启中断，下降沿触发

#主函数
while(True):
    clock.tick()                    # Update the FPS clock.
    img = sensor.snapshot()         # Take a picture and return the image.
    lcd.display(img)                # Display on LCD
    text=uart.read()                #读取数据
    if text:                        #如果读取到了数据
        uart_read_data = text.decode('utf-8')
        print('uart_read:'+text.decode('utf-8')) #REPL打印
        if uart_read_data == 'led on':
            LED_B.value(0)
            print('K210:LED_B OPEN')
        if uart_read_data == 'led off':
            LED_B.value(1)
            print('K210:LED_B OFF')

