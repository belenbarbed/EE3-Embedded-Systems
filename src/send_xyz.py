import machine
import time
import sys
import os
import ujson
import network
from umqtt.simple import MQTTClient

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

# enable accelerometer read at 100Hz (at reg 0x20)
i2cport.writeto(24, bytearray([0x20, 0x57]))	

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

run_for_s = 20
run_freq = 100
for i in range(0, run_for_s * run_freq):

	x = getY()	
	y = getY()
	z = getZ()
	
	# save values in dictionary
	#dict = {'X': x, 'Y': y, 'Z': z, 'It': i}
	#data = ujson.dumps(dict)
	#client.publish('esys/The100/', bytes(data, 'utf-8'))

	#print("X: ", x)
	#print("Y: ", y)
	#print("Z: ", z)
	#print("Fucks up here", i)
	print(z)
	
	# 100Hz
	time.sleep(1/run_freq)
