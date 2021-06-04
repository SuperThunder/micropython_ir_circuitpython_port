# A "port" of micropython_ir to work with CircuitPython pulseio
CircuitPython does not support setting on your own interrupts or callbacks or even timer interrupts.
However, for the common use case of measuring the length of pulses, it does have a library called pulseio.

The decode functions from micropython_ir are not too difficult to convert to work with pulseio, which I have done for the protocol relevant to me (NEC8).

# What works
NEC8 decode when used in code.py works, mostly.

# What doesn't work
Currently, any receive protocol other than NEC, and any form of transmit. Each has to be adapted so that callbacks and interrupts are not required.


