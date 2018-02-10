import machine
import time
import ujson
import network
from umqtt.simple import MQTTClient

# read z axis
def getZ():
	z_higher = int.from_bytes(i2cport.readfrom_mem(24, 0x2D, 1), 'little')
	z_lower = int.from_bytes(i2cport.readfrom_mem(24, 0x2C, 1), 'little')
	z = (z_higher << 8) + z_lower
	return z
	
def max_val(x):
    max = x[0]
    for i in range(1, len(x)-1):
        if(x[i] > max):
            max = x[i]
    return max

# ###################### CODE BEGINS HERE ##############################################

# set up i2c comm
i2cport = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4), freq=100000)

# enable accelerometer read at 100Hz (at reg 0x20)
#i2cport.writeto(24, bytearray([0x20, 0x57]))
# enable accelerometer read at 400Hz (at reg 0x20)
i2cport.writeto(24, bytearray([0x20, 0x74]))	

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

run_for_s = 60
run_freq = 400
bpm_freq  = 10

time.sleep(2)
isBelow = False

moving_av = 5
z_vals = [0] * moving_av

for i in range(0, run_for_s/bpm_freq):

	peak_ps = 0

	for j in range (0, run_freq * bpm_freq):
	
		z_vals[j%moving_av] = getZ()
		# moving average
		z = z_vals[0] + z_vals[1] + z_vals[2] + z_vals[3] + z_vals[4]
		z = z/moving_av
		#z = max_val(z_vals)
		
		if(z < 15000):
			isBelow = True
		
		if((z > 46500) and (isBelow == True)):
			peak_ps += 1
			isBelow = False
	
		time.sleep(1/run_freq)

	bpm = int(peak_ps * (60/bpm_freq))
	print(bpm)
	dict = {'bpm': bpm}
	data = ujson.dumps(dict)
	client.publish('esys/The100/', bytes(data, 'utf-8'))
