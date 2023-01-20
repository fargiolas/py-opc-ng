import struct
from time import sleep

import logging

try:
    from usbiss.usbiss import USBISSError
except ImportError:
    class USBISSError(BaseException):
        pass

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


#
# Alphasense OPC commands and flags
#
_OPC_READY = 0xF3
_OPC_BUSY  = 0x31
# Most opcodes are shared among different device versions
_OPC_CMD_WRITE_POWER_STATE   = 0x03
_OPC_CMD_READ_POWER_STATE    = 0x13
_OPC_CMD_READ_INFO_STRING    = 0x3F
_OPC_CMD_READ_SERIAL_STRING  = 0x10
_OPC_CMD_READ_FW_VERSION     = 0x12
_OPC_CMD_READ_HISTOGRAM      = 0x30
_OPC_CMD_READ_PM             = 0x32
_OPC_CMD_READ_CONFIG         = 0x3C
_OPC_CMD_CHECK_STATUS        = 0xCF
_OPC_CMD_RESET               = 0x06
# OPC-N3 peripheral power status "OptionByte" flags. See 072-0503.
_OPC_N3_POPT_FAN_POT      = 1
_OPC_N3_POPT_LASER_POT    = 2
_OPC_N3_POPT_LASER_SWITCH = 3
_OPC_N3_POPT_GAIN_TOGGLE  = 4

# Most device queries return a list of bytes that must be
# decoded. Each device (N2, N3, R1) returns a specific set of data,
# differing in size, ordering and data types.

# The following lists define how this data is structured, both for
# reading (decoding) and for writing (encoding) data to an OPC device.
# Each model definition is a list of (field, fmt) pairs, with fmt in
# python struct notation

# N3 and N2 DAC and power state ("digital pot"), queries with 0x13. R1
# doesn't seem to support this command.
_OPC_N3_POPT_MODEL =      [['FanON',              'B'],
                           ['LaserON',            'B'],
                           ['FanDACVal',          'B'],
                           ['LaserDACVal',        'B'],
                           ['LaserSwitch',        'B'],
                           ['GainToggle',         'B']]

_OPC_N2_POPT_MODEL =      [['FanON',              'B'],
                           ['LaserON',            'B'],
                           ['FanDACVal',          'B'],
                           ['LaserDACVal',        'B']]

# Histogram structs
_OPC_N2_HISTOGRAM_MODEL = [['Bin 0',              'H'],
                           ['Bin 1',              'H'],
                           ['Bin 2',              'H'],
                           ['Bin 3',              'H'],
                           ['Bin 4',              'H'],
                           ['Bin 5',              'H'],
                           ['Bin 6',              'H'],
                           ['Bin 7',              'H'],
                           ['Bin 8',              'H'],
                           ['Bin 9',              'H'],
                           ['Bin 10',             'H'],
                           ['Bin 11',             'H'],
                           ['Bin 12',             'H'],
                           ['Bin 13',             'H'],
                           ['Bin 14',             'H'],
                           ['Bin 15',             'H'],
                           ['Bin1 MToF',          'B'],
                           ['Bin3 MToF',          'B'],
                           ['Bin5 MToF',          'B'],
                           ['Bin7 MToF',          'B'],
                           ['SFR',                'f'],
                           ['Temperature',        'L'],
                           ['Sampling Period',    'f'],
                           ['Checksum',           'H'],
                           ['PM1',                'f'],
                           ['PM2.5',              'f'],
                           ['PM10',               'f']]

# [*[['Bin {}'.format(b), t] for b, t in zip(range(24), ["H"]*24)],
_OPC_N3_HISTOGRAM_MODEL = [['Bin 0',              'H'],
                           ['Bin 1',              'H'],
                           ['Bin 2',              'H'],
                           ['Bin 3',              'H'],
                           ['Bin 4',              'H'],
                           ['Bin 5',              'H'],
                           ['Bin 6',              'H'],
                           ['Bin 7',              'H'],
                           ['Bin 8',              'H'],
                           ['Bin 9',              'H'],
                           ['Bin 10',             'H'],
                           ['Bin 11',             'H'],
                           ['Bin 12',             'H'],
                           ['Bin 13',             'H'],
                           ['Bin 14',             'H'],
                           ['Bin 15',             'H'],
                           ['Bin 16',             'H'],
                           ['Bin 17',             'H'],
                           ['Bin 18',             'H'],
                           ['Bin 19',             'H'],
                           ['Bin 20',             'H'],
                           ['Bin 21',             'H'],
                           ['Bin 22',             'H'],
                           ['Bin 23',             'H'],
                           ['Bin1 MToF',          'B'],
                           ['Bin3 MToF',          'B'],
                           ['Bin5 MToF',          'B'],
                           ['Bin7 MToF',          'B'],
                           ['Sampling Period',    'H'],
                           ['SFR',                'H'],
                           ['Temperature',        'H'],
                           ['Relative humidity',  'H'],
                           ['PM1',                'f'],
                           ['PM2.5',              'f'],
                           ['PM10',               'f'],
                           ['#RejectGlitch',      'H'],
                           ['#RejectLongTOF',     'H'],
                           ['#RejectRatio',       'H'],
                           ['#RejectOutOfRange',  'H'],
                           ['Fan rev count',      'H'],
                           ['Laser status',       'H'],
                           ['Checksum',           'H']]

_OPC_R1_HISTOGRAM_MODEL = [['Bin 0',              'H'],
                           ['Bin 1',              'H'],
                           ['Bin 2',              'H'],
                           ['Bin 3',              'H'],
                           ['Bin 4',              'H'],
                           ['Bin 5',              'H'],
                           ['Bin 6',              'H'],
                           ['Bin 7',              'H'],
                           ['Bin 8',              'H'],
                           ['Bin 9',              'H'],
                           ['Bin 10',             'H'],
                           ['Bin 11',             'H'],
                           ['Bin 12',             'H'],
                           ['Bin 13',             'H'],
                           ['Bin 14',             'H'],
                           ['Bin 15',             'H'],
                           ['Bin1 MToF',          'B'],
                           ['Bin3 MToF',          'B'],
                           ['Bin5 MToF',          'B'],
                           ['Bin7 MToF',          'B'],
                           ['SFR',                'f'],
                           ['Temperature',        'H'],
                           ['Relative humidity',  'H'],
                           ['Sampling Period',    'f'],
                           ['#RejectGlitch',      'B'],
                           ['#RejectLongTOF',     'B'],
                           ['PM1',                'f'],
                           ['PM2.5',              'f'],
                           ['PM10',               'f'],
                           ['Checksum',           'H']]

# Particle Mass loadings models, no checksum for N2
_OPC_N2_PM_MODEL =        [['PM1',                'f'],
                           ['PM2.5',              'f'],
                           ['PM10',               'f']]

_OPC_N3_PM_MODEL =        [['PM1',                'f'],
                           ['PM2.5',              'f'],
                           ['PM10',               'f'],
                           ['Checksum',           'H']]

_OPC_R1_PM_MODEL = _OPC_N3_PM_MODEL


# Config variables
_OPC_N3_CONFIG_MODEL =    [*[['BB{}'.format(b), t] for b, t in zip(range(25), ["H"] * 25)],
                           *[['BBD{}'.format(b), t] for b, t in zip(range(25), ["H"] * 25)],
                           *[['BW{}'.format(b), t] for b, t in zip(range(24), ["H"] * 24)],
                           ['M_A',                'H'],
                           ['M_B',                'H'],
                           ['M_C',                'H'],
                           ['MaxTOF',             'H'],
                           ['AMSamplingIntervalCount', 'H'],
                           ['AMIdleIntervalCount', 'H'],
                           ['AMMaxDataArraysInFile', 'H'],
                           ['AMOnlySavePMData',   'B'],
                           ['AMFanOnInIdle',      'B'],
                           ['AMLaserOnInIdle',    'B'],
                           ['TOF to SFR factor',  'B'],
                           ['PVP',                'B'],
                           ['BinWeightingIndex',  'B']]


class _data_model(object):
    """Helper class to manage a data sequence to be read or written
    sequentially to the OPC using SPI. Mostly caches struct size,
    fields and complete format string.
    """
    def __init__(self, model):
        self.model = model
        self.fields = [field for field, fmt in self.model]
        self.fmt = '<' + ''.join([fmt for field, fmt in self.model])
        self.size = struct.calcsize(self.fmt)

    def unpack(self, raw_bytes):
        assert(len(raw_bytes) == self.size)

        values = struct.unpack_from(self.fmt, raw_bytes)

        return dict(zip(self.fields, values))


class _OPCError(IOError):
    pass


class _OPC(object):
    """OPC Base class, handle common logic among different devices.

    :param spi: a SPI device as returned by SpiDev or USBiss
    """
    def __init__(self, spi):
        self.spi = spi

    def _send_command(self, cmd, interval=10e-6):
        """Send a single command through the SPI bus.
        :param cmd: command opcode (single byte)
        :param interval: seconds to sleep after sending a command (default: 10us)
        """
        r = self.spi.xfer([cmd])[0]
        logger.debug('command: 0x{:02X}, response: 0x{:02X},  sleep: {} s'.format(cmd, r, interval))
        sleep(interval)
        return r

    def _send_command_and_wait(self, cmd):
        """OPC-N3 and R1 always return _OPC_BUSY after sending a command.  The
        device keeps returning _OPC_BUSY until it's completed the
        requested operation or ready for sending or receiving a data
        sequence. At this point it returns _OPC_READY.  OPC-N2 always
        returns _OPC_READY so it should work transparently by just
        skipping the busy/waiting logic.

        Raises an exception if the device gives bogus responses or if
        it stays busy for too much time (maximum timeout: ~25 seconds)

        :param cmd: command opcode (single byte)

        """
        r = _OPC_BUSY
        attempts = 0

        while (r != _OPC_READY):
            # The first returned byte should always be 0x31 (busy). Subsequent returned bytes will
            # either be 0x31 (busy) or 0xF3 (ready) depending on the status of the OPC-N3. If
            # another byte value is received by the SPI master at this stage, an error has occurred
            # and communication should cease for > 2s to allow the OPC-N3 to realise the error and
            # clear its buffered data. [Alphasense 072-0502]
            if r != _OPC_BUSY:
                # wait for the device to settle
                sleep(5)
                raise _OPCError("Received unexpected response 0x{:02X} for command: 0x{:02X}".format(r, cmd))

            if attempts > 20:
                # if this cycle has happened many times, e.g. 20, wait > 2s ( < 10s) for OPC's SPI
                # buffer to reset [Alphasense 072-0503]
                logger.warning("Device not responding, waiting for 5s for the SPI buffer to reset")
                sleep(5)

            if attempts > 25:
                # this is not described by Alphasense manuals but I've seen it happen with N3
                raise _OPCError("Timeout after sending command: 0x{:02X}".format(cmd))

            # wait > 10 ms (< 100 ms)
            r = self._send_command(cmd, interval=0.02)

            attempts = attempts + 1

    def _read_bytes(self, cmd, sz):
        """Read a sequence of bytes.

        :param cmd: command opcode
        :param sz: number of bytes to read
        """
        buf = []
        try:
            self._send_command_and_wait(cmd)
            for i in range(sz):
                buf += [self._send_command(cmd)]

        except _OPCError as e:
            logger.error("Error while reading bytes from the device: {}".format(e))
        except USBISSError as e:
            logger.error("USB-SPI communication error: {}".format(e))
            logger.warning("Waiting 5 seconds for the device to settle")
            sleep(5)

        result = bytearray(buf)
        if len(result) < sz:
            logger.error('Something failed while reading byte sequence, expected size: {}, received: {}'.format(sz, len(result)))

        return result

    def _write_bytes(self, cmd, buf):
        """Write a sequence of bytes.

        :param cmd: command opcode
        :param buf: list of bytes to send
        """
        try:
            self._send_command_and_wait(cmd)
            for c in buf:
                self._send_command(c)
        except _OPCError as e:
            logger.error("Error while reading bytes from the device: {}".format(e))
        except USBISSError as e:
            logger.error("USB-SPI communication error: {}".format(e))
            logger.warning("Waiting 5 seconds for the device to settle")
            sleep(5)

    def _read_struct(self, cmd, model):
        """Read a complex data structure (e.g. an histogram) from the
        device. If appliable calculate data checksum and return None if it
        fails.

        :param cmd: command opcode
        :param m: data structure definition

        :returns: dictionary filled with the struct data
        """
        raw_bytes = self._read_bytes(cmd, model.size)

        if len(raw_bytes) < model.size:
            logger.error('Bad histogram data, size mismatch')
            return None

        data = model.unpack(raw_bytes)

        if 'Checksum' in model.fields:
            crc = self._checksum(data, raw_bytes)
            if data['Checksum'] != crc:
                logger.warning('Bad histogram data, invalid checksum')
                return None

        return data

    def _convert_temperature(self, x):
        """Convert temperature to °C"""
        return -45. + 175. * x / (float(1 << 16) - 1.)

    def _convert_humidity(self, x):
        """Convert relative humidity to percentage"""
        return 100. * x / (float(1 << 16) - 1.)

    def _convert_hist_to_count_per_ml(self, hist):
        """Convert counts/s to counts/ml using flow rate and sampling period.

        Modifies histogram bins in-place.
        """
        ml_per_period = hist['SFR'] * hist['Sampling Period']
        if ml_per_period > 0:
            for field in self._histogram_model.fields:
                if 'Bin ' in field:
                    hist[field] = hist[field] / ml_per_period

        return hist

    def _convert_mtof(self, hist):
        """Convert MToF from 1/3us units.

        Modifies MToF bins in-place"""
        for field in self._histogram_model.fields:
            if 'MToF' in field:
                hist[field] = hist[field] / 3.
        return hist

    def info(self):
        """Query device information"""
        buf = self._read_bytes(_OPC_CMD_READ_INFO_STRING, 60)
        return buf.decode()

    def serial(self):
        """Query device serial"""
        buf = self._read_bytes(_OPC_CMD_READ_SERIAL_STRING, 60)
        return buf.decode()

    def fwversion(self):
        """Query device firmware version"""
        major, minor = self._read_bytes(_OPC_CMD_READ_FW_VERSION, 2)
        return major, minor

    def ping(self):
        """Check device status. Returns True if the device is responding."""
        try:
            self._send_command_and_wait(_OPC_CMD_CHECK_STATUS)
            return True
        except BaseException:
            return False

    def _checksum(self, data, raw_bytes):
        """Checksum calculation for OPC-N3 and R1. See e.g. Appendix E,
        Alphasense manual 072-0502. Python translation of their C code.
        """
        # the following only works for N3 and R1, N2 is different and
        # should override this
        raw_bytes = raw_bytes[:-2]
        poly = 0xA001
        init_crc_val = 0xFFFF

        crc = init_crc_val

        for i in range(len(raw_bytes)):
            crc ^= raw_bytes[i]
            for bit in range(8):
                if (crc & 1):
                    crc >>= 1
                    crc ^= poly
                else:
                    crc >>= 1

        return crc

    def histogram(self, raw=False):
        """Query and decode histogram data.

        :param raw: if True do not post process data (e.g. converting
                    raw temperature to degrees etc.) and return raw
                    numbers instead.

        :returns: a dictionary of histogram bins and auxiliary data
        """
        data = self._read_struct(_OPC_CMD_READ_HISTOGRAM, self._histogram_model)
        if raw or (data is None):
            return data
        else:
            return self._histogram_post_process(data)

    def pm(self):
        """Query particle mass loadings.

        :returns: a dictionary containing PM1, PM2.5 and PM10 data.
        """
        return self._read_struct(_OPC_CMD_READ_PM, self._pm_model)


class OPCN3(_OPC):
    """OPC-N3

    :param spi: a SPI device as returned by SpiDev or USBiss
    """
    def __init__(self, spi):
        super().__init__(spi)

        self._histogram_model = _data_model(_OPC_N3_HISTOGRAM_MODEL)
        self._popt_model = _data_model(_OPC_N3_POPT_MODEL)
        self._pm_model = _data_model(_OPC_N3_PM_MODEL)
        self._config_model = _data_model(_OPC_N3_CONFIG_MODEL)

    def power_state(self):
        """Report peripherals and digital pots state.

        :returns: a dictionary of each peripheral current state.
        :Example:

        >>> o = OPCN3(spi)
        >>> o.power_state()
        {'FanON': 0,
         'LaserON': 1,
         'FanDACVal': 255,
         'LaserDACVal': 140,
         'LaserSwitch': 0,
         'GainToggle': 3}
        """
        return self._read_struct(_OPC_CMD_READ_POWER_STATE, self._popt_model)

    # Turn peripherals on/off. POPT flag, left shifted by 1 selects
    # the proper digital pot/switch, LSB sets its state, 0 for off, 1
    # for on.
    def fan_off(self):
        """Power off fan."""
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [_OPC_N3_POPT_FAN_POT << 1 | 0])

    def fan_on(self):
        """Power on fan.

        Wait at least 600ms for the fan speed to settle and power
        absorption peak to pass before sending more commands.

        """
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [_OPC_N3_POPT_FAN_POT << 1 | 1])

    def laser_off(self):
        """Power off laser."""
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [_OPC_N3_POPT_LASER_SWITCH << 1 | 0])

    def laser_on(self):
        """Power on laser."""
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [_OPC_N3_POPT_LASER_SWITCH << 1 | 1])

    def on(self):
        """Power on peripherals (both laser and fan).

        Wait at least 600ms for the fan speed to settle and power
        absorption peak to pass before sending more commands.

        """
        self.laser_on()
        self.fan_on()

    def off(self):
        """Power off peripherals (both laser and fan)."""
        self.laser_off()
        self.fan_off()

    def reset(self):
        """Reset device.

        Not so clear what it really does, poorly documented in
        manufacturer docs.

        """
        self._send_command_and_wait(_OPC_CMD_RESET)

    def _histogram_post_process(self, hist):
        """Convert histogram raw data into proper measurements."""
        hist['Temperature'] = self._convert_temperature(hist['Temperature'])
        hist['Relative humidity'] = self._convert_humidity(hist['Relative humidity'])

        hist['Sampling Period'] = hist['Sampling Period'] / 100.
        hist['SFR'] = hist['SFR'] / 100.

        hist = self._convert_hist_to_count_per_ml(hist)
        hist = self._convert_mtof(hist)

        return hist

    def config(self):
        """Query configuration variables."""
        return self._read_struct(_OPC_CMD_READ_CONFIG, self._config_model)


class OPCR1(_OPC):
    """OPC-R1

    :param spi: a SPI device as returned by SpiDev or USBiss
    """
    def __init__(self, spi):
        super().__init__(spi)

        self._histogram_model = _data_model(_OPC_R1_HISTOGRAM_MODEL)
        self._pm_model = _data_model(_OPC_R1_PM_MODEL)

    def on(self):
        """Power on peripherals (both laser and fan).

        Wait at least 600ms for the fan speed to settle and power
        absorption peak to pass before sending more commands.

        """
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [0x03])

    def off(self):
        """Power off peripherals (both laser and fan)."""

        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [0x00])

    def reset(self):
        """Reset device.

        Not so clear what it really does, poorly documented in
        manufacturer docs.

        """
        return self._send_command_and_wait(_OPC_CMD_RESET)

    def _histogram_post_process(self, hist):
        """Convert histogram raw data into proper measurements."""
        hist['Temperature'] = self._convert_temperature(hist['Temperature'])
        hist['Relative humidity'] = self._convert_humidity(hist['Relative humidity'])

        hist = self._convert_hist_to_count_per_ml(hist)
        hist = self._convert_mtof(hist)

        return hist


class OPCR2(OPCR1):
    def pm(self):
        """Query particle mass readings."""
        major, minor = super().fwversion()
        if (major <= 2) and (minor < 82):
            logger.warning('Querying PM from full histogram.')
            logger.warning('READ_PM command does not work on firmwares before 2.82.')
            logger.warning('Please consider a firmware upgrade.')
            logger.warning('Contact Alphasense for more info.')
            hist = super().histogram()
            return {k: v for k, v in hist.items() if k in ["PM1", "PM2.5", "PM10"]}
        else:
            return super().pm()


class OPCN2(_OPC):
    """OPC-N2

    Experimental support, only tested with firmware 18

    :param spi: a SPI device as returned by SpiDev or USBiss
    """
    def __init__(self, spi):
        super().__init__(spi)

        self._histogram_model = _data_model(_OPC_N2_HISTOGRAM_MODEL)
        self._popt_model = _data_model(_OPC_N2_POPT_MODEL)
        self._pm_model = _data_model(_OPC_N2_PM_MODEL)

    def on(self):
        """Power on peripherals (laser and fan).

        Wait at least 600ms for the fan speed to settle and power absorption
        peak to pass before sending more commands.

        """
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [0x00])

    def off(self):
        """Power off peripherals."""
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [0x01])

    def power_state(self):
        """Report peripherals and digital pots state.

        :returns: a dictionary of each peripheral current state.
        :Example:

        >>> o = OPCN2(spi)
        >>> o.power_state()
        {'FanON': 1, 'LaserON': 1, 'FanDACVal': 255, 'LaserDACVal': 164}
        """
        return self._read_struct(_OPC_CMD_READ_POWER_STATE, self._popt_model)

    def _checksum(self, data, raw_bytes):
        """Checksum calculation for OPC-N2.

        Return least significant 16bits of histogram bin sum.
        """
        bins = [data[k] for k in data.keys() if 'Bin ' in k]
        binsum = 0
        for b in bins:
            binsum += b

        # checksum is the least significant dword of the binned data sum
        return binsum & 0xFFFF

    def _histogram_post_process(self, hist):
        """Convert raw histogram data to measurements."""

        # Temperature is an odd beast here, can alternatively report
        # Temperature and Pressure but on my devices it always returns
        # 10000 which should be considered invalid. Guess not all the
        # units have these sensors? Disabling it anyway.

        # hist['Temperature'] = self._convert_temperature(hist['Temperature'])

        hist = self._convert_hist_to_count_per_ml(hist)
        hist = self._convert_mtof(hist)

        return hist


def detect(spi):
    """Try to autodetect a device parsing information string

    :param spi: SPI device instance as returned by SpiDev or USBiss

    :returns: an OPC_(N3,N2,R1,R2) instance, check type() to see if the device was properly detected.
    """
    o = _OPC(spi)
    info = o.info()
    logger.info('Detecting device type from info string: "{}"'.format(info))
    if "OPC-N3" in info:
        o = OPCN3(spi)
    elif "OPC-R1" in info:
        o = OPCR1(spi)
    elif "OPC-R2" in info:
        o = OPCR2(spi)
    elif "OPC-N2" in info:
        o = OPCN2(spi)
    else:
        o = None

    if o:
        logger.info('Detected an istance of: {}'.format(type(o)))
    else:
        logger.error('Could not detect a valid OPC device')
    return o
