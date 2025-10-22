import sensor,image,time,lcd,utime
from machine import Timer,UART
from Maix import GPIO
from fpioa_manager import fm
fm.register(6, fm.fpioa.UART1_RX, force=True)
fm.register(7, fm.fpioa.UART1_TX, force=True)
fm.register(12, fm.fpioa.GPIO0)
fm.register(16, fm.fpioa.GPIOHS0)
fm.register(10, fm.fpioa.GPIOHS10)
fm.register(11, fm.fpioa.GPIOHS11)
LED_B   =   GPIO(GPIO.GPIO0, GPIO.OUT,value=1)
KEY	 =   GPIO(GPIO.GPIOHS0, GPIO.IN, GPIO.PULL_UP)
Key_IO10=   GPIO(GPIO.GPIOHS10, GPIO.IN, GPIO.PULL_UP)
Key_IO11=   GPIO(GPIO.GPIOHS11, GPIO.IN, GPIO.PULL_UP)
uart	=   UART(UART.UART1, 115200)
loop = False
mod = 1
KEY_State = 1
Key_IO10_State = 0
Key_IO11_State = 0
rect_threshold=[(0, 31, -42, 16, -16, 10)]
Point_Rainbow_threshold=[(25, 62, -128, 127, -128, 127)]
Point_Num=0
Point_In_Sensor_x=[0,0,0,0]
Point_In_Sensor_y=[0,0,0,0]
clock = time.clock()
def lcd_init():
    lcd.init(freq=20000000)
    lcd.clear()
    lcd.rotation(2)
lcd_init()
def sensor_init():
    sensor.reset()
    sensor.run(0)
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(time = 2000)
    sensor.set_hmirror(0)
    sensor.set_vflip(0)
    sensor.set_brightness(-2)
    sensor.set_contrast(3)
    sensor.set_gainceiling(2)
    sensor.set_auto_gain(False,gain_db=-2)
sensor_init()
def find_point():
    global loop,Point_In_Sensor_X,Point_In_Sensor_y,Key_IO10_State,Key_IO11_State,Point_Num
    sensor.reset()
    sensor.run(0)
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(time = 2000)
    sensor.set_hmirror(0)
    sensor.set_vflip(0)
    sensor.set_brightness(-3)
    sensor.set_contrast(3)
    sensor.set_gainceiling(2)
    sensor.set_auto_gain(False,gain_db=-2)
    loop=True
    while(loop):
        img = sensor.snapshot()
        rainbow_point_x=rainbow_point_y=0
        img=img.to_rainbow()
        rainbow_point = img.find_blobs(Point_Rainbow_threshold,x_stride=1,y_stride=1,pixels_threshold=1,area_threshold=1)
        if rainbow_point:
            for r in rainbow_point:
                if r[4]<=15:
                    rainbow_point_x=r[5]
                    rainbow_point_y=r[6]
                    tmp=img.draw_cross(rainbow_point_x,rainbow_point_y,color=(139,117,0),size=3,thickness=2)
        string_x=(str)(rainbow_point_x)
        string_y=(str)(rainbow_point_y)
        img.draw_string(1,1,'Point:'+'('+string_x+','+string_y+')',color=(139,117,0),x_spacing=1)
        text=uart.read()
        #if text:
            #uart_read_data = text.decode('utf-8')
            #print('uart_read:'+uart_read_data) #REPL打印
            #if uart_read_data=='point':
                #uart.write(string_x+','+string_y)
        if Key_IO10_State:
            Key_IO10_State=0
            Point_In_Sensor_x[Point_Num]=rainbow_point_x
            Point_In_Sensor_y[Point_Num]=rainbow_point_y
            print(Point_In_Sensor_x)
            print(Point_In_Sensor_y)
            print('Point_Num:'+(str)(Point_Num))
            print('OK')
        if Key_IO11_State:
            Key_IO11_State=0
            Point_Num=Point_Num+1
            if Point_Num==4:	Point_Num=0
        img.draw_string(0,12,'Compile Point '+(str)(Point_Num)+' :',color=(139,117,0),x_spacing=1)
        x_show=(str)(Point_In_Sensor_x)
        img.draw_string(0,24,'x:'+x_show,color=(139,117,0),x_spacing=1)
        y_show=(str)(Point_In_Sensor_y)
        img.draw_string(0,36,'y:'+y_show,color=(139,117,0),x_spacing=1)
        lcd.display(img)
def fun(Key_IO10):
    global Key_IO10_State,Key_IO11_State,Point_Num
    utime.sleep_ms(50)
    if Key_IO10.value()==0:
        Key_IO10_State = 1
        print('Key_IO10 is down')
Key_IO10.irq(fun, GPIO.IRQ_FALLING)
def fun(Key_IO11):
    global Key_IO10_State,Key_IO11_State,Point_Num
    utime.sleep_ms(50)
    if Key_IO11.value()==0:
        Key_IO11_State = 1
Key_IO11.irq(fun, GPIO.IRQ_FALLING)
def find_black_rect():
    global loop
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QQVGA)
    sensor.skip_frames(time = 2000)
    sensor.set_vflip(1)
    loop=True
    get=[0,0,0,0,0,0,0,0]
    while(loop):
        img = sensor.snapshot()
        img.midpoint(1, bias=0.9, threshold=True, offset=5, invert=True)
        for r in img.find_rects(threshold = 60000):
            if(r[0]>30 and r[0]<90 and r[1]>30 and r[0]<90):
                img.draw_rectangle(r.rect(), color = (255, 0, 0))
                f=0
                for p in r.corners():
                    img.draw_circle(p[0], p[1], 5, color = (0, 255, 0))
                    get[f]=p[0]
                    get[f+1]=p[1]
                    f=f+2
        text=uart.read()
        if text:
            uart_read_data = text.decode('utf-8')
            print('uart_read:'+uart_read_data)
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
        lcd.display(img)
def normal_film():
    global loop
    sensor.reset()
    sensor.run(0)
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(time = 2000)
    sensor.set_hmirror(True)
    sensor.set_vflip(2)
    sensor.set_brightness(2)
    loop=True
    while(loop):
        img = sensor.snapshot()
        lcd.display(img)
print('K210 ON')
while(True):
    clock.tick()
    if mod==0:
        normal_film()
    if mod==1:
        find_point()
    if mod==2:
        find_black_rect()
def fun(KEY):
    global KEY_State,mod,loop
    utime.sleep_ms(10)
    if KEY.value()==0:
        KEY_State = not KEY_State
        mod=mod+1
        if mod==3:
            mod=0
        loop=False
        print(mod)
KEY.irq(fun, GPIO.IRQ_FALLING)
