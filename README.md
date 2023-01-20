# py-opc-ng

A small python library to operate Alphasense OPC devices.

Supports most modern OPC devices: OPC-N2, OPC-N3, OPC-R1 and OPC-R2.

## Installation

    $ pip install py-opc-ng

## Dependencies

The devices work with SPI interface. You can either connect them
directly to a SPI bus using
[`py-spidev`](https://github.com/doceme/py-spidev) (e.g. with the GPIO
pins of a RaspberryPi) or use a SPI to USB device, like the one
Alphasense provides, using the
[`pyusbiss`](https://github.com/dancingquanta/pyusbiss) library.

## Getting help

You can find full documentation, including API references, at http://py-opc-ng.readthedocs.io/

## Usage

With a direct SPI connection:

```python
from time import sleep
import spidev
import opcng as opc

spi = spidev.SpiDev()
spi.open(0, 0)
spi.mode = 1
spi.max_speed_hz = 500000
spi.lsbfirst = False

dev = opc.detect(spi)

print(f'device information: {dev.info()}')
print(f'serial: {dev.serial()}')
print(f'firmware version: {dev.serial()}')

# power on fan and laser
dev.on()

for i in range(10):
    # query particle mass readings
    sleep(1)
    print(dev.pm())

# power off fan and laser
dev.off()
```

or with a SPI to USB bridge:

```python
from time import sleep
from usbiss.spi import SPI
import opcng as opc

spi = SPI('/dev/ttyACM0')
spi.mode = 1
spi.max_speed_hz = 500000
spi.lsbfirst = False

dev = opc.detect(spi)

print(f'device information: {dev.info()}')
print(f'serial: {dev.serial()}')
print(f'firmware version: {dev.serial()}')

# power on fan and laser
dev.on()

for i in range(10):
    # query particle mass readings
    sleep(1)
    print(dev.pm())

# power off fan and laser
dev.off()
```

## Known issues

OPC N2 and N3 have a so-called *autonomous mode* where the device
operates on its own saving data in the included sd-card. When you
power on the devices and don't do anything for some time (about 65s
for N3) the automatically enter this standalone mode and start
acquiring data. See e.g. Chapter 9 in OPC N3 manual.

When this happens the device still listens for SPI commands but
sometimes (most of the time?) fails to respond and behaves erratically.

When you try to access the device while in this mode you may get
errors like:

```
>>> opc.detect()
ERROR:opcng:Error while reading bytes from the device: Received unexpected response 0x00 for command: 0x3F
ERROR:opcng:Something failed while reading byte sequence, expected size: 60, received: 0
ERROR:opcng:Could not detect a valid OPC device
```

I don't have a solution yet, see discussion in issue #1. The solution
is do not let the device enter this mode. As soon as you power up your
host or connect the OPC send some SPI command to prevent this
autonomous mode. If it enters it before you have the chance to
interact with it the best way out is to power cycle the device or
reboot the host.

Not much of an issue as these are devices that should be operated
continously so you should start them as soon as you boot your host.

Nonetheless, if you know a way to disable this mode please do let me
know.

## A note about the name

When this project was started the most popular library to operate
Alphasense OPC devices was
[`py-opc`](https://github.com/dhagan/py-opc). At the time it only
supported OPC-N2 and had a lot of code very specific to that device
generation.

Adding support for next generation (hence the `-ng`) devices there
seemed to require quite some effort. We wanted to abstract common
characteristics of the different devices in a single interface right
from the start. We also didn't want to support all the quirks they had
for N2 different firmware versions as we were already moving away
from N2 devices.

So we opted to start a completely new project. It's not a fork and
doesn't share any code with
[`py-opc`](https://github.com/dhagan/py-opc).


## License

This module is licensed under the GNU Lesser General Public License
Version 3. Full text can be found in the LICENSE file.


## Acknowledgement
This package was developed within the Cagliari2020 project with the support of [Istituto Nazionale di Fisica Nucleare (INFN)](http://home.infn.it/en/)
