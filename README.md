# scd30
Python library for the Sensirion SCD30 co2, temperature, humidity sensor. 

### I2C Clock stretching

Master needs to support Clock Stretching up to 150ms. The default in Raspbian is too low, we have to increase it:

To set it, download from here:

```
https://github.com/raspihats/raspihats/tree/master/clk_stretch
```

Compile:
```
gcc -o i2c1_set_clkt_tout i2c1_set_clkt_tout.c
gcc -o i2c1_get_clkt_tout i2c1_get_clkt_tout.c
```

execute (add to /etc/rc.local to run on every boot):

```
./i2c1_set_clkt_tout 20000 # for 200ms
```

### Thanks

I borrowed some code and ideas from these two repos:

https://github.com/UnravelTEC/Raspi-Driver-SCD30 (python code, i2c clock stretching)
https://github.com/sparkfun/SparkFun_SCD30_Arduino_Library (code structure, commands)
