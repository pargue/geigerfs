import time,pigpio

fo=open("randtimegeiger_82_1.txt","a")
def mycb(x,y,z):
	t=time.time()
	print t
	fo.write(str(t)+'\n')
	fo.flush()

pin=pigpio.pi()
cb=pin.callback(23,pigpio.FALLING_EDGE,mycb)

while True:

	time.sleep(15)
