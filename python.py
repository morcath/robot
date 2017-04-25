#!/usr/bin/env python3
import ev3dev.ev3 as ev3
import time
import math
from PIL import Image

#A,B,C,D - silniki // 1,2,3,4 - czujniki

csP = ev3.ColorSensor('in1') #prawy
csL = ev3.ColorSensor('in4') #lewy
ifs = ev3.InfraredSensor('in2') #sensor podczerwieni
mR = ev3.LargeMotor('outA') #prawe
mL = ev3.LargeMotor('outB') #lewe
msen = ev3.MediumMotor('outD') #silnik z sensorem
ts = ev3.TouchSensor('in3')

msen.run_to_abs_pos(position_sp=0, speed_sp=80)

nominalSpeed = 100
maxSpeed = 200

kp = 0.9
ki = 0.0
kd = 0.0

lastError = 0
backgroundColor = 27
integral = 0


maxSpeeds = [0.0]

def set_motors(leftSpeed, rightSpeed):
    mL.run_forever(speed_sp=leftSpeed)
    mR.run_forever(speed_sp=rightSpeed)

lastR = 0
lastL = 0
	

def skipObstacle():


	mR.run_to_rel_pos(position_sp=-180, speed_sp=80)			#guziczek naciśnięty - cofa się
	mL.run_to_rel_pos(position_sp=-180, speed_sp=80)

	while "running" in (mR.state or mL.state):
		continue
		
	mR.run_to_rel_pos(position_sp=325, speed_sp=80)			#skręt w lewo
	msen.run_to_abs_pos(position_sp=90, speed_sp=80)

	while "running" in (mR.state or mL.state):
		continue
	
	mR.run_to_rel_pos(position_sp=180, speed_sp=80)			#podjeżdza trochę do przodu
	mL.run_to_rel_pos(position_sp=180, speed_sp=80)

	while "running" in (mR.state or mL.state):
		continue

	while ifs.value() < 30:
		mR.run_to_rel_pos(position_sp=45, speed_sp=80)		#dopóki widzi przeszkodę jedzie
		mL.run_to_rel_pos(position_sp=45, speed_sp=80)

	out = False
	while out == False:	
		mL.run_to_rel_pos(position_sp=280, speed_sp=80)			#skręt w prawo 325
		mR.run_to_rel_pos(position_sp=-40, speed_sp=80)
		while "running" in (mR.state or mL.state):
			if csP.reflected_light_intensity < backgroundColor or csL.reflected_light_intensity < backgroundColor:
				msen.run_to_abs_pos(position_sp=0, speed_sp=80)
				while "running" in (msen.state):
					continue
				print("!")
				out = True
				break

		while ifs.value() > 30 and out == False:
			mR.run_to_rel_pos(position_sp=90, speed_sp=80)			#podjeżdża, żeby zobaczyć przeszkodę
			mL.run_to_rel_pos(position_sp=90, speed_sp=80)
			if csP.reflected_light_intensity < backgroundColor or csL.reflected_light_intensity < backgroundColor:
				msen.run_to_abs_pos(position_sp=0, speed_sp=80)
				while "running" in (msen.state):
					continue
				print("!")
				out = True
				break


		while "running" in (mR.state or mL.state):
			continue

	
		while ifs.value() < 30 and out == False:
			mR.run_to_rel_pos(position_sp=45, speed_sp=80)
			mL.run_to_rel_pos(position_sp=45, speed_sp=80)
			print("-----------jkjkj---------------")
			print(csP.reflected_light_intensity )
			print(csL.reflected_light_intensity)
			print("-----------------------------")
			if csP.reflected_light_intensity < backgroundColor or csL.reflected_light_intensity < backgroundColor:
				msen.run_to_abs_pos(position_sp=0, speed_sp=80)
				while "running" in (msen.state):
					continue
				print("!")
				out = True
				break

		if out:
			break

		print("Wszedl?")
		mR.run_to_rel_pos(position_sp=270, speed_sp=80)			#podjeżdża, żeby zobaczyć przeszkodę
		mL.run_to_rel_pos(position_sp=270, speed_sp=80)

		while "running" in (mR.state or mL.state):
			continue



	while csP.reflected_light_intensity > backgroundColor:		#prawy sensor wykrywa czarny		
		mR.run_timed(time_sp=100, speed_sp=250) #3000ms 500degress per sec   w


def findObstacle():
	if ts.is_pressed:
		print("UPS!")
		skipObstacle()


nominalSpeed = 70
maxSpeed = 70

initialPositionR = mR.position
initialPositionL = mL.position

lastR = initialPositionR
lastL = initialPositionL

d = 0.135
r = 0.069/2

teta = 0
x = 0
y = 0

bitmap = list()

tmpL = mL.position
tmpR = mR.position
deltaFiL = tmpL - lastL
deltaFiR = tmpR - lastR
lastL = tmpL
lastR = tmpR

deltaTeta = r/d*(deltaFiL - deltaFiR)
deltaP = r/2*((deltaFiL + deltaFiR)/180*math.pi)


teta = teta + deltaTeta
x = x + deltaP*math.cos((teta + deltaTeta/2)/180*math.pi)
y = y + deltaP*math.sin((teta + deltaTeta/2)/180*math.pi)

tup = (int(x*100),int(y*100))
bitmap.append(tup)

print(x,"\t",y,"\t",teta)

def pomiary():
	global tmpL, tmpR, deltaFiL, deltaFiR, lastL, lastR, deltaTeta, deltaP, x, y, teta, bitmap
	tmpL = mL.position
	tmpR = mR.position
	deltaFiL = tmpL - lastL
	deltaFiR = tmpR - lastR
	lastL = tmpL
	lastR = tmpR

	deltaTeta = r/d*(deltaFiL - deltaFiR)
	deltaP = r/2*((deltaFiL + deltaFiR)/180*math.pi)



	x = x + deltaP*math.cos((teta + deltaTeta/2)/180*math.pi)
	y = y + deltaP*math.sin((teta + deltaTeta/2)/180*math.pi)
	teta = teta + deltaTeta


	tup = (int(x*100),int(y*100))
	bitmap.append(tup)

	print(x,"\t",y,"\t",teta)

try:
#----------------------------------
	direction = "l"	



	while True:
		speedDifference = 0
       
		pomiary()
		findObstacle()

		if csP.reflected_light_intensity < backgroundColor or csL.reflected_light_intensity < backgroundColor:
		        tmpColor = (csL.reflected_light_intensity - csP.reflected_light_intensity)
		       
		             
		        error            =  -tmpColor
		        proportional        =  kp * error
		        integral        =  ki * error + 0.75 * integral
		        derivative        =  kd *(error - lastError)
		        lastError = error


		        speedDifference = proportional + integral + derivative
		        if speedDifference > maxSpeed:
		            speedDifference = maxSpeed
		            maxSpeeds.append(time.clock()-maxSpeeds[-1])
		        elif speedDifference < -maxSpeed:
		            speedDifference = -maxSpeed

		        if speedDifference > 0: # Wprawo
		            set_motors(nominalSpeed+speedDifference, nominalSpeed)
		            direction = "r"
		   
		        else: #Wlewo
		            set_motors(nominalSpeed, nominalSpeed-speedDifference)
		            direction = "l"
		else:
		        if direction == 'r': # Wprawo   
		            set_motors(maxSpeed, -maxSpeed*0.85)
		            direction = "r"
		   
		        else: #Wlewo
		            set_motors(-maxSpeed*0.85, maxSpeed)
		            direction = "l"
           

		time.sleep(0.01)
#--------------------------------
	while True:
	    ev3.Leds.set_color(ev3.Leds.LEFT, (ev3.Leds.GREEN, ev3.Leds.RED)[ts.value()])


except KeyboardInterrupt:	

	# Jaka szerokosc i wysokosc ze skrajnych punktów
	bitmap = sorted(bitmap, key=lambda tup:tup[1])
	set_motors(0, 0)

	minimalY = bitmap[0][1]
	maximalY = bitmap[-1][1]
	
	bitmap = sorted(bitmap, key=lambda tup:tup[0])

	minimalX = bitmap[0][0]
	maximalX = bitmap[-1][0]


	width =  2*max(maximalX, -minimalX) +20
	height = 2*max(maximalY, -minimalY) +20
	#Przeróbmy współrzędne na tablicę 2D 0 i 1 uwaga - 1 to tło 0 to linia
	
	image = list()
	for i in  range (0,width):
		image.append(list())

	for row in image:
	    for i in range (0, height):
	    	row.append(1)
	print (width)
	for point in bitmap:
		image[(point[0]+int(width/2))][point[1]+int(height/2)] = 0



	#Zmień 0 i 1 na bmp
	img = Image.new('1', (width, height))
	pixels = img.load()

	for i in range(img.size[0]):
	   for j in range(img.size[1]):
	   	pixels[i, j] = image[i][j]

	img.show()
	img.save("mapa.bmp")
	
