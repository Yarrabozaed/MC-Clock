from machine import Pin, ADC, PWM, RTC, ADC, I2C
import utime
import neopixel
import time
import ssd1306
import uasyncio as asyncio
import sys


xAxis = ADC(Pin(27))
yAxis = ADC(Pin(26))
joystick_button = Pin(16,Pin.IN, Pin.PULL_UP)

buzzer = PWM(Pin(20))


led_len = 76
#was 10
np = neopixel.NeoPixel(machine.Pin(10), led_len, bpp=3)


global time_dis
global led_status

led_status = "na"

#date variables
rtc=RTC()
rtc.datetime((2017, 8, 23, 2, 12, 48, 0, 0))
#screen variables
i2c=machine.SoftI2C(sda=Pin(4), scl=Pin(5))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

alarm_single_led = Pin(7, Pin.OUT) #initialize digital pin as an output for led
off_button = Pin(10, Pin.IN,Pin.PULL_DOWN) #initialize digital pin 10 as an input

adc = ADC(Pin(26))

motor_pin = machine.Pin(22, machine.Pin.OUT)
    
"""
while True:
    duty = 0; #duty range between  0 and 65535
    value = adc.read_u16() #reads in pot value between 0 and 1023
    if (value < 100):
        duty = 6553
    elif (value < 200):
        duty = 13106
    elif (value < 300):
        duty = 19659
    elif (value < 400):
        duty = 26212
    elif (value < 500):
        duty = 32765
    elif (value < 600):
        duty = 39318
    elif (value < 700):
        duty = 45871
    elif (value < 800):
        duty = 52424
    elif (value < 900):
        duty = 58977
    elif (value < 1023):
        duty = 65530
    playsong(song, duty)
"""

def turn_motor_on():
    motor_pin.on()

def turn_motor_off():
    motor_pin.off()

def display(output):
    print(output)
    oled.fill(0)
    oled.text(output, 35, 30)
    oled.show()

# 1 - 12, 0 and 59
#hours, minutes, am pm (0 for am, 1 for pm)

def print_time(t):
    am_or_pm = ""
    if t[2] == 0:
        am_or_pm = "am"
    else:
        am_or_pm = "pm"
    
    output = ""
    if t[0] < 10:
        output = output + "0" + str(t[0])
    else:
        output = output + str(t[0])
    
    if t[1] < 10:
        output = output + ":0" + str(t[1])
    else:
        output = output + ":" + str(t[1])
    
    output = output + am_or_pm
    return output
    
    
    #print("%s:%s %s" % (time[0], time[1], am_or_pm) )

def time_setter():
    global time_dis
    time_dis = [1,0,0]

    digit_position = 0
    
    print("entering setup mode")
    utime.sleep(1)
    while True:
        xValue = xAxis.read_u16()
        yValue = yAxis.read_u16()
        joystick_buttonValue = joystick_button.value()

        xStatus = "middle"
        yStatus = "middle"
        joystick_buttonStatus = "not pressed"
        
        if xValue <= 600:
            xStatus = "left"
            
            if digit_position - 1 >= 0:
                digit_position = digit_position - 1
            else:
                digit_position = 2
                
            if digit_position == 0:
                display("Hours")
                utime.sleep(2)
            elif digit_position == 1:
                display("Minutes")
                utime.sleep(2)
            else:
                display("AM/PM")
                utime.sleep(2)
    
            print(digit_position)
            
        elif xValue >= 60000:
            xStatus = "right"
            
            if digit_position + 1 <= 2:
                digit_position = digit_position + 1
            else:
                digit_position = 0
            
            
            if digit_position == 0:
                display("Hours")
                utime.sleep(2)
            elif digit_position == 1:
                display("Minutes")
                utime.sleep(2)
            else:
                display("AM/PM")
                utime.sleep(2)
            
            print(digit_position)
            
        if yValue <= 600:
            yStatus = "up"
            
            #change hours
            if digit_position == 0:
                if time_dis[digit_position] + 1 <= 12:
                    time_dis[digit_position] = time_dis[digit_position] + 1
                    if time_dis[digit_position] == 12:
                        if time_dis[2] == 0:
                            time_dis[2] = 1
                        else:
                            time_dis[2] = 0
                else:
                    time_dis[digit_position] = 1
            elif digit_position == 1:
                if time_dis[digit_position] + 1 <= 59:
                    time_dis[digit_position] = time_dis[digit_position] + 1
                else:
                    time_dis[digit_position] = 0
            else:
                if time_dis[2] == 0:
                    time_dis[2] = 1
                else:
                    time_dis[2] = 0
            
            display(print_time(time_dis))
            
        elif yValue >= 60000:
            yStatus = "down"
            
            #change hours
            if digit_position == 0:
                if time_dis[digit_position] - 1 >= 1:
                    time_dis[digit_position] = time_dis[digit_position] - 1
                    if time_dis[digit_position] == 12:
                        if time_dis[2] == 0:
                            time_dis[2] = 1
                        else:
                            time_dis[2] = 0
                else:
                    time_dis[digit_position] = 12
            elif digit_position == 1:
                if time_dis[digit_position] - 1 >= 0:
                    time_dis[digit_position] = time_dis[digit_position] - 1
                else:
                    time_dis[digit_position] = 59
            else:
                if time_dis[2] == 0:
                    time_dis[2] = 1
                else:
                    time_dis[2] = 0
            display(print_time(time_dis))
            
        if joystick_buttonValue == 0:
            display("Exiting...")
            utime.sleep(2)
            
            print("exiting setup mode")
            
            return
        
        utime.sleep(0.25)

def clock_updater(current):
    if current[1] == 59:
        current[1] = 0
        if current[0] == 12 and current[2] == 1:
            current[0] = 1
            current[2] = 1 - current[2]
            time_led_check(current)
        elif current[0] == 12:
            current[0] = 1
            time_led_check(current)
        else:
            current[0] = current[0] + 1
            time_led_check(current)
    else:
        current[1] = current[1] + 1
        time_led_check(current)
        
 
async def buzzer_start():
    tones = {
    "C4": 262,
    "D4": 294,
    "E4": 330,
    "F4": 349,
    "G4": 392,
    "A4": 440,
    "B4": 494,
    "C5": 523,
    "D5": 587,
    "E5": 659,
    "F5": 698,
    "G5": 784,
    "A5": 880,
    "B5": 988
    }

    
    song = ["A4","F4","D5","C5","P","A4","F4","P","D4","G4","P","P","P",
"F4","G4","A4","D5","P","E5","F5","C5","P","P","P","P","P","P","P"]
    while True:
        for i in range(len(song)):
            if song[i] == "P":
                buzzer.duty_u16(0)
            else:
                buzzer.duty_u16(1000)
                buzzer.freq(tones[song[i]])
            
            await asyncio.sleep(0.5)  # Adjust the sleep duration as needed
            
        buzzer.duty_u16(0)
        await asyncio.sleep(1)
    

def buzzer_stop():
    buzzer.duty_u16(0)

def morning_colors():
    global np
    count = 0
    net = 0
    for net in range(led_len):
        if count == 0:
            np[net] = (255,165,0)
            count = count + 1
            np.brightness = 0.001
            np.write()
        elif count == 1:
            np[net] = (255,215,0)
            count = count + 1
            np.write()
        else:
            np[net] = (255,69,0)
            count = 0
            np.write()

def night_colors():
    count = 0
    net = 0
    for net in range(led_len):
        if count == 0:
            np[net] = (0,0,128)
            count = count + 1
            np.write()
        elif count == 1:
            np[net] = (75,0,130)
            count = count + 1
            np.write()
        else:
            np[net] = (25,25,112)
            count = 0
            np.write()

def evening_colors():
    count = 0
    net = 0
    global np
    for net in range(led_len):
        if count == 0:
            np[net] = (128,0,0)
            count = count + 1
            np.brightness = 0
            np.write()
        elif count == 1:
            np[net] = (75,0,130)
            count = count + 1
            np.write()
        else:
            np[net] = (255,140,0)
            count = 0
            np.write()
            
async def alarm_colors(dt):
    count = 0
    net = 0
    current_col = "reds"
    
    reds = [(255, 0, 0), (235, 87, 0), (255, 234, 0)]
    purples = [(21, 6, 85),(121, 45, 163), (209, 78, 224)]
    
    time_to_change = 0
    while True:
        logic_state = off_button.value()
        if logic_state == True:
            return dt
        count = 0
        net = 0
    
        for net in range(led_len):
            logic_state = off_button.value()
            if logic_state == True:
                return dt
            
            print(time_to_change)
            if current_col == "reds":
                if count == 0:
                    np[net] = reds[0]
                    count = count + 1
                    np.write()
                elif count == 1:
                    np[net] = reds[1]
                    count = count + 1
                    np.write()
                else:
                    np[net] = reds[2]
                    count = 0
                    np.write()
                    
                time.sleep(0.5)
            elif current_col == "purples":
                if count == 0:
                    np[net] = purples[0]
                    count = count + 1
                    np.write()
                elif count == 1:
                    np[net] = purples[1]
                    count = count + 1
                    np.write()
                else:
                    np[net] = purples[2]
                    count = 0
                    np.write()
                    
                time.sleep(0.5)
            
            time_to_change = time_to_change + 0.5
            if time_to_change % 60 == 0 and time_to_change != 0:
                clock_updater(dt)
                to_display = print_time(dt)
                display(to_display)
                
        if current_col == "reds":
               current_col = "purples"
        elif current_col == "purples":
              current_col = "reds"
        time.sleep(1)
        
        time_to_change = time_to_change + 1
        if time_to_change % 60 == 0 and time_to_change != 0:
            clock_updater(dt)
            to_display = print_time(dt)
            display(to_display)

def colors_off():
    np.fill((0,0,0))
    np.write()

async def alarm_on(dt):
    turn_motor_on()
    loop = asyncio.get_event_loop()
    loop.create_task(buzzer_start())
    task = loop.create_task(alarm_colors(dt))

    new_dt = await task  # Wait for the completion of alarm_colors()
    print(new_dt)
    return new_dt
    
def alarm_off():
    turn_motor_off()
    buzzer_stop()
    colors_off()
    #need to add audio off function

def time_led_check(t):
    global led_status
    #print(t)
    #4am -> 11am, 12pm -> 6pm, 7pm -> 3am
    if int(t[0]) > 4 and int(t[0]) < 12 and int(t[2]) == 0 and led_status != "morning":
        #set to morning colors
        morning_colors()
        led_status = "morning"
    elif (t[0] == 12 or (t[0] > 0 and t[0] < 6)) and t[2] == 1 and led_status != "evening":
        evening_colors()
        led_status = "evening"
    elif (t[0] >= 7 and t[0] < 3) and led_status != "night":
        night_colors()
        led_status = "night"


def driver():
    turn_motor_on()
    oled.text("Hello!", 45, 0)
    oled.text("I am your clock", 5, 20)
    oled.text(":)", 45, 40)
    oled.show()

    utime.sleep(3)
    oled.fill(0)
    
    
    
    global time_dis
    display_time = [3,50,0]
    alarm_time = [4,1,0]
    
    oled.text("Setup the alarm...", 5, 20)
    oled.show()

    utime.sleep(1.5)
    oled.fill(0)
    
    time_setter()
    alarm_time = time_dis
    
    utime.sleep(0.5)
    oled.fill(0)
    
    oled.text("Setup the time...", 5, 20)
    oled.show()

    utime.sleep(1.5)
    oled.fill(0)
    
    time_setter()
    display_time = time_dis
    oled.fill(0)
    
    #night_colors()
    
    while True:
        if joystick_button.value() == 0:
            time_setter()
            display_time = time_dis
            utime.sleep(1)
        else:
            for i in range(60):
                if joystick_button.value() == 0:
                    break
                utime.sleep(1)
            clock_updater(display_time)
            
            to_display = print_time(display_time)
            display(to_display)
            
        if display_time == alarm_time:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(alarm_on(display_time))
            alarm_off()

            
driver()
