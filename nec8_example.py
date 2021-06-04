print("Hello from CircuitPython!")

import pulseio
import board
import time

pulsein = pulseio.PulseIn(board.D11, maxlen=200, idle_state=True)

# times: array of the time of each edge (originally, ticks_us() stored at each edge
# edge: count of the number of edges
# ticks_diff: find difference between two utime.ticks_xx (us, ms, or cpu) times (as normal +/- operations don't work properly)
#   - the original program recorded the actual time (in uS) of pulse events so needed to subtract adjacent events to figure out pulse length, pulseio has already done this for us
#   - thus calls to ticks_diff have been replaced with direct list accesses
def nec8_decode(edge, times):
    # This is all the parameters extracted from the nec8 class / abstract IR_RX class
    addr = -1 #init address
    addr_extended = False #we are using nec8
    nedges = 68 # 'Block lasts <= 80ms (extended mode) and has 68 edges'
    tblock = 80

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


    # return addr and cmd, rather than setting up callback like in micropython_ir
    return [addr, cmd]


while True:
    start_time = time.monotonic()

    # block until enough pulses
    # todo: doesn't account for repeat codes (they get ignored)
    while(len(pulsein) < 68):
        # if we get a timeout from pulseio, then clear the pulses
        if(len(pulsein) > 0 and pulsein[len(pulsein)-1] == 65535):
            pulsein.clear()

    # pause pulsein so that no new pulses get added between now and when it ultimately gets to the decode function
    pulsein.pause()

    edges = len(pulsein)
    edgel = []
    # convert the pulsein object data to a normal list
    for i in range(68):
        edgel.append(pulsein[i])
    #edgel.append(0)
    decode_result = nec8_decode(68, edgel)

    print('edges: ', edges)
    print(edgel)
    print(decode_result)

    # if you wanted to make a simple CircuitPython program than took in commands from an IR remote and did something in response, this is where you would do it
    # eg, you can make a USB HID consumer control device to remotely control volume, next/prev track, play-pause, mute, etc on your PC or phone

    pulsein.clear()
    pulsein.resume()

    # Shows the time it took to get here since the start of the while loop, most of which is waiting time in the while loop to get enough pulses
    print("Time = ", str(time.monotonic() - start_time))
    print("----------------------------")

