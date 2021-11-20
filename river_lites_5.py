# river lites 5 setting button/program always activated until power loss
# river lites 4 adding sound
# river lites 3 adding a start  GPIO button
# river lites 2 just doubled main to see longer display
# fake an I2C using GPIO 2/13/2021
# _v0 is just a speed test... it takes 35sec to set 69 registers 1000 times
# _v1 just sends data walking thru some bightnsess a few times
# _v1a set PWM freq to max
# use GPIO
# _v2r dos random and uses pinout for intrface PCB, OE* to 16, SCL to 8
#   SDO to 12, SDI to 10
# seq lights LEDs 0-15 one at time for 0.2sec. then off for 1 second tot 4.2 sec
import RPi.GPIO as GPIO
import time
import random
import pygame
from pygame import mixer

pygame.init()

def send_byte_s(byt): #send low nibble of byte, handle enable on/off
    GPIO.output(scl,GPIO.LOW)
    for i in range(9): # allow for underscore at b.4, b.0 is msb
        if i != 4:
            if byt[i]=='1' :
                #GPIO.output(sdob,GPIO.LOW)
                GPIO.output(sdo ,GPIO.HIGH)
            elif byt[i]=='0' :
                #GPIO.output(sdob,GPIO.HIGH)
                GPIO.output(sdo ,GPIO.LOW)
            else:
                print('bad byte string')
            GPIO.output(scl,GPIO.HIGH)  #clock a bit out
            #print('')
            GPIO.output(scl,GPIO.LOW)
    #look for ack
    #GPIO.output(sdob,GPIO.LOW) #set data bar out low so it can float up
    GPIO.output(sdo ,GPIO.HIGH) #set data bar out low so it can float up
    res=GPIO.input(sdi) #could check for low which is an ack, high no_ack
    if res==True :
        print('nac1') #input('check ack/nack level then press enter to continue')
    res=GPIO.input(sdi) #could check for low which is an ack, high no_ack
    if res==True :
        print('nac2')

    #help the SDA to stay low to avoid a new start condition
    #GPIO.output(sdob,GPIO.HIGH) #allow for NPN
    GPIO.output(sdo ,GPIO.LOW) #allow for NPN

    GPIO.output(scl,GPIO.HIGH)  #clock the ack to be over
    GPIO.output(scl,GPIO.LOW)

def send_2byte_num(num): #send low nibble of byte, handle enable on/off
    GPIO.output(scl,GPIO.LOW)
    num_loc=num % 4096 #set to 0-4095
    byte=bin(65536+num_loc)[3:19] #16bit string w/o 0b1
    for ibyte in range(2): # 0-1 send low byte first
        for icnt in range(8) : #0-7
            ibit=icnt+(1-ibyte)*8 #do 8-15 and then 0-7
            if   byte[ibit]=="1" :
                GPIO.output(sdo ,GPIO.HIGH)
            elif byte[ibit]=="0" :
                GPIO.output(sdo ,GPIO.LOW)
            else:
                print('bad conversion of num to bits')
            GPIO.output(scl,GPIO.HIGH)  #clock the bit out
            GPIO.output(scl,GPIO.LOW)

        #look for ack at end of byte
        GPIO.output(sdo ,GPIO.HIGH) #set data bar out low so it can float up
        res=GPIO.input(sdi) #could check for low which is an ack, high no_ack
        if res==True :
            print('nac1') #input('check ack/nack level then press enter to continue')
        res=GPIO.input(sdi) #2nd check for low which is an ack, high no_ack
        if res==True :
            print('nac2')

        #help the SDA to stay low to avoid a new start condition
        GPIO.output(sdo ,GPIO.LOW)

        GPIO.output(scl,GPIO.HIGH)  #clock scl for the ack to be over
        GPIO.output(scl,GPIO.LOW)



##*************************
## start of MAIN
##*************************

#***** Initialize GPIO
# GND=9, 3.3v=1, and V+ are hardwired
od=16  #pin 16 was 11 for OE* = od output disable
scl=8  #pin 8 was 3 for Serial CLock
sdo =12  #pin was 5 for Serial Dat Out
sdi=10


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(od,GPIO.OUT)
GPIO.setup(scl,GPIO.OUT)
GPIO.setup(sdo,GPIO.OUT)
GPIO.setup(sdi,GPIO.IN)   #not inverted because oi can just read



# Pre-start initialization
GPIO.output(od ,GPIO.LOW)

#set to sleep mode first Mode1.4=1 else PWM freq can't be set
# prepare to start both high
GPIO.output(scl, GPIO.HIGH)
GPIO.output(sdo, GPIO.HIGH)
#do the start
GPIO.output(sdo ,GPIO.LOW) # start condition, inv because of NPN
GPIO.output(scl ,GPIO.LOW)   # prepare to clock, end of start condition
#wake up give address
send_byte_s('1000_0000') #address slave 0 in write mode
send_byte_s('0000_0000') #address Mode 1
send_byte_s('0001_0000') #set data to 0x10
GPIO.output(scl ,GPIO.HIGH)
GPIO.output(sdo ,GPIO.HIGH) # stop condition, inv because of NPN



#freq set in 0xFE to 3 (max)
# prepare to start both high
GPIO.output(scl,GPIO.HIGH)
GPIO.output(sdo ,GPIO.HIGH)
#do the start
GPIO.output(sdo ,GPIO.LOW) # start condition
GPIO.output(scl,GPIO.LOW)   # prepare to clock, end of start condition
#wake up give address
send_byte_s('1000_0000') #address slave 0 in write mode
send_byte_s('1111_1110') #address register 0xFE
send_byte_s('0000_0011') #set data to 3
GPIO.output(scl,GPIO.HIGH)
GPIO.output(sdo ,GPIO.HIGH) # stop condition

##### Get data from file only use the first 32,000 entries
#fd=open('/home/pi/Desktop/Python_Projects/junk0.txt','rb')
#fd=open('/home/pi/Desktop/Python_Projects/triangle0.txt','rb')
#fd=open('/home/pi/Desktop/Python_Projects/junk0.txt','rb')
fd=open('/home/pi/Desktop/Python_Projects/triple_triangle0.txt','rb')
#fd=open('/home/pi/Desktop/Python_Projects/ramp0.txt','rb')
#fd=open('/home/pi/Desktop/Python_Projects/rand0.txt','rb')
#fd=open('/home/pi/Desktop/Python_Projects/seq0.txt','rb')
stuff=fd.read()
fd.close()

#set for auto increment and OE* enabled
# prepare to start both high
GPIO.output(scl,GPIO.HIGH)
GPIO.output(sdo ,GPIO.HIGH)
#do the start
GPIO.output(sdo ,GPIO.LOW) # start condition
GPIO.output(scl,GPIO.LOW)   # prepare to clock, end of start condition
send_byte_s('1000_0000') #address slave 0 in write mode
send_byte_s('0000_0000') #address register 0
send_byte_s('0010_0000') #set AI bit in MODE1 reg
send_byte_s('0000_0100') #MODE2 b.1:0=01 lets OE* work. b.2=1 totem out
                        #b.4=0 invert
send_byte_s('0000_0000') #junk sub-address1
send_byte_s('0000_0000') #junk sub-address2
send_byte_s('0000_0000') #junk sub-address3
send_byte_s('0000_0000') #junk to  all call
GPIO.output(scl,GPIO.HIGH)
GPIO.output(sdo ,GPIO.HIGH) # stop condition

#set up pushbutton to start
#***** Initialize GPIO
# GND=39, pull_up=38, push_button=40
p_b=40
p_u=38
GPIO.setup(p_u,GPIO.OUT)
GPIO.setup(p_b,GPIO.IN)

# init pushbutton
GPIO.output(p_u ,GPIO.HIGH)
p_b_old=GPIO.input(p_b)

# start the program
z=1
y=0
while z > 0:
    print ('push button when ready .04/800/2')
    while GPIO.input(40)==1 : #wait for low
        #a=1
        pass
    pygame.mixer.music.load("/home/pi/Desktop/Sounds/carol_of_the_bells.mp3")
    pygame.mixer.music.play()

    ##### send the main stuff
    num = 2 # number of 30 sec repetition
    for x in range(num):
        y = y+1

    #    print ('push button when ready')
    #    while GPIO.input(40)==1 : #wait for low
    #        #a=1
    #        pass

        GPIO.output(od ,GPIO.LOW) #turns on lites else stays off w/o line.

        time_old=time.time() #this is the start time for the main stuff
        sync_error=[]
        for j in range(800): #was 1000
            #wait for the right time
            sync_target=time_old+float(j)*0.04 #changed from 0.03
            while time.time()<sync_target:
                wait=1
            sync_error.append(time.time()-sync_target) #save error

            #prepare to start - both high
            GPIO.output(scl,GPIO.HIGH)
            GPIO.output(sdo,GPIO.HIGH)
            #do the start
            GPIO.output(sdo,GPIO.LOW) # start condition
            GPIO.output(scl,GPIO.LOW)   # prepare to clock, end of start condition

            send_byte_s('1000_0000') #address slave 0 in write mode
            send_byte_s('0000_0110') #address register 6


            for i in range(16):
                brght_H=stuff[j*32+i*2    ]
                brght_L=stuff[j*32+i*2 + 1]
                brght=64*brght_H + brght_L
                send_2byte_num(0) #on at zero
                send_2byte_num(brght) #off at brght


            GPIO.output(scl,GPIO.HIGH)
            GPIO.output(sdo ,GPIO.HIGH) # stop condition



        t_del=time.time()-time_old

        #GPIO.output(od ,GPIO.HIGH) #turns off lites
        if y == 2:
            print("elapsed time for 800 sets = ",t_del)#was for 1000 sets
            print("max sync error=",max(sync_error))
            print("average sync error=",sum(sync_error)/800)#was /1000

            GPIO.output(od ,GPIO.HIGH) #turns off lites else stays lit w/o line.
            y=0
    pass
