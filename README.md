# A "port" of micropython_ir to work with CircuitPython pulseio
CircuitPython does not support setting on your own interrupts or callbacks or even timer interrupts.
However, for the common use case of measuring the length of pulses, it does have a library called pulseio.

The decode functions from micropython_ir are not too difficult to convert to work with pulseio, which I have done for the protocol relevant to me (NEC8).

# What works
NEC8 decode when used in code.py works: copy the code in nec8_example.py into code.py of your CircuitPython board. At the moment it is the only example since I don't have other forms of remote (although it would probably be possible to simulate other remotes with an IR transmitter).

The global variables in nec8_example were extracted from micropython_ir's class system. It should be possible to make it back into an object that takes the pulseio instance, but the lack of threading / asynchronous events in CircuitPython makes it difficult to truly push processing the commands into the background.

# What doesn't work
Currently, any receive protocol other than NEC, and any form of transmit. Each has to be adapted so that callbacks and interrupts are not required.


