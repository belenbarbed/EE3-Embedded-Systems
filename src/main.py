import machine
import time
import ujson
import network
from umqtt.simple import MQTTClient

# function to read x axis
def getX():
	x_higher = int.from_bytes(i2cport.readfrom_mem(24, 0x29, 1), 'little')
	x_lower = int.from_bytes(i2cport.readfrom_mem(24, 0x28, 1), 'little')
	x = (x_higher << 8) + x_lower
	return x

# ###################### CODE BEGINS HERE ##############################################

# set up i2c comm
i2cport = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4), freq=100000)

# enable accelerometer read at 400Hz, only x axis activated
i2cport.writeto(24, bytearray([0x20, 0x77]))	

# connect to phone hotspot
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Belen', 'exhibition')

# give time for connection
time.sleep(5)
print(sta_if.isconnected())

# connect to eclipse iot MQTT broker
client = MQTTClient(machine.unique_id(), "iot.eclipse.org")
client.connect()

# give time for user to start running before we count the pace
time.sleep(2)

# run_freq: frequency of axis sampling
run_freq = 400
# bpm_freq: how often we calculate bpm
bpm_freq  = 15

# isBelow: False = rising edge has been last detected
#          True  = falling edge has been last detected
isBelow = False

while True:

	peak_ps = 0
	until = 0

	for j in range (0, run_freq * bpm_freq):
	
		x = getX()
		
		# state 1: 
		if((x < 20000) and (j > until) and (isBelow == False)):
			# update peak counter
			peak_ps += 1
			# don't detect a rising edge until 75 cycles have passed
			# as seen when running at 180bpm (avoids noise)
			until = j + 75
			# isBelow: True = falling edge has been last detected
			# rising edge should be detected next
			isBelow = True
		
		if((x > 50000) and (j > until) and (isBelow == True)):
			# update peak counter
			peak_ps += 1
			# don't detect a falling edge until 125 cycles have passed
			# as seen when running at 180bpm (avoids noise)
			until = j + 125
			# isBelow: False = rising edge has been last detected
			# falling edge should be detected next
			isBelow = False
	
		# total period is 2500us - 400Hz
		# computation per period takes approx 2100us
		# sleep for 400us to maintain periodicity
		time.sleep_us(400)

	# calculate peaks per minute from peaks in 15s period
	bpm = int(peak_ps * (60/bpm_freq))
	print("bpm: "+str(bpm))
	
	# send bpm values to broker
	dict = {'bpm': bpm}
	data = ujson.dumps(dict)
	client.publish('esys/The100/', bytes(data, 'utf-8'))
