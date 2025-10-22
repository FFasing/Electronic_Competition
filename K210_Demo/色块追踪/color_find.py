import sensor,image,time,lcd,utime
from machine import Timer,UART,PWM
from Maix import GPIO
from fpioa_manager import fm

lcd.init(freq=20000000)             # LCD初始化
lcd.clear()
lcd.rotation(3)                     # LCD翻转

sensor.reset()                      # Reset and initialize the sensor.
sensor.run(0)                       # run automatically
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565
sensor.set_framesize(sensor.QVGA)     # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
sensor.set_hmirror(0)                               # 水平镜像
sensor.set_vflip(0)                                 # 摄像头翻转
sensor.set_brightness(-3)                           # 亮度
sensor.set_contrast(3)                              # 对比度
sensor.set_saturation(3)                            # 饱和度
sensor.set_gainceiling(2)                           # 增益上限
sensor.set_auto_gain(False,gain_db=-10)             # 增益
sensor.set_auto_exposure(False,exposure=500)        # 曝光速度
sensor.set_auto_whitebal(False)                     # 白平衡
sensor.skip_frames(20)                              # 跳过帧

tim0 = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PWM)
Servo_y = PWM(tim0, freq=50, duty=7, pin=6)
tim1 = Timer(Timer.TIMER1, Timer.CHANNEL1, mode=Timer.MODE_PWM)
Servo_x = PWM(tim1, freq=50, duty=4, pin=9)

color_threshold=[(0, 100, 26, 74, 1, 124)]
Servo_y_Duty=7                    # 2.5~12.5
Servo_x_Duty=4                    # 2.5~12.5

Point_Rainbow_threshold=[(25, 62, -128, 127, -128, 127)]
Point_red_threshold=[(100, 200, -128, 127, -128, 127)]

while True:
    img = sensor.snapshot().lens_corr(strength = 1.9, zoom = 1.0)
    #color_blob = img.find_blobs(color_threshold,x_stride=10,y_stride=10,pixels_threshold=800)
    color_blob = img.find_blobs(Point_red_threshold,x_stride=1,y_stride=1,pixels_threshold=1,area_threshold=1)
    #img=img.to_rainbow()
    #color_blob = img.find_blobs(Point_Rainbow_threshold,x_stride=1,y_stride=1,pixels_threshold=10,area_threshold=1)
    x_f=130
    y_f=150
    x_num=0
    y_num=0
    if color_blob:
         for c in color_blob:
            if c[4]<50:
                tmp=img.draw_cross(c[5],c[6],color=(139,117,0),size=3,thickness=2)
                tmp=img.draw_rectangle(c[0:4],color=(139,117,0),size=3,thickness=2)
                print(c)
                if x_f>c[5]: x_num=x_f-c[5]
                else: x_num=c[5]-x_f
                if y_f>c[5]: y_num=y_f-c[5]
                else: y_num=c[5]-y_f
                x_num=x_num/30
                y_num=y_num/20
                if c[5]<x_f+5: Servo_y_Duty=Servo_y_Duty-x_num*0.05
                if c[5]>x_f-5: Servo_y_Duty=Servo_y_Duty+x_num*0.05
                if c[6]<y_f+5: Servo_x_Duty=Servo_x_Duty-y_num*0.05
                if c[6]>y_f-5: Servo_x_Duty=Servo_x_Duty+y_num*0.05
                print(Servo_x_Duty)
                print(Servo_y_Duty)
    Servo_y.duty(Servo_y_Duty)
    Servo_x.duty(Servo_x_Duty)
