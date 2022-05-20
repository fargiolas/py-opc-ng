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

   import opcng as opc

   # autodetect device
   dev = opc.detect(spi)

   # power on fan and laser
   dev.on()

   for i in range(10):
       # query particle mass readings
       sleep(1)
       pm = dev.pm()

       for k, v in pm.items():
           print(f'{k}: {v}')

   # power off fan and laser
   dev.off()
