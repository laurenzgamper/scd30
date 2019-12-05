import pigpio
import struct
import crcmod
import sys
import time

COMMAND_CONTINUOUS_MEASUREMENT = 0x0010
COMMAND_SET_MEASUREMENT_INTERVAL = 0x4600
COMMAND_GET_DATA_READY = 0x0202
COMMAND_READ_MEASUREMENT = 0x0300
COMMAND_AUTOMATIC_SELF_CALIBRATION = 0x5306
COMMAND_SET_FORCED_RECALIBRATION_FACTOR = 0x5204
COMMAND_SET_TEMPERATURE_OFFSET = 0x5403
COMMAND_SET_ALTITUDE_COMPENSATION = 0x5102

class SCD30: 

	def __init__(self, pigpioHost='::1', i2cSlave=0x61, i2cBus=1):
	    self.pi = pigpio.pi(pigpioHost)
	    if not self.pi.connected:
	    	print("no connection to pigpio daemon at " + pigpioHost + ".")
	    	exit(1)

	    try:
	    	self.pi.i2c_close(0)
	    except:
	    	[type, value, traceback] = sys.exc_info()
	    	if value and str(value) != "'unknown handle'":
	    		print("Unknown error: ", type, ":", value)

	    try:
	    	self.handle = self.pi.i2c_open(i2cBus, i2cSlave)
	    except:
	    	print("i2c open failed")
	    	exit(1)


	def close(self):
	    self.pi.i2c_close(self.handler)


	def sendCommand(self, command, argument=None):
	    if argument is None:
		    commandLSB = 0xFF & command
		    commandMSB = 0xFF & (command >> 8)

		    return self.i2cWrite([commandMSB, commandLSB])

	    else:
		    commandLSB = 0xFF & command
		    commandMSB = 0xFF & (command >> 8)
		    argumentLSB = 0xFF & argument
		    argumentMSB = 0xFF & (argument >> 8)

		    f_crc8 = crcmod.mkCrcFun(0x131, 0xFF, False, 0x00)
		    argumentString = (chr(argumentMSB) + chr(argumentLSB)).encode('utf-8')
		    crc8 = f_crc8(argumentString)

	    return self.i2cWrite([commandMSB, commandLSB, argumentMSB, argumentLSB, crc8])

	def read_n_bytes(self, n_bytes):

		try:
			(count, data)=self.pi.i2c_read_device(self.handle, n_bytes)
		except:
			print("error: i2c_read failed")
			exit(1)

		if count == n_bytes:
			return data
		else:
			print("error: read measurement interval didnt return " + str(n_bytes) + "B")
			return False

	def i2cWrite(self, data):
		try:
			self.pi.i2c_write_device(self.handle, data)
		except:
			print("error: i2c_write failed")
			return -1
		return True

	def readMeasurement(self):
		self.sendCommand(COMMAND_READ_MEASUREMENT)
		data=self.read_n_bytes(18)

		if data == False:
			return False
		struct_co2=struct.pack('>BBBB', data[0], data[1], data[3], data[4])
		float_co2=struct.unpack('>f', struct_co2)

		struct_T=struct.pack('>BBBB', data[6], data[7], data[9], data[10])
		float_T=struct.unpack('>f', struct_T)

		struct_rH=struct.pack('>BBBB', data[12], data[13], data[15],  data[16])
		float_rH=struct.unpack('>f', struct_rH)

		return [float_co2[0], float_T[0], float_rH[0]]

	def waitForDataReady(self):
	    # wait for read ready status
	    while True:
	    	ret=self.sendCommand(COMMAND_GET_DATA_READY)
	    	if ret == -1:
	    		exit(1)

	    	data=self.read_n_bytes(3)
	    	if data == False:
	    		time.sleep(0.1)
	    		continue

	    	if data[1] == 1:
	    		return
	    	else:
	    		time.sleep(0.1)
