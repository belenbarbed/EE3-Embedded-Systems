from machine import Pin, I2C
from time import sleep
# set up i2c comm
i2cport = I2C(scl=Pin(5), sda=Pin(4), freq=100000)

# enable accelerometer read at 100Hz (at reg 0x20)
i2cport.writeto(24, bytearray([0x20, 0x57]))

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

fileX = open("dataX.txt", "w")
fileY = open("dataY.txt", "w")
fileZ = open("dataZ.txt", "w")
	
for i in range(0, 10):

	x = getX()
	y = getY()
	z = getZ()

	print("X: ", x)
	print("Y: ", y)
	print("Z: ", z)
	
	fileX.write(x)
	fileY.write(y)
	fileZ.write(z)
	
	# 100Hz
	time.sleep(.1)
