import time, pigpio

fo = open("times.txt", "a")
def myGetTS(x, y, z):
    t = time.time()
    fo.write(str(t) + '\n')
    fo.flush()

pin = pigpio.pi()
cb = pin.callback(23, pigpio.FALLING_EDGE, myGetTS)

while True:
    time.sleep(15)
