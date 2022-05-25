Introduction
============

**py-opc-ng** is a small Python module to drive Alphasense Optical Particle Counters.

We currently support OPC-N2, OPC-N3, OPC-R1 and OPC-R2. The library
doesn't aim to be feature complete but provides support for most comon
operations: turning on and off the device and the internal
peripherals, querying device information, querying histograms and
particle mass loadings readings.

Feedback, `bug reports`_ and `pull requests`_ to extend the module
beyond this basic functionality are more than welcome. Or just drop me
an email at filippo.argiolas@gmail.com if you need help or have any feedback.

.. _bug reports: https://github.com/fargiolas/py-opc-ng/issues
.. _pull requests: https://github.com/fargiolas/py-opc-ng/pulls

Installation
============

.. code-block:: bash

   $ pip install py-opc-ng


Requirements
------------

The devices work with SPI interface. You can either connect them
directly to a SPI bus using
`py-spidev <https://github.com/doceme/py-spidev>`_ (e.g. with the GPIO
pins of a Raspberry Pi) or use a SPI to USB device, like the one
Alphasense provides, using the
`pyusbiss <https://github.com/dancingquanta/pyusbiss>`_ library.

Examples
========

Opening a SPI channel
---------------------

You first need a SPI interface. This can be either a direct one,
e.g. from the MISO/MOSI headers in a RaspberryPi, or you can use a SPI
to USB converters like the ones provided by Alphasense.

You can open a direct SPI connection with `spidev <https://github.com/doceme/py-spidev>`_::

   import spidev

   spi = spidev.SpiDev()
   spi.open(0, 0)
   spi.mode = 1
   spi.max_speed_hz = 500000
   spi.lsbfirst = False

Or you can use `pyusbiss <https://github.com/dancingquanta/pyusbiss>`_ if you have a SPI to USB converter::

   from usbiss.spi import SPI

   spi = SPI('/dev/ttyACM0')
   spi.mode = 1
   spi.max_speed_hz = 500000
   spi.lsbfirst = False


Reading PM data
---------------

Basic steps to operate the device and read some measurement::

   from time import sleep
   import opcng as opc

   # autodetect device
   dev = opc.detect(spi)

   # power on fan and laser
   dev.on()

   sleep(1)

   for i in range(10):
       # query particle mass readings
       pm = dev.pm()

       for k, v in pm.items():
           print(f'{k}: {v}')

       sleep(1)

   # power off fan and laser
   dev.off()


Querying device information
---------------------------

Here's an example session where we read both metadata and histogram
data from one of our OPC-N3:

>>> import opcng as opc
>>> dev = opc.OPCN3(spi)
>>> dev.info()        # query information string
'OPC-N3 Iss1.1 FirmwareVer=1.17a...........................BS'
>>> dev.fwversion()   # firmware version
(1, 17)
>>> dev.serial()      # serial number
'OPC-N3 177700019                                            '
>>> dev.power_state() # power state (only available for N2 and N3)
{ 'FanON': 0,
  'LaserON': 1,
  'FanDACVal': 255,
  'LaserDACVal': 140,
  'LaserSwitch': 0,
  'GainToggle': 3 }
>>> dev.on()
>>> dev.power_state() # power state after turning it on
{ 'FanON': 1,
  'LaserON': 1,
  'FanDACVal': 255,
  'LaserDACVal': 140,
  'LaserSwitch': 1,
  'GainToggle': 3 }
>>> dev.histogram()   # full histogram data
{ 'Bin 0': 1.883357398455647,
  'Bin 1': 0.4185238663234771,
  'Bin 2': 0.20926193316173855,
  'Bin 3': 0.0,
  'Bin 4': 0.0,
  'Bin 5': 0.20926193316173855,
  'Bin 6': 0.0,
  'Bin 7': 0.0,
  'Bin 8': 0.0,
  'Bin 9': 0.0,
  'Bin 10': 0.0,
  'Bin 11': 0.0,
  'Bin 12': 0.0,
  'Bin 13': 0.0,
  'Bin 14': 0.0,
  'Bin 15': 0.0,
  'Bin 16': 0.0,
  'Bin 17': 0.0,
  'Bin 18': 0.0,
  'Bin 19': 0.0,
  'Bin 20': 0.0,
  'Bin 21': 0.0,
  'Bin 22': 0.0,
  'Bin 23': 0.0,
  'Bin1 MToF': 5.0,
  'Bin3 MToF': 0.0,
  'Bin5 MToF': 10.666666666666666,
  'Bin7 MToF': 0.0,
  'Sampling Period': 0.51,
  'SFR': 9.37,
  'Temperature': 31.22453650720989,
  'Relative humidity': 40.822461280231934,
  'PM1': 0.29056867957115173,
  'PM2.5': 1.235719919204712,
  'PM10': 1.6337664127349854,
  '#RejectGlitch': 9,
  '#RejectLongTOF': 0,
  '#RejectRatio': 2335,
  '#RejectOutOfRange': 3,
  'Fan rev count': 0,
  'Laser status': 613,
  'Checksum': 35040 }

