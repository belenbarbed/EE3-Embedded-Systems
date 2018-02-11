import machine
import time
#import ujson
#import network
#from umqtt.simple import MQTTClient

# read x axis
def getX():
	x_higher = int.from_bytes(i2cport.readfrom_mem(24, 0x29, 1), 'little')
	x_lower = int.from_bytes(i2cport.readfrom_mem(24, 0x28, 1), 'little')
	x = (x_higher << 8) + x_lower
	return x

# read y axis
def getY():
	y_higher = int.from_bytes(i2cport.readfrom_mem(24, 0x2B, 1), 'little')
	y_lower = int.from_bytes(i2cport.readfrom_mem(24, 0x2A, 1), 'little')
	y = (y_higher << 8) + y_lower
	return y

# read z axis
def getZ():
	z_higher = int.from_bytes(i2cport.readfrom_mem(24, 0x2D, 1), 'little')
	z_lower = int.from_bytes(i2cport.readfrom_mem(24, 0x2C, 1), 'little')
	z = (z_higher << 8) + z_lower
	return z


# ###################### CODE BEGINS HERE ##############################################

# set up i2c comm
i2cport = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4), freq=100000)

# enable accelerometer read at 400Hz (at reg 0x20)
i2cport.writeto(24, bytearray([0x20, 0x77]))	

'''
# connect to WiFi
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('EEERover', 'exhibition')
time.sleep(5)
print(sta_if.isconnected())

# connect to MQTT broker
client = MQTTClient(machine.unique_id(), "192.168.0.10")
client.connect()
'''

time.sleep(2)

run_freq = 400
bpm_freq  = 15
run_for_s = bpm_freq * 2

# isBelow: False = rising edge has been last detected
#          True  = falling edge has been last detected
isBelow = False

for i in range(0, run_for_s/bpm_freq):

	peak_ps = 0
	until = 0

	for j in range (0, run_freq * bpm_freq):
	
		x = getX()
		#print(x)
		
		if((x < 20000) and (j > until) and (isBelow == False)):
			peak_ps += 1
			until = j + 75
			isBelow = True
		
		if((x > 50000) and (j > until) and (isBelow == True)):
			peak_ps += 1
			until = j + 125
			isBelow = False
	
		# total period is 2500us
		# computation per period takes approx 2100us
		time.sleep_us(400)

	bpm = int(peak_ps * (60/bpm_freq))
	print("bpm: "+str(bpm))
