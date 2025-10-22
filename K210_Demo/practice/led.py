import sensor, image, time, lcd
from machine import Timer
from Maix import GPIO
from fpioa_manager import fm

#IO注册到内部GPIO,注意高速GPIO口才有中断
fm.register(12, fm.fpioa.GPIO0)
fm.register(13, fm.fpioa.GPIO1)
fm.register(14, fm.fpioa.GPIO2)
fm.register(16, fm.fpioa.GPIOHS0)   #高速

#初始化IO
LED_B = GPIO(GPIO.GPIO0, GPIO.OUT,value=1)
LED_G = GPIO(GPIO.GPIO1, GPIO.OUT,value=1)
LED_R = GPIO(GPIO.GPIO2, GPIO.OUT,value=1)
KEY = GPIO(GPIO.GPIOHS0, GPIO.IN)

#定义变量
key_val=0
key_old=0
key_down=0
LED=[LED_B, LED_G, LED_R]
LED_show_num=0

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

while(True):
    clock.tick()                    # Update the FPS clock.
    img = sensor.snapshot()         # Take a picture and return the image.
    lcd.display(img)                # Display on LCD
    if KEY.value()==0: #按键被按下接地
        key_val=1
    else:
        key_val=0
    key_down=key_val&(key_val^key_old)
    key_old=key_val
    if key_down==1:
        LED_show_num=LED_show_num+1
        if LED_show_num==3:
            LED_show_num=0
        print(LED_show_num)
    LED[LED_show_num].value(0)
    LED[LED_show_num-1].value(1)


