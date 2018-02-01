from machine import Pin, I2C
# set up i2c comm
i2cport = I2C(scl=Pin(5), sda=Pin(4), freq=100000)

# enable accelerometer read at 100Hz (at reg 0x20)
i2cport.writeto(24, bytearray([0x20, 0x57]))

# read x axis
x_higher = int.from_bytes(i2cport.readfrom_mem(24, 0x29, 1), 'little')
x_lower = int.from_bytes(i2cport.readfrom_mem(24, 0x28, 1), 'little')
x = (x_higher << 8) + x_lower

# read y axis
y_higher = int.from_bytes(i2cport.readfrom_mem(24, 0x2B, 1), 'little')
y_lower = int.from_bytes(i2cport.readfrom_mem(24, 0x2A, 1), 'little')
y = (y_higher << 8) + y_lower

# read z axis
z_higher = int.from_bytes(i2cport.readfrom_mem(24, 0x2D, 1), 'little')
z_lower = int.from_bytes(i2cport.readfrom_mem(24, 0x2C, 1), 'little')
z = (z_higher << 8) + z_lower

print(x)
print(y)
print(z)
