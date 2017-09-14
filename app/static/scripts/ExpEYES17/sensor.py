import eyes17.eyes as eyes, time
from eyes17.SENSORS import MPU6050

from eyes17.SENSORS.supported import supported,nameMap
from eyes17.sensorlist import sensors as sensorHints


p=eyes.open()

lst =  p.I2C.scan()
for a in lst:
	sen = sensorHints.get(a,['unknown'])[0]
	if 'MPU-6050' in sen:
		mysensor = supported[a].connect(p.I2C,address = a)
		print mysensor.PLOTNAMES
		break

st = time.time()
for k in range(1000):
	x=mysensor.getRaw()

print time.time()-st
