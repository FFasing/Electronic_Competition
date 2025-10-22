import sensor,image,time,lcd,utime
from machine import Timer,UART,PWM
from Maix import GPIO
from fpioa_manager import fm

#-IO注册到内部GPIO,注意高速GPIO口才有中断#
fm.register(16, fm.fpioa.GPIOHS3)
fm.register(10, fm.fpioa.GPIOHS10)
fm.register(11, fm.fpioa.GPIOHS11)
fm.register(6 , fm.fpioa.GPIO6)
fm.register(7 , fm.fpioa.GPIO7)
fm.register(8 , fm.fpioa.GPIO5)
fm.register(9 , fm.fpioa.GPIO4)
fm.register(12, fm.fpioa.UART1_RX, force=True)
fm.register(13, fm.fpioa.UART1_TX, force=True)


#-初始化IO-#
KEY         =   GPIO(GPIO.GPIOHS3, GPIO.IN, GPIO.PULL_UP)
Key_IO10    =   GPIO(GPIO.GPIOHS10, GPIO.IN, GPIO.PULL_UP)
Key_IO11    =   GPIO(GPIO.GPIOHS11, GPIO.IN, GPIO.PULL_UP)
Key_IO6     =   GPIO(GPIO.GPIO6, GPIO.IN, GPIO.PULL_UP)
Key_IO7     =   GPIO(GPIO.GPIO7, GPIO.IN, GPIO.PULL_UP)
Key_IO8     =   GPIO(GPIO.GPIO5, GPIO.IN, GPIO.PULL_UP)
Key_IO9     =   GPIO(GPIO.GPIO4, GPIO.IN, GPIO.PULL_UP)
uart        =   UART(UART.UART1, 115200)    #uart.read(),uart.write()

#全局变量定义
loop = False

key_set_slow_down=0
KEY_State = 1
Key_Val=0
Key_Down=0
Key_Old=0

rect_threshold=[(0, 31, -42, 16, -16, 10)]
Point_Rainbow_threshold=[(25, 62, -128, 127, -128, 127)]

Point_Num=0                            # 铅笔顶点坐标编号
Point_In_Sensor_x=[0,0,0,0]            # 铅笔顶点x坐标
Point_In_Sensor_y=[0,0,0,0]            # 铅笔顶点y坐标

#PWM 通过定时器配置，接到 IO15 引脚
tim0 = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PWM)
Servo_1 = PWM(tim0, freq=50, duty=2.5, pin=15)
Servo_1_Duty=5.5                    # 2.5~12.5
tim1 = Timer(Timer.TIMER1, Timer.CHANNEL1, mode=Timer.MODE_PWM)
Servo_2 = PWM(tim1, freq=50, duty=2.5, pin=32)
Servo_2_Duty=5.5                    # 2.5~12.5

mod = 1

clock = time.clock()

#-液晶屏初始化-#
def lcd_init():
    lcd.init(freq=20000000)             # LCD初始化
    lcd.clear()
    lcd.rotation(2)                     # LCD翻转
lcd_init()

#-摄像头初始化-#
def sensor_init():
    sensor.reset()                      # Reset and initialize the sensor.
    sensor.run(0)                       # run automatically
    sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565
    sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
    sensor.skip_frames(time = 2000)     # Wait for settings take effect.
    sensor.set_hmirror(0)
    sensor.set_vflip(0)                     # 摄像头翻转
    sensor.set_brightness(-2)               # 亮度
    sensor.set_contrast(3)                  # 对比度
    sensor.set_gainceiling(2)               # 增益上限
    sensor.set_auto_gain(False,gain_db=-2)  # 增益
sensor_init()

#-舵机运行程序-#
def Servo_Proc():
    global Servo_1_Duty,Servo_2_Duty
    Servo_1.duty(Servo_1_Duty)
    Servo_2.duty(Servo_2_Duty)

#-找点-#
def find_point():
    global loop,Point_In_Sensor_X,Point_In_Sensor_y,Key_Down,Point_Num,key_set_slow_down
    sensor.reset()                      # Reset and initialize the sensor.
    sensor.run(0)                       # run automatically
    sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565
    sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
    sensor.skip_frames(time = 2000)     # Wait for settings take effect.
    sensor.set_hmirror(0)
    sensor.set_vflip(0)                     # 摄像头翻转
    sensor.set_brightness(-3)               # 亮度
    sensor.set_contrast(3)                  # 对比度
    sensor.set_gainceiling(2)               # 增益上限
    sensor.set_auto_gain(False,gain_db=-2)  # 增益
    loop=True
    while mod==1:
        img = sensor.snapshot().lens_corr(strength = 1.9, zoom = 1.0)         # Take a picture and return the image.
        rainbow_point_x=rainbow_point_y=0
        img=img.to_rainbow()
        rainbow_point = img.find_blobs(Point_Rainbow_threshold,x_stride=1,y_stride=1,pixels_threshold=1,area_threshold=1)
        if rainbow_point:
            for r in rainbow_point:
                if r[4]<=15:
                    rainbow_point_x=r[5]
                    rainbow_point_y=r[6]
                    tmp=img.draw_cross(rainbow_point_x,rainbow_point_y,color=(139,117,0),size=3,thickness=2)
                    #print(r)
        #串口通信
        string_x=(str)(rainbow_point_x)
        string_y=(str)(rainbow_point_y)
        img.draw_string(1,1,'Point:'+'('+string_x+','+string_y+')',color=(139,117,0),x_spacing=1)
        text=uart.read()                # 读取数据
        if text:                        # 如果读取到了数据
            uart_read_data = text.decode('utf-8')
            print('uart_read:'+uart_read_data) #REPL打印
            if uart_read_data=='point':
                uart.write(string_x+','+string_y)
        #较位
        if Key_Down==10:
            Point_In_Sensor_x[Point_Num]=rainbow_point_x
            Point_In_Sensor_y[Point_Num]=rainbow_point_y
            print(Point_In_Sensor_x)
            print(Point_In_Sensor_y)
            print('Point_Num:'+(str)(Point_Num))
            Key_Down=0
        if Key_Down==11:
            Point_Num=Point_Num+1
            if Point_Num==4:
                Point_Num=0
            Key_Down=0
        img.draw_string(0,12,'Compile Point '+(str)(Point_Num)+' :',color=(139,117,0),x_spacing=1)
        x_show=(str)(Point_In_Sensor_x)
        img.draw_string(0,24,'x:'+x_show,color=(139,117,0),x_spacing=1)
        y_show=(str)(Point_In_Sensor_y)
        img.draw_string(0,36,'y:'+y_show,color=(139,117,0),x_spacing=1)
        lcd.display(img)                # Display on LCD
        Servo_Proc()

def Key_Read():
    global Key_Val,Key_Down,Key_Old
    Key_Val=0
    if Key_IO6.value()==0:      Key_Val=6
    if Key_IO7.value()==0:      Key_Val=7
    if Key_IO8.value()==0:      Key_Val=8
    if Key_IO9.value()==0:      Key_Val=9
    if Key_IO10.value()==0:     Key_Val=10
    if Key_IO11.value()==0:     Key_Val=11
    if KEY.value()==0:          Key_Val=1
    Key_Down=Key_Val&(Key_Val^Key_Down)
    Key_Old=Key_Val
    if Key_Down!=0:
        print(Key_Down)

def Key_Proc():
    global Key_Down,Servo_1_Duty,Servo_2_Duty,mod
    if Key_Down==1:
        mod=mod+1
        if mod==3: mod=0
        print(mod)
    if Key_Down==6: Servo_1_Duty+=0.5
    if Key_Down==7: Servo_1_Duty-=0.5
    if Key_Down==8: Servo_2_Duty+=0.5
    if Key_Down==9: Servo_2_Duty-=0.5
    if Servo_1_Duty<=2.5: Servo_1_Duty=2.5
    if Servo_2_Duty<=2.5: Servo_2_Duty=2.5
    if Servo_1_Duty>=12.5: Servo_1_Duty=12.5
    if Servo_2_Duty>=12.5: Servo_2_Duty=12.5
    Key_Read()

def fun(tim):
    global key_set_slow_down
    key_set_slow_down=key_set_slow_down+1
    if key_set_slow_down==10:
        key_set_slow_down=0
        Key_Proc()

tim = Timer(Timer.TIMER2, Timer.CHANNEL2, mode=Timer.MODE_PERIODIC,period=1, callback=fun)

def find_black_rect():
    global loop
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QQVGA)
    sensor.skip_frames(time = 2000)
    sensor.set_vflip(1)
    loop=True
    get=[0,0,0,0,0,0,0,0]
    while mod==2:
        img = sensor.snapshot().lens_corr(strength = 1.9, zoom = 1.0)         # Take a picture and return the image.
        img.midpoint(1, bias=0.9, threshold=True, offset=5, invert=True)    #凸显黑线
        for r in img.find_rects(threshold = 60000):
            if(r[0]>30 and r[0]<90 and r[1]>30 and r[0]<90):
                img.draw_rectangle(r.rect(), color = (255, 0, 0))
                f=0
                for p in r.corners():
                    img.draw_circle(p[0], p[1], 5, color = (0, 255, 0))
                    get[f]=p[0]
                    get[f+1]=p[1]
                    f=f+2
                    #print(frame)
                #print(frame)
        text=uart.read()                # 读取数据
        if text:                        # 如果读取到了数据
            uart_read_data = text.decode('utf-8')
            print('uart_read:'+uart_read_data) #REPL打印
            if uart_read_data=='frame4':
                str_0=(str)(get[0])
                str_1=(str)(get[1])
                uart.write(str_0+','+str_1)
            if uart_read_data=='frame1':
                str_0=(str)(get[2])
                str_1=(str)(get[3])
                uart.write(str_0+','+str_1)
            if uart_read_data=='frame2':
                str_0=(str)(get[4])
                str_1=(str)(get[5])
                uart.write(str_0+','+str_1)
            if uart_read_data=='frame3':
                str_0=(str)(get[6])
                str_1=(str)(get[7])
                uart.write(str_0+','+str_1)
        lcd.display(img)                # Display on LCD

def normal_film():
    global loop
    sensor.reset()                      # Reset and initialize the sensor.
    sensor.run(0)                       # run automatically
    sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565
    sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
    sensor.skip_frames(time = 2000)     # Wait for settings take effect.
    sensor.set_hmirror(True)
    sensor.set_vflip(2)                 # 摄像头翻转
    sensor.set_brightness(2)            # 亮度
    loop=True
    while(loop):
        img = sensor.snapshot().lens_corr(strength = 1.9, zoom = 1.0)         # Take a picture and return the image.
        lcd.display(img)                # Display on LCD

print('K210 ON')
while(True):
    clock.tick()                    # Update the FPS clock.
    if mod==0:
        normal_film()
    if mod==1:
        print('mod1')
        find_point()
    if mod==2:
        print('mod2')
        find_black_rect()

