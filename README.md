# A "port" of micropython_ir to work with CircuitPython pulseio
CircuitPython does not support setting on your own interrupts or callbacks or even timer interrupts.
However, for the common use case of measuring the length of pulses, it does have a library called pulseio.

The decode functions from micropython_ir are not too difficult to convert to work with pulseio, which I have done for the protocol relevant to me (NEC8).

# What works
NEC8 decode when used in code.py works, mostly.

# What doesn't work
Currently, any receive protocol other than NEC, and any form of transmit. Each has to be adapted so that callbacks and interrupts are not required.


# Original readme:

# Device drivers for IR (infra red) remote controls

This repo provides a driver to receive from IR (infra red) remote controls and
a driver for IR "blaster" apps. The device drivers are nonblocking. They do not
require `uasyncio` but are compatible with it, and are designed for standard
firmware builds.

The receiver is cross platform and has been tested on Pyboard, ESP8266, ESP32
and Raspberry Pi Pico.

In a typical use case the receiver is employed at the REPL to sniff the address
and data values associated with buttons on a remote control. The transmitter is
then used in an application to send those codes, emulating the remote control.

Other use cases involve running the receiver in an application. This enables an
IR remote to control a device such as a robot.

## Raspberry Pi Pico note

Early firmware has [this issue](https://github.com/micropython/micropython/issues/6866)
affecting USB communication with some PC's. It particularly affects code which
issues `print()` only occasionally: the application appears to have failed. The
missing messages appear when you press a key. Hopefully this will be fixed soon
(note dated 8th March 2021).

#### [Receiver docs](./RECEIVER.md)

The transmitter driver is compatible with Pyboard (1.x and D series) and ESP32.
ESP8266 is unsupported; it seems incapable of generating the required signals.

#### [Transmitter docs](./TRANSMITTER.md)

# 1. IR communication

IR communication uses a carrier frequency to pulse the IR source. Modulation
takes the form of OOK (on-off keying). There are multiple protocols and at
least three options for carrier frequency: 36, 38 and 40KHz.

In the case of the transmitter the carrier frequency is a runtime parameter:
any value may be specified. The receiver uses a hardware demodulator which
should be purchased for the correct frequency. The receiver device driver sees
the demodulated signal and is hence carrier frequency agnostic.

Remotes transmit an address and a data byte, plus in some cases an extra value.
The address denotes the physical device being controlled. The data defines the
button on the remote. Provision usually exists for differentiating between a
button repeatedly pressed and one which is held down; the mechanism is protocol
dependent.

# 2. Supported protocols

The drivers support NEC and Sony protocols plus two Philips protocols, namely
RC-5 and RC-6 mode 0. There is also support for the OrtekMCE protocol used on
VRC-1100 remotes. These originally supported Microsoft Media Center but can be
used to control Kodi and (with a suitable receiver) to emulate a PC keyboard.

Examining waveforms from various remote controls it is evident that numerous
protocols exist. Some are doubtless proprietary and undocumented. The supported
protocols are those for which I managed to locate documentation. My preference
is for the NEC version. It has conservative timing and good provision for error
detection. RC-5 has limited error detection, and RC-6 mode 0 has rather fast
timing.

A remote using the NEC protocol is [this one](https://www.adafruit.com/products/389).

# 3. Hardware Requirements

These are discussed in detail in the relevant docs; the following provides an
overview.

The receiver is cross-platform. It requires an IR receiver chip to demodulate
the carrier. The chip must be selected for the frequency in use by the remote.
For 38KHz devices a receiver chip such as the Vishay TSOP4838 or the
[adafruit one](https://www.adafruit.com/products/157) is required. This
demodulates the 38KHz IR pulses and passes the demodulated pulse train to the
microcontroller.

In my testing a 38KHz demodulator worked with 36KHz and 40KHz remotes, but this
is obviously neither guaranteed nor optimal.

The transmitter requires a Pyboard 1.x (not Lite), a Pyboard D or an ESP32.
Output is via an IR LED which will need a transistor to provide sufficient
current. The ESP32 requires an extra transistor to work as a transmitter.

## 3.1 Carrier frequencies

These are as follows. The Samsung and Panasonic remotes appear to use
proprietary protocols and are not supported by these drivers.

| Protocol  | F KHz | How found     | Support |
|:---------:|:-----:|:-------------:|:-------:|
| NEC       | 38    | Measured      | Y       |
| RC-5 RC-6 | 36    | Spec/measured | Y       |
| Sony      | 40    | Spec/measured | Y       |
| MCE       | 38    | Measured      | Y       | 
| Samsung   | 38    | Measured      | N       |
| Panasonic | 36.3  | Measured      | N       |

# 4. References

Sources of information about IR protocols. The `sbprojects.net` site is an
excellent resource.  
[General information about IR](https://www.sbprojects.net/knowledge/ir/)

The NEC protocol:  
[altium](http://techdocs.altium.com/display/FPGA/NEC+Infrared+Transmission+Protocol)  
[circuitvalley](http://www.circuitvalley.com/2013/09/nec-protocol-ir-infrared-remote-control.html)
[sbprojects.net](https://www.sbprojects.net/knowledge/ir/nec.php)

Philips protocols:  
[RC5 Wikipedia](https://en.wikipedia.org/wiki/RC-5)  
[RC5 sbprojects.net](https://www.sbprojects.net/knowledge/ir/rc5.php)  
[RC6 sbprojects.net](https://www.sbprojects.net/knowledge/ir/rc6.php)

Sony protocol:  
[SIRC sbprojects.net](https://www.sbprojects.net/knowledge/ir/sirc.php)

MCE protocol:  
[OrtekMCE](http://www.hifi-remote.com/johnsfine/DecodeIR.html#OrtekMCE)

IR decoders (C sourcecode):  
[in the Linux kernel](https://github.com/torvalds/linux/tree/master/drivers/media/rc)
