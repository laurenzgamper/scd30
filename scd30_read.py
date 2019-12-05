#!/usr/bin/env python3
# coding=utf-8

import sys
import time
import scd30

PIGPIO_HOST = '::1'
I2C_SLAVE = 0x61
I2C_BUS = 1

sensor = scd30.SCD30(PIGPIO_HOST, I2C_SLAVE, I2C_BUS)

# trigger continous measurement
sensor.sendCommand(scd30.COMMAND_CONTINUOUS_MEASUREMENT, 970)

# enable autocalibration
sensor.sendCommand(scd30.COMMAND_AUTOMATIC_SELF_CALIBRATION, 1)

sensor.waitForDataReady()

try:
	while True:
		# read measurement
		data = sensor.readMeasurement()

		if (data == False):
			exit(1)

		[float_co2, float_T, float_rH] = data

		if float_co2 > 0.0:
			print("gas_ppm{sensor=\"SCD30\",gas=\"CO2\"} %f" % float_co2)

		print("temperature_degC{sensor=\"SCD30\"} %f" % float_T)

		if float_rH > 0.0:
			print("humidity_rel_percent{sensor=\"SCD30\"} %f" % float_rH)

		time.sleep(3)

except KeyboardInterrupt:
    sensor.close()
	