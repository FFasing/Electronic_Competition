import sensor, image, time, lcd, utime
from machine import Timer
from Maix import GPIO
from fpioa_manager import fm

loop = False
mod = 1
Key_Set_State = 1
KEY_State = 1

#注册IO，蓝灯-->IO12,KEY-->IO16
fm.register(12, fm.fpioa.GPIO0)
fm.register(16, fm.fpioa.GPIOHS0)       # 高速GPIO
fm.register(10, fm.fpioa.GPIOHS1)       # 高速GPIO

#初始化IO
LED_B   =    GPIO(GPIO.GPIO0, GPIO.OUT)
KEY     =    GPIO(GPIO.GPIOHS0, GPIO.IN)
Key_Set =    GPIO(GPIO.GPIOHS1, GPIO.IN, GPIO.PULL_UP)

lcd.init(freq=20000000)
lcd.clear()
lcd.rotation(0)                     # LCD翻转
sensor.reset()                      # Reset and initialize the sensor.
sensor.run(0)                       # run automatically
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.跳帧
sensor.set_brightness(2)            # 亮度
sensor.set_vflip(1)                 # 摄像头翻转
clock = time.clock()                # Create a clock object to track the FPS.

def fun(KEY):                           #中断回调函数
    global KEY_State,mod,loop
    utime.sleep_ms(10)                  #消除抖动
    if KEY.value()==0:                  #确认按键被按下
        print(KEY)
KEY.irq(fun, GPIO.IRQ_FALLING)          #开启中断，下降沿触发


def fun(Key_Set):                           #中断回调函数
    utime.sleep_ms(10)                      #消除抖动
    if Key_Set.value()==0:                  #确认按键被按下
        utime.sleep_ms(10)                  #消除抖动
        if Key_Set.value()==0:
            print(Key_Set)
Key_Set.irq(fun, GPIO.IRQ_FALLING)          #开启中断，下降沿触发

while(True):
    clock.tick()                    # Update the FPS clock.
    img = sensor.snapshot()         # Take a picture and return the image.
    lcd.display(img)                # Display on LCD
    if KEY.value()==0:              #按键被按下接地
        LED_B.value(0)              #点亮LED_B,蓝灯
    else:
        LED_B.value(1)              #熄灭LED
