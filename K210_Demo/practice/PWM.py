import sensor,image,time,lcd,utime
from machine import Timer,UART,PWM
from Maix import GPIO
from fpioa_manager import fm

fm.register(10, fm.fpioa.GPIO0)
fm.register(11, fm.fpioa.GPIO1)
fm.register(6 , fm.fpioa.GPIO2)
fm.register(7 , fm.fpioa.GPIO3)
fm.register(8 , fm.fpioa.GPIO4)
fm.register(9 , fm.fpioa.GPIO5)
Key_IO10    =   GPIO(GPIO.GPIO0, GPIO.IN, GPIO.PULL_UP)
Key_IO11    =   GPIO(GPIO.GPIO1, GPIO.IN, GPIO.PULL_UP)
Key_IO6     =   GPIO(GPIO.GPIO2, GPIO.IN, GPIO.PULL_UP)
Key_IO7     =   GPIO(GPIO.GPIO3, GPIO.IN, GPIO.PULL_UP)
Key_IO8     =   GPIO(GPIO.GPIO4, GPIO.IN, GPIO.PULL_UP)
Key_IO9     =   GPIO(GPIO.GPIO5, GPIO.IN, GPIO.PULL_UP)

#PWM 通过定时器配置，接到 IO15 引脚
tim0 = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PWM)
Servo_1 = PWM(tim0, freq=50, duty=2.5, pin=15)
Servo_1_Duty=5.5                    # 2.5~12.5
tim1 = Timer(Timer.TIMER1, Timer.CHANNEL1, mode=Timer.MODE_PWM)
Servo_2 = PWM(tim1, freq=50, duty=2.5, pin=32)
Servo_2_Duty=5.5                    # 2.5~12.5

Key_Val=0
Key_Down=0
Key_Old=0

def Key_Read():
    global Key_Val,Key_Down,Key_Old
    Key_Val=0
    if Key_IO6.value()==0:
        Key_Val=6
    if Key_IO7.value()==0:
        Key_Val=7
    if Key_IO8.value()==0:
        Key_Val=8
    if Key_IO9.value()==0:
        Key_Val=9
    if Key_IO10.value()==0:
        Key_Val=10
    if Key_IO11.value()==0:
        Key_Val=11
    Key_Down=Key_Val&(Key_Val^Key_Down)
    Key_Old=Key_Val
    if Key_Down!=0: print(Key_Down)

def Key_Proc():
    global Key_Down,Servo_1_Duty,Servo_2_Duty
    Key_Read()
    if Key_Down==6: Servo_1_Duty+=0.5
    if Key_Down==7: Servo_1_Duty-=0.5
    if Key_Down==8: Servo_2_Duty+=0.5
    if Key_Down==9: Servo_2_Duty-=0.5
    if Servo_1_Duty<=2.5: Servo_1_Duty=2.5
    if Servo_2_Duty<=2.5: Servo_2_Duty=2.5
    if Servo_1_Duty>=12.5: Servo_1_Duty=12.5
    if Servo_2_Duty>=12.5: Servo_2_Duty=12.5
def fun(tim):
    Key_Proc()
tim = Timer(Timer.TIMER2, Timer.CHANNEL2, mode=Timer.MODE_PERIODIC,period=20, callback=fun)
print('K210 IS OPEN')


while True:
    Servo_1.duty(Servo_1_Duty)
    Servo_2.duty(Servo_2_Duty)

