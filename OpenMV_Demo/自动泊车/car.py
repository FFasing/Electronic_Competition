import sensor, image, time, utime, ustruct, pyb
from pyb import UART

# OpenMV4 H7 Plus, OpenMV4 H7, OpenMV3 M7, OpenMV2 M4 的UART(3)是P4-TX P5-RX
uart = UART(3,115200)
uart.init(115200, bits=8, parity=None, stop=1)

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.set_hmirror(True )                               # 水平镜像
sensor.set_vflip(True)                                  # 摄像头翻转
sensor.set_brightness(3)                                # 亮度
sensor.set_contrast(-3)                                 # 对比度

mod = 0

uart_tx=0

clock = time.clock()

black_invert=(0, 21, -18, -1, -7, 14)
line_color=(50,255,100)
line_color2=(250,55,100)

#倒车入库
#走直线    p[6]-k(25~35)
str_fol_lef = [160,0,10,240]
str_fol_rig = [175,0,40,240]
#准备入库
stop_hig1 = [0,60,320,60]
stop_low1 = [0,80,320,80]
stop_hig2 = [0,140,320,140]
stop_low2 = [0,170,320,170]
#入库+停车
str_ruku_lef = [170,0,40,240]
str_ruku_rig = [180,0,75,240]
stop_ruku_hig = [0,155,320,155]
stop_ruku_low = [0,170,320,170]
stop_flag_num = 0

def ruku_star_stop(img):
    global uart_tx,mod,stop_flag_num
    black_line = img.find_lines(roi=(0,0,str_ruku_rig[0],240))
    if black_line:
        for b in black_line:        #k(25,35)
            print(b)
            if b[4] > 150:
                if b[6]>=20 and b[6]<=30:
                    stop_flag_num=stop_flag_num+1
                    if stop_flag_num == 4:
                        dif_val = 0
                        uart_tx = 'STOP2'
                        mod=3
                    img.draw_line(b[0],b[1],b[2],b[3],color=(255,255,0),thickness=3)
    img.draw_line(str_ruku_lef,color=line_color2,thickness=2)
    img.draw_line(str_ruku_rig,color=line_color2,thickness=2)
    img.draw_line(stop_ruku_hig,color=line_color2,thickness=2)
    img.draw_line(stop_ruku_low,color=line_color2,thickness=2)

def stop(img):
    global uart_tx,mod
    L=0
    H=0
    black_line = img.find_lines(roi=(0,stop_hig1[1],320,stop_low1[1]-stop_hig1[1])) #上线
    if black_line:
        for b in black_line:
            if b[4] > 200:
#                img.draw_line(b[0],b[1],b[2],b[3],color=(255,255,0),thickness=1)
                H=1
    black_line = img.find_lines(roi=(0,stop_hig2[1],320,stop_low2[1]-stop_hig2[1])) #下线
    if black_line:
        for b in black_line:
            if b[4] > 200:
#                img.draw_line(b[0],b[1],b[2],b[3],color=(255,255,0),thickness=1)
                L=1
    if H==1 and L==1:
        uart_tx = 'STOP1'
        print('STOP1')
        uart.write(uart_tx)
        mod=1
    img.draw_line(stop_hig1,color=line_color,thickness=2)
    img.draw_line(stop_low1,color=line_color,thickness=2)
    img.draw_line(stop_hig2,color=line_color,thickness=2)
    img.draw_line(stop_low2,color=line_color,thickness=2)

def straight_follow(img):
    global uart_tx
    n=0
    black_line = img.find_lines(roi=(0,0,str_fol_lef[0],240))
    if black_line:
        for b in black_line:
                if b[4] > 180:
                    if b[6] <= 50 or b[6] >= 120:
                        dif_val = 0
                        uart_tx = '*W#'
                        if b[0] > 100:
                            if b[0] < str_fol_lef[0]-10:
                                dif_val = str_ruku_lef[0]-10-b[0]
                                uart_tx = '*L%d#1'%dif_val
                                n=1
                        if b[2] > 100:
                            if b[2] > str_fol_rig[2]:
                                dif_val = b[2]-str_fol_rig[2]
                                uart_tx = '*R%d#2'%dif_val
                                n=1
                            if b[2] < str_fol_lef[2]:
                                dif_val = str_ruku_lef[2]-b[2]
                                uart_tx = '*L%d#2'%dif_val
                                n=1
                        if n==0:
                            if b[6] < 25:
                                dif_val = 25-b[6]+10
                                uart_tx = '*L%d#3'%dif_val
                            if b[6] > 35:
                                dif_val = b[6]-35
                                uart_tx = '*R%d#3'%dif_val
                    img.draw_line(b[0],b[1],b[2],b[3],color=(255,255,0),thickness=3)
    #img.draw_line(str_fol_lef,color=line_color,thickness=2)
    #img.draw_line(str_fol_rig,color=line_color,thickness=2)

def uart_proc():
    global uart_tx
    if uart_tx:
        uart.write(uart_tx)
        print(uart_tx)
        uart_tx=0

while(True):
    clock.tick()
    img = sensor.snapshot()
#    ruku_star_stop(img)
    if mod==2:
        ruku_star_stop(img)
    if mod==0:
        stop(img)
        if uart_tx!='STOP1':
            straight_follow(img)
    if mod==1:
        pyb.delay(4000)
        mod=2
    uart_proc()
