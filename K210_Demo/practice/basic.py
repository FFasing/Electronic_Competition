import sensor, image, time, lcd
from machine import Timer

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
