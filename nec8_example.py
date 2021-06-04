print("Feather RP2040 started!")


import pulseio
import board
#import adafruit_irremote
import time
#import neopixel

#pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)

pulsein = pulseio.PulseIn(board.D11, maxlen=200, idle_state=True)
#decoder = adafruit_irremote.GenericDecode()

print('entering code.py ir test')
#pixels.fill([0,0,0])

addr = -1 #init address
addr_extended = False #we are using nec8
nedges = 68 # 'Block lasts <= 80ms (extended mode) and has 68 edges'
tblock = 80
# times: array of the time of each edge (originally, ticks_us() stored at each edge
# edge: count of the number of edges
# callback: in micropython_ir, callback given to run after each recognized IR command
# ticks_diff: find difference between two utime.ticks_xx (us, ms, or cpu) times (as normal +/- operations don't work properly)
def nec8_decode(edge, times):
    #print('nec8d edge', edge)
    #print('nec8d times', times)
    global addr
    # Repeat button code
    REPEAT = -1
    # Error codes
    BADSTART = -2
    BADBLOCK = -3
    BADREP = -4
    OVERRUN = -5
    BADDATA = -6
    BADADDR = -7
    try:
        if edge > 68:
            raise RuntimeError(OVERRUN)

        #width = ticks_diff(self._times[1], self._times[0])
        #width = times[1] - times[0]
        width = times[0]

        if width < 4000:  # 9ms leading mark for all valid data
            raise RuntimeError(BADSTART)
        #width = ticks_diff(self._times[2], self._times[1])
        #width = times[2] - times[1]
        width = times[1]

        if width > 3000:  # 4.5ms space for normal data
            if edge < 68:  # Haven't received the correct number of edges
                raise RuntimeError(BADBLOCK)
            # Time spaces only (marks are always 562.5µs)
            # Space is 1.6875ms (1) or 562.5µs (0)
            # Skip last bit which is always 1
            val = 0
            for edge in range(3, 68 - 2, 2):
                val >>= 1
                #if ticks_diff(self._times[edge + 1], self._times[edge]) > 1120:
                if times[edge] > 1120:
                    val |= 0x80000000
        elif width > 1700: # 2.5ms space for a repeat code. Should have exactly 4 edges.
            raise RuntimeError(REPEAT if edge == 4 else BADREP)  # Treat REPEAT as error.
        else:
            raise RuntimeError(BADSTART)
        addr = val & 0xff  # 8 bit addr
        cmd = (val >> 16) & 0xff
        if cmd != (val >> 24) ^ 0xff:
            raise RuntimeError(BADDATA)
        if addr != ((val >> 8) ^ 0xff) & 0xff:  # 8 bit addr doesn't match check
            if not addr_extended:
                raise RuntimeError(BADADDR)
            addr |= val & 0xff00  # pass assumed 16 bit address to callback
        #self._addr = addr
    except RuntimeError as e:
        cmd = e.args[0]
        addr = addr if cmd == REPEAT else 0  # REPEAT uses last address

    # Set up for new data burst and run user callback
    #self.do_callback(cmd, addr, 0, self.REPEAT)

    # we just return the addr and cmd instead
    return [addr, cmd]


while True:
    start_time = time.monotonic()
    #pulses = decoder.read_pulses(pulsein, max_pulse=10000, pulse_window=0.068, )
    #print("Heard", len(pulses), "Pulses:", pulses)
    #try:
    #    code = decoder.decode_bits(pulses)
    #    print("Decoded:", code)
    #except adafruit_irremote.IRNECRepeatException:  # unusual short code!
    #    print("NEC repeat!")
    #except adafruit_irremote.IRDecodeException as e:     # failed to decode
    #    print("Failed to decode: ", e.args)

    # block until enough pulses
    # todo: doesn't account for repeat codes
    while(len(pulsein) < 68):
        # if we get a timeout from pulseio, then clear the pulses
        if(len(pulsein) > 0 and pulsein[len(pulsein)-1] == 65535):
            pulsein.clear()
    pulsein.pause()

    edges = len(pulsein)
    edgel = []
    for i in range(68):
        edgel.append(pulsein[i])
    #edgel.append(0)
    res = nec8_decode(68, edgel)
    print('edges: ', edges)
    print(edgel)
    print('width1: ', pulsein[0])
    print(pulsein[2], pulsein[1], pulsein[0])
    print(res)

    pulsein.clear()
    pulsein.resume()

    print("Time = ", str(time.monotonic() - start_time))
    print("----------------------------")

