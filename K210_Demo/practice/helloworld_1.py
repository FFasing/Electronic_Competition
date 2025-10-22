#------------------库函数申明------------------#
import math , sensor, image, time, lcd , utime
from machine import Timer
from machine import I2C
from Maix import GPIO
from fpioa_manager import fm
import touchscreen as ts

#------------------设备初始化------------------#
i2c = I2C(I2C.I2C0, freq=400000, scl=30, sda=31)#NS2009
ts.init(i2c)
ts.calibrate() #触摸校准
lcd.init(freq=20000000)
lcd.clear()
sensor.reset()                      # Reset and initialize the sensor. It will7
sensor.run(0)                       # run automatically, call sensor.run(0) to stop
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
sensor.set_brightness(2)            #亮度
sensor.set_vflip(1)                 #翻转
clock = time.clock()                # Create a clock object to track the FPS.
#------------------全局变量申明------------------#
yellow_threshold   = (75, 100, -109, 6, 14, 67)  #色块
led_val = 1         #led灯
key_val,key_old,key_down = [0,0,0]

status_last = ts.STATUS_IDLE
x_last = 0
y_last = 0

#--------------------GPIO配置--------------------#
#注册 LED_B->IO12 KEY->IO16
fm.register(12,fm.fpioa.GPIO0)
fm.register(16,fm.fpioa.GPIOHS0)#高速GPIO才有中断
#构建 LED_B , KEY 对象
LED_B   =  GPIO(GPIO.GPIO0, GPIO.OUT,value=led_val)
KEY     =  GPIO(GPIO.GPIOHS0, GPIO.IN, GPIO.PULL_UP)

#---------------------功能函数---------------------#
def ts_draw():
    global x_last,y_last,status_last    #引用全局变量
    status_condition = False
    (status,x,y) = ts.read()            #获取触摸屏状态
    #print(status, x, y)
    if status_last!=status:             #根据触摸屏状态判断是否触摸
        if (status==ts.STATUS_PRESS or status == ts.STATUS_MOVE):
            status_condition = True
            x_last=x
            y_last=y
        else:                           #松开
            status_condition = False
            x_last=y_last=0
        status_last = status
    tmp=img.draw_string(1,1,("x=%3.2d,y=%3.2d"%(x_last,y_last)),color=(220,20,60),scale=1.5)

def yellow_draw_blobs(dat):
    for b in dat:
        if(b[4]>=2000):   #S(blobs)>2000
            tmp=img.draw_rectangle(b[0:4],color=(220,20,60),thickness=3)
            img.draw_circle(b[5],b[6],3,color=(220,20,60),thickness=3)
            tmp=img.draw_cross(b[5],b[6],color=(220,20,60))
            #mg.draw_string(1,1,("x=%3.2d,y=%3.2d"%(b[5],b[6])),color=(220,20,60),scale=1.5)

def key_read():
    global key_val,key_old,key_down
    key_val=0
    if KEY.value()==0:
        key_val=1
    key_down=key_val&(key_val^key_old)
    key_old=key_val
    return key_down

#--------------------中断函数--------------------#
#def key_read(KEY):               #中断回调函数
#  utime.sleep_ms(10)
def fun(tim):               #定时器回调函数
    global led_val,count    #引用全局变量
    if key_read()==1:
        led_val^=1
        LED_B.value(led_val)

#------------------中断配置初始化------------------#
#KEY.irq(key_read,GPIO.IRQ_FALLING)                       #开启中断，下降沿触发
tim = Timer(Timer.TIMER0,Timer.CHANNEL0,mode=Timer.MODE_PERIODIC,
            unit=Timer.UNIT_US,period=1000,callback=fun)  #定时器0初始化，周期100Us

#-----------------------主函数-----------------------#
while(True):
    clock.tick()                    # Update the FPS clock.
    img = sensor.snapshot()         # Take a picture and return the image.
    blobs = img.find_blobs([yellow_threshold])    #色彩识别
    if blobs:
        yellow_draw_blobs(blobs)
    ts_draw()
    lcd.display(img)                # Display on LCD
