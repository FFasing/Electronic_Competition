import sensor, image, lcd, time
import KPU as kpu
from machine import UART
import gc, sys
from fpioa_manager import fm


fm.register(6, fm.fpioa.UART2_TX, force=True)
fm.register(7, fm.fpioa.UART2_RX, force=True)
uart2 = UART(UART.UART2, 115200)
mod = 0

input_size = (224, 224)

#139442
#labels = ['8', '1', '2', '3', '4', '5', '6', '7']
#anchors = [2.31, 3.06, 0.81, 1.38, 3.19, 3.94, 1.25, 1.84, 1.69, 2.34]

#139604
labels = ['2', '3', '4', '5', '6', '7', '8', '1']
anchors = [2.62, 3.66, 1.78, 2.59, 1.31, 2.03, 3.69, 4.97, 1.0, 1.56]
color = (225,255,0)

target = 0
write_flag = 0
car_run = 0 #0-stop 1-w 2-s 3-a 4-d

left_num = 0
right_num = 0
left_percent = 0
right_percent = 0

left_T_num = 0
right_T_num = 0
left_T_percent = 0
right_T_percent = 0

def lcd_show_except(e):
    import uio
    err_str = uio.StringIO()
    sys.print_exception(e, err_str)
    err_str = err_str.getvalue()
    img = image.Image(size=input_size)
    img.draw_string(0, 10, err_str, scale=1, color=(0xff,0x00,0x00))
    lcd.display(img)

class Comm:
    def __init__(self, uart):
        self.uart = uart

    def send_detect_result(self, objects, labels):
        msg = ""
        for obj in objects:
            pos = obj.rect()
            p = obj.value()
            idx = obj.classid()
            label = labels[idx]
            msg += "{}:{}:{}:{}:{}:{:.2f}:{}, ".format(pos[0], pos[1], pos[2], pos[3], idx, p, label)
        if msg:
            msg = msg[:-2] + "\n"
        self.uart.write(msg.encode())

def draw_proc(img):
    global left_num,right_num,left_percent,right_percent,mod,target,write_flag
    global left_T_num,right_T_num,left_T_percent,right_T_percent
    img = img.draw_line(115,0,115,240,color=color,thickness=3)
    img.draw_string(5,175, "run: %s" %(str)(car_run), scale=2, color=color)
    img.draw_string(125,195, "traget: %s" %(str)(target), scale=2, color=color)
    img.draw_string(125,175, "w_fg: %s" %(str)(write_flag), scale=2, color=color)
    img.draw_string(5,195, "mod: %s" %(str)(mod), scale=2, color=color)
    #img = img.draw_string(20,200,"x:0~110",color=color,scale=2)
    #img = img.draw_string(130,200,"x:110~220",color=color,scale=2)
    if mod==3:
        img.draw_string(0,0, "t_n: %s,%.1f" %((str)(left_T_num),left_T_percent), scale=2, color=color)
        img.draw_string(125,0, "t_n: %s,%.1f" %((str)(right_T_num),right_T_percent), scale=2, color=color)
    if mod==2 or mod==4:
        img.draw_string(0,0, "l_n: %s,%.1f" %((str)(left_num),left_percent), scale=2, color=color)
        img.draw_string(125,0, "r_n: %s,%.1f" %((str)(right_num),right_percent), scale=2, color=color)

def init_uart():
    fm.register(10, fm.fpioa.UART1_TX, force=True)
    fm.register(11, fm.fpioa.UART1_RX, force=True)
    uart = UART(UART.UART1, 115200)
    return uart

def uart_read_proc():
    global left_num,right_num,left_percent,right_percent,mod,target,write_flag
    global left_T_num,right_T_num,left_T_percent,right_T_percent,car_run
    uart_read = 0
    text=uart2.read()                   # 读取数据
    if text:                            # 如果读取到了数据
        uart_read = text.decode('utf-8')
        print(uart_read)                # REPL打印
        if uart_read == 'm0':
            mod=0
            write_flag=1
        if uart_read == 'm1':
            mod=1
            write_flag=1
        if uart_read == 'm2':
            mod=2
            left_num=right_num=left_percent=right_percent=0
            write_flag=1
        if uart_read == 'm3':
            mod=3
            left_T_num=right_T_num=left_T_percent=right_T_percent=0
            write_flag=1
        if uart_read == 'm4':
            mod=4
            left_num=right_num=left_percent=right_percent=0
            write_flag=1
        if uart_read == 'm5':
            mod=5
            write_flag=1
        if uart_read == 'ok':
            write_flag=0
            car_run=0

def car_run_proc(car_run,write_flag):#0-stop 1-w 2-s 3-a 4-d
    if car_run == 1:
        uart2.write('#W')
        print('#W')
    if car_run == 2:
        uart2.write('#S')
        print('#S')
    if car_run == 3:
        uart2.write('#L')
        print('#L')
    if car_run == 4:
        uart2.write('#R')
        print('#R')

def uart_write_proc(mod):
    global write_flag,right_percent,car_run
    uart_read_proc()
    if write_flag == 1:
        if mod==1: car_run=1
        if mod==2:
            if target==1: car_run=3
            if target==2: car_run=4
            if target!=1 and target!=2:
                car_run=1
        if mod==3:
            if left_num==target: car_run=3
            if right_num==target: car_run=4
            if left_num!=target and right_num!=target:
                car_run=1
        if mod==4:
            if left_num==target or right_num==target: car_run=4
            if left_num!=target and right_num!=target: car_run=3
        if mod==5:
            if left_num==target: car_run=3
            if right_num==target: car_run=4
        car_run_proc(car_run,write_flag)


def main(anchors, labels = None, model_addr="/sd/m.kmodel", sensor_window=input_size, lcd_rotation=0, sensor_hmirror=False, sensor_vflip=False):
    global left_num,right_num,left_percent,right_percent,mod,target
    global left_T_num,right_T_num,left_T_percent,right_T_percent
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.set_windowing(sensor_window)
    sensor.set_hmirror(sensor_hmirror)
    sensor.set_vflip(sensor_vflip)
    sensor.set_brightness(0)                            # 亮度
    sensor.set_contrast(0)                              # 对比度
    sensor.set_saturation(0)                            # 饱和度
    #sensor.set_auto_exposure(False,exposure=500)        # 曝光速度
    sensor.set_auto_whitebal(False)                     # 白平衡
    sensor.skip_frames(20)                              # 跳过帧
    sensor.set_windowing(sensor_window)                 # 放大
    sensor.run(1)

    lcd.init(type=1)
    lcd.rotation(2)
    lcd.clear(lcd.WHITE)

    if not labels:
        with open('labels.txt','r') as f:
            exec(f.read())
    if not labels:
        print("no labels.txt")
        img = image.Image(size=(320, 240))
        img.draw_string(90, 110, "no labels.txt", color=(255, 0, 0), scale=2)
        lcd.display(img)
        return 1
    try:
        img = image.Image("startup.jpg")
        lcd.display(img)
    except Exception:
        img = image.Image(size=(320, 240))
        img.draw_string(90, 110, "loading model...", color=(255, 255, 255), scale=2)
        lcd.display(img)

    uart = init_uart()
    comm = Comm(uart)

    try:
        task = None
        task = kpu.load(model_addr)
        kpu.init_yolo2(task, 0.7, 0.3, 5, anchors) # threshold:[0,1], nms_value: [0, 1]
        while(True):
            img = sensor.snapshot()#.lens_corr(strength = 1.3, zoom = 1.0)
            t = time.ticks_ms()
            objects = kpu.run_yolo2(task, img)
            t = time.ticks_ms() - t
            if objects:
                for obj in objects:
                    pos = obj.rect()
                    img.draw_rectangle(pos)
                    img.draw_string(pos[0], pos[1], "%s : %.2f" %(labels[obj.classid()], obj.value()), scale=2, color=(255, 0, 0))
                    if mod==0:
                        t_n = labels[obj.classid()]
                        target = t_n
                    if mod==2 or mod==4:
                        if pos[0]+pos[2]/2 <110:
                            l_num = labels[obj.classid()]
                            if left_num==0: left_num = l_num
                            if left_num!=right_num:
                                if left_percent < obj.value():
                                    left_percent = obj.value()
                                    left_num = l_num
                        elif pos[0]+pos[2]/2 >=110:
                            r_num = labels[obj.classid()]
                            if right_num==0: right_num = r_num
                            if left_num!=right_num:
                                if right_percent < obj.value():
                                    right_percent = obj.value()
                                    right_num = r_num
                    if mod==3:
                     if pos[0]+pos[2]/2 <110:
                         l_num = labels[obj.classid()]
                         if left_T_num==0: left_T_num = l_num
                         if left_T_num!=left_T_percent:
                             if left_T_percent < obj.value():
                                 left_T_percent = obj.value()
                                 left_T_num = l_num
                     elif pos[0]+pos[2]/2 >=110:
                         r_num = labels[obj.classid()]
                         if right_T_num==0: right_T_num = r_num
                         if left_num!=right_T_num:
                             if right_T_percent < obj.value():
                                 right_T_percent = obj.value()
                                 right_T_num = r_num
                comm.send_detect_result(objects, labels)
            draw_proc(img)
            uart_read_proc()
            uart_write_proc(mod)
            lcd.display(img)
    except Exception as e:
        raise e
    finally:
        if not task is None:
            kpu.deinit(task)


if __name__ == "__main__":
    try:
        #main(anchors = anchors, labels=labels, model_addr=0x300000, lcd_rotation=0)
        #main(anchors = anchors, labels=labels, model_addr="/sd/model-139442.kmodel")
        main(anchors = anchors, labels=labels, model_addr="/sd/model-139604.kmodel")
    except Exception as e:
        sys.print_exception(e)
        lcd_show_except(e)
    finally:
        gc.collect()
