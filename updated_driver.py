from machine import Pin, ADC, PWM, RTC, ADC, I2C
import utime
import neopixel
import time
import ssd1306
from ssd1306 import SSD1306_I2C

xAxis = ADC(Pin(27))
yAxis = ADC(Pin(26))
joystick_button = Pin(16,Pin.IN, Pin.PULL_UP)

buzzer = PWM(Pin(6))


led_len = 76
np = neopixel.NeoPixel(machine.Pin(10), led_len, bpp=3)


global time_dis
global led_status

led_status = "morning"

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
            print(digit_position)
            
        elif xValue >= 60000:
            xStatus = "right"
            
            if digit_position + 1 <= 2:
                digit_position = digit_position + 1
            else:
                digit_position = 0
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
            
            print_time(time_dis)
            
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
            
            print_time(time_dis)
            
        if joystick_buttonValue == 0:
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
        
 
def buzzer_start():
    #Set buzzer 'pitch'
    buzzer.freq(500)
    #Set buzzer loudness
    buzzer.duty_u16(1000)

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
            
def alarm_colors(dt):
    count = 0
    net = 0
    current_col = "reds"
    
    reds = [(255, 0, 0), (235, 87, 0), (255, 234, 0)]
    purples = [(21, 6, 85),(121, 45, 163), (209, 78, 224)]
    
    time_to_change = 0
    while True:
        logic_state = off_button.value()
        if logic_state == True:
            break
        count = 0
        net = 0
    
        for net in range(led_len):
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

def alarm_on(dt):
    buzzer_start()
    new_dt = alarm_colors(dt)
    
    return new_dt
        
    #need to add audio on function
    
def alarm_off(pin):
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
    else:
        night_colors()
        led_status = "night"


def driver():
    global time_dis
    display_time = [3,50,0]
    seconds = 0
    turn_off_alarm = False
    alarm_time = [3,55,0]
    
    night_colors()
    
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
            display_time = alarm_on(display_time)
        
        #Alarm on/off mode code -> needs HW testing
        """
        if display_time == alarm_time
            alarm_on()
            turn_off_alarm = True
            while off_button.value() == 0:
                utime.sleep(0.2)
        
        if turn_off_alarm == True:
            alarm_off()
            turn_off_alarm = False
        """
            
driver()

