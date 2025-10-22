import sensor,image,time,lcd,utime
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
LED = [LED_B, LED_G, LED_R]
key_state = 1
Counter = 0                           #计数变量

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

#定时器回调函数
def fun(tim):
    global Counter
    Counter = Counter + 1
    print(Counter)

#定时器0初始化，周期1秒
tim = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PERIODIC, period=1000, callback=fun)

#主函数
while(True):
    clock.tick()                    # Update the FPS clock.
    img = sensor.snapshot()         # Take a picture and return the image.
    lcd.display(img)                # Display on LCD

