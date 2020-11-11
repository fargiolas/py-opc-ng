import struct
from time import sleep

try:
    from usbiss.usbiss import USBISSError
except:
    class USBISSError(BaseException):
        pass


# Alphasense OPC commands and flags
_OPC_READY = 0xF3
_OPC_BUSY  = 0x31

# Most opcodes are shared amongst the various device versions
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
# decoded. Each device (N2, N3, R1) return a specific set of data,
# differing in size, ordering and data types.

# The following lists define how this data is structured, both for
# reading (decoding) and for writing (encoding) data to an OPC device.

# N3 and N2 DAC and power state ("digital pot"), queries with 0x13. R1
# doesn't seem to support this command.
_OPC_N3_POPT_STRUCT =      [['FanON',               'uint8'],
                           ['LaserON',             'uint8'],
                           ['FanDACVal',           'uint8'],
                           ['LaserDACVal',         'uint8'],
                           ['LaserSwitch',         'uint8'],
                           ['GainToggle',          'uint8']]

_OPC_N2_POPT_STRUCT =      [['FanON',               'uint8'],
                           ['LaserON',             'uint8'],
                           ['FanDACVal',           'uint8'],
                           ['LaserDACVal',         'uint8']]

# Histogram structs
_OPC_N2_HISTOGRAM_STRUCT = [['Bin 0',              'uint16'],
                           ['Bin 1',              'uint16'],
                           ['Bin 2',              'uint16'],
                           ['Bin 3',              'uint16'],
                           ['Bin 4',              'uint16'],
                           ['Bin 5',              'uint16'],
                           ['Bin 6',              'uint16'],
                           ['Bin 7',              'uint16'],
                           ['Bin 8',              'uint16'],
                           ['Bin 9',              'uint16'],
                           ['Bin 10',             'uint16'],
                           ['Bin 11',             'uint16'],
                           ['Bin 12',             'uint16'],
                           ['Bin 13',             'uint16'],
                           ['Bin 14',             'uint16'],
                           ['Bin 15',             'uint16'],
                           ['Bin1 MToF',           'uint8'],
                           ['Bin3 MToF',           'uint8'],
                           ['Bin5 MToF',           'uint8'],
                           ['Bin7 MToF',           'uint8'],
                           ['SFR',               'float32'],
                           ['Temperature',        'uint32'],
                           ['Sampling Period' ,  'float32'],
                           ['Checksum',           'uint16'],
                           ['PM1',               'float32'],
                           ['PM2.5',             'float32'],
                           ['PM10',              'float32']]

#[*[['Bin {}'.format(b), t] for b, t in zip(range(24), ["uint16"]*24)],
_OPC_N3_HISTOGRAM_STRUCT = [['Bin 0',              'uint16'],
                           ['Bin 1',              'uint16'],
                           ['Bin 2',              'uint16'],
                           ['Bin 3',              'uint16'],
                           ['Bin 4',              'uint16'],
                           ['Bin 5',              'uint16'],
                           ['Bin 6',              'uint16'],
                           ['Bin 7',              'uint16'],
                           ['Bin 8',              'uint16'],
                           ['Bin 9',              'uint16'],
                           ['Bin 10',             'uint16'],
                           ['Bin 11',             'uint16'],
                           ['Bin 12',             'uint16'],
                           ['Bin 13',             'uint16'],
                           ['Bin 14',             'uint16'],
                           ['Bin 15',             'uint16'],
                           ['Bin 16',             'uint16'],
                           ['Bin 17',             'uint16'],
                           ['Bin 18',             'uint16'],
                           ['Bin 19',             'uint16'],
                           ['Bin 20',             'uint16'],
                           ['Bin 21',             'uint16'],
                           ['Bin 22',             'uint16'],
                           ['Bin 23',             'uint16'],
                           ['Bin1 MToF',           'uint8'],
                           ['Bin3 MToF',           'uint8'],
                           ['Bin5 MToF',           'uint8'],
                           ['Bin7 MToF',           'uint8'],
                           ['Sampling Period' ,   'uint16'],
                           ['SFR',                'uint16'],
                           ['Temperature',        'uint16'],
                           ['Relative humidity',  'uint16'],
                           ['PM1',               'float32'],
                           ['PM2.5',             'float32'],
                           ['PM10',              'float32'],
                           ['#RejectGlitch',      'uint16'],
                           ['#RejectLongTOF',     'uint16'],
                           ['#RejectRatio',       'uint16'],
                           ['#RejectOutOfRange',  'uint16'],
                           ['Fan rev count',      'uint16'],
                           ['Laser status',       'uint16'],
                           ['Checksum',           'uint16']]

_OPC_R1_HISTOGRAM_STRUCT = [['Bin 0',              'uint16'],
                           ['Bin 1',              'uint16'],
                           ['Bin 2',              'uint16'],
                           ['Bin 3',              'uint16'],
                           ['Bin 4',              'uint16'],
                           ['Bin 5',              'uint16'],
                           ['Bin 6',              'uint16'],
                           ['Bin 7',              'uint16'],
                           ['Bin 8',              'uint16'],
                           ['Bin 9',              'uint16'],
                           ['Bin 10',             'uint16'],
                           ['Bin 11',             'uint16'],
                           ['Bin 12',             'uint16'],
                           ['Bin 13',             'uint16'],
                           ['Bin 14',             'uint16'],
                           ['Bin 15',             'uint16'],
                           ['Bin1 MToF',           'uint8'],
                           ['Bin3 MToF',           'uint8'],
                           ['Bin5 MToF',           'uint8'],
                           ['Bin7 MToF',           'uint8'],
                           ['SFR',               'float32'],
                           ['Temperature',        'uint16'],
                           ['Relative humidity',  'uint16'],
                           ['Sampling Period' ,  'float32'],
                           ['#RejectGlitch',       'uint8'],
                           ['#RejectLongTOF',      'uint8'],
                           ['PM1',               'float32'],
                           ['PM2.5',             'float32'],
                           ['PM10',              'float32'],
                           ['Checksum',           'uint16']]


# Particle Mass loadings struct
_OPC_N2_PM_STRUCT =        [['PM1',               'float32'],
                           ['PM2.5',             'float32'],
                           ['PM10',              'float32']]

_OPC_N3_PM_STRUCT =        [['PM1',               'float32'],
                           ['PM2.5',             'float32'],
                           ['PM10',              'float32'],
                           ['Checksum',           'uint16']]

_OPC_R1_PM_STRUCT = _OPC_N3_PM_STRUCT


# Data struct encoding/decoding helper functions
def _unpack(t, x):
    """Helper function to convert a list of bytes as returned from an the
    device into a number with the proper datatype. 

    :param t: datatype (e.g. 'uint8', 'float32', ...)
    """
    if t == 'uint8':
        return x[0]
    elif t == 'uint16':
        return (x[1] << 8) | x[0]
    elif t == 'uint32':
        r  = (x[3] << 24) | (x[2] << 16) | (x[1] << 8) | x[0]
        return r
    elif t == 'float32':
        return struct.unpack('f', struct.pack('4B', *x))[0]
    else:
        raise ValueError

def _len(t):
    """Returns the size in bytes of a given datatype

    :param t: datatype (e.g. 'uint8', 'float32')
    """
    if t == 'uint8':
        return 1
    elif t == 'uint16':
        return 2
    elif t == 'uint32':
        return 4
    elif t == 'float32':
        return 4
    else:
        raise ValueError


class _data_struct(object):
    """Helper class to manage a data sequence to be read or written
    sequentially to the OPC using SPI. Mostly caches struct size and
    dictionary keys to void unnecessary looping each time they're
    neede.

    """
    def __init__(self, m):
        self.data_struct = m
        self.size = self._struct_size(self.data_struct)
        self.keys = self._keys()

    def _struct_size(self, m):
        l = 0
        for k, t in m:
            l += _len(t)
        return l

    def _keys(self):
        return [k for k, t in self.data_struct]

    def unpack(self, raw_bytes):
        assert(len(raw_bytes) == self.size)

        data = dict()
        c = 0
        for k, t in self.data_struct:
            l = _len(t)
            data[k] = _unpack(t, raw_bytes[c:c+l])
            c += l

        return data

class OPCError(IOError):
    pass

class _OPC(object):
    """OPC Base class, holds common logic amongst different device

    :param spi: a SPI device as returned by SpiDev or USBiss
    """
    def __init__(self, spi):
        self.spi = spi

    def _send_command(self, cmd, interval=10e-6):
        """Sends a single command through the SPI bus.
        :param cmd: command opcode (single byte)
        :param interval: seconds to sleep after sending a command (default: 10us)
        """
        r = self.spi.xfer([cmd])[0]
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
                raise OPCError("Received unexpected response 0x{:02X} for command: 0x{:02X}".format(r, cmd))

            if attempts > 20:
                # if this cycle has happened many times, e.g. 20, wait > 2s ( < 10s) for OPC's SPI
                # buffer to reset [Alphasense 072-0503]
                # print('opc not responding, waiting 5s for the SPI buffer to reset')
                sleep(5)

            if attempts > 25:
                # this is not described by Alphasense manuals but I've seen it happen with N3
                raise OPCError("Timeout after sending command: 0x{:02X}".format(cmd))

            # wait > 10 ms (< 100 ms)
            r = self._send_command(cmd, interval=0.02)

            attempts = attempts + 1

    def _read_bytes(self, cmd, sz):
        """Read a sequence of bytes.

        :param cmd: command opcode
        :param sz: number of bytes to read
        """
        l = []
        try:
            self._send_command_and_wait(cmd)
            for i in range(sz):
                l += [self._send_command(cmd)]

        except OPCError as e:
            print("Error while reading bytes from the device: {}".format(e))
        except USBISSError as e:
            print("USB-SPI communication error: {}".format(e))
            print("Waiting 5 seconds for the device to settle")
            sleep(5)

        return l

    def _write_bytes(self, cmd, l):
        """Write a sequence of bytes.

        :param cmd: command opcode
        :param l: list of bytes to send
        """
        try:
            self._send_command_and_wait(cmd)
            for c in l:
                self._send_command(c)
        except OPCError as e:
            print("Error while reading bytes from the device: {}".format(e))
        except USBISSError as e:
            print("USB-SPI communication error: {}".format(e))
            print("Waiting 5 seconds for the device to settle")
            sleep(5)

    def _read_struct(self, cmd, m):
        """Read a complex data structure (e.g. an histogram) from the
        device. If appliable calculate data checksum and return None if it
        fails.

        :param cmd: command opcode
        :param m: data structure definition

        :returns: dictionary filled with the struct data
        """
        raw_bytes = self._read_bytes(cmd, m.size)
        data = m.unpack(raw_bytes)

        if 'Checksum' in m.keys:
            crc = self._checksum(data, raw_bytes)
            if data['Checksum'] != crc:
                print('checksum error!')
                return None

        return data

    def _convert_temperature(self, x):
        """Convert temperature to °C"""
        return -45. + 175. * x / (float(1<<16) - 1.)

    def _convert_humidity(self, x):
        """Convert relative humidity to percentage"""
        return 100. * x / (float(1<<16) - 1.)

    def _convert_hist_to_count_per_ml(self, hist):
        """Convert counts/s to counts/ml using flow rate and sampling period.
        Changes histogram bins in-place.
        """
        ml_per_period = hist['SFR'] * hist['Sampling Period']
        if ml_per_period > 0:
            for k in self.histogram_struct.keys:
                if 'Bin ' in k:
                    hist[k] = hist[k] / ml_per_period

        return hist

    def _convert_mtof(self, hist):
        """Convert MToF from 1/3us units. Changes MToF bins in-place"""
        for k in self.histogram_struct.keys:
            if 'MToF' in k:
                hist[k] = hist[k] / 3.
        return hist

    def info(self):
        """Returns device informations string"""
        l = self._read_bytes(_OPC_CMD_READ_INFO_STRING, 60)
        return ''.join([chr(c) for c in l])

    def serial(self):
        """Returns device serial"""
        l = self._read_bytes(_OPC_CMD_READ_SERIAL_STRING, 60)
        return ''.join([chr(c) for c in l])

    def fwversion(self):
        """Return device firmware version"""
        major, minor = self._read_bytes(_OPC_CMD_READ_FW_VERSION, 2)
        return major, minor

    def ping(self):
        """Check device status. Returns True if the device is responding."""
        try:
            self._send_command_and_wait(_OPC_CMD_CHECK_STATUS)
            return True
        except:
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
        data = self._read_struct(_OPC_CMD_READ_HISTOGRAM, self.histogram_struct)
        if raw or (data is None):
            return data
        else:
            return self._histogram_post_process(data)

    def pm(self):
        """Query particle mass loadings.

        :returns: a dictionary containing PM1, PM2.5 and PM10 data.
        """
        return self._read_struct(_OPC_CMD_READ_PM, self.pm_struct)

class OPCN3(_OPC):
    """OPC-N3

    :param spi: a SPI device as returned by SpiDev or USBiss
    """
    def __init__(self, spi):
        super().__init__(spi)

        self.histogram_struct = _data_struct(_OPC_N3_HISTOGRAM_STRUCT)
        self.popt_struct = _data_struct(_OPC_N3_POPT_STRUCT)
        self.pm_struct = _data_struct(_OPC_N3_PM_STRUCT)

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
        return self._read_struct(_OPC_CMD_READ_POWER_STATE, self.popt_struct)

    # Turn peripherals on/off. POPT flag, left shifted by 1 selects
    # the proper digital pot/switch, LSB sets its state, 0 for off, 1
    # for on.
    def fan_off(self):
        """Power off fan"""
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [_OPC_N3_POPT_FAN_POT << 1 | 0])

    def fan_on(self):
        """Power on fan. Wait at least 600ms for the fan speed to settle and
        power absorption peak to pass before sending more commands.

        """
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [_OPC_N3_POPT_FAN_POT << 1 | 1])

    def laser_off(self):
        """Power off laser"""
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [_OPC_N3_POPT_LASER_SWITCH << 1 | 0])

    def laser_on(self):
        """Power on laser"""
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [_OPC_N3_POPT_LASER_SWITCH << 1 | 1])

    def on(self):
        """Power on peripherals (laser and fan). Wait at least 600ms for the
        fan speed to settle and power absorption peak to pass before
        sending more commands.

        """
        self.laser_on()
        self.fan_on()

    def off(self):
        """Power off peripherals (laser and fan)."""
        self.laser_off()
        self.fan_off()

    def reset(self):
        """Reset device. Not clear what it does, poorly documented in
        manufacturer docs.

        """
        self._send_command_and_wait(_OPC_CMD_RESET)

    def _histogram_post_process(self, hist):
        """Convert histogram raw data into proper measurements."""
        hist['Temperature'] = self._convert_temperature(hist['Temperature'])
        hist['Relative humidity'] = self._convert_temperature(hist['Relative humidity'])

        hist['Sampling Period'] = hist['Sampling Period'] / 100.
        hist['SFR'] = hist['SFR'] / 100.

        hist = self._convert_hist_to_count_per_ml(hist)
        hist = self._convert_mtof(hist)

        return hist

class OPCR1(_OPC):
    """OPC-R1

    :param spi: a SPI device as returned by SpiDev or USBiss
    """
    def __init__(self, spi):
        super().__init__(spi)

        self.histogram_struct = _data_struct(_OPC_R1_HISTOGRAM_STRUCT)
        self.pm_struct = _data_struct(_OPC_R1_PM_STRUCT)

    def on(self):
        """Power on peripherals (laser and fan). Wait at least 600ms for the
        fan speed to settle and power absorption peak to pass before
        sending more commands.

        """
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [0x03])

    def off(self):
        """Power off peripherals (laser and fan)."""

        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [0x00])

    def reset(self):
        """Reset device. Not clear what it does, poorly documented in
        manufacturer docs.

        """
        return self._send_command_and_wait(_OPC_CMD_RESET)

    def _histogram_post_process(self, hist):
        """Convert histogram raw data into proper measurements."""
        hist['Temperature'] = self._convert_temperature(hist['Temperature'])
        hist['Relative humidity'] = self._convert_temperature(hist['Relative humidity'])

        hist = self._convert_hist_to_count_per_ml(hist)
        hist = self._convert_mtof(hist)

        return hist

class OPCN2(_OPC):
    """Experimental OPC-N2 support, only tested with firmware 18

    :param spi: a SPI device as returned by SpiDev or USBiss
    """
    def __init__(self, spi):
        super().__init__(spi)

        self.histogram_struct = _data_struct(_OPC_N2_HISTOGRAM_STRUCT)
        self.popt_struct = _data_struct(_OPC_N2_POPT_STRUCT)
        self.pm_struct = _data_struct(_OPC_N2_PM_STRUCT)

    def on(self):
        """Power on peripherals (laser and fan). Wait at least 600ms for the
        fan speed to settle and power absorption peak to pass before
        sending more commands.

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
        return self._read_struct(_OPC_CMD_READ_POWER_STATE, self.popt_struct)

    def _checksum(self, data, raw_bytes):
        """Checksum calculation for OPC-N2. Least significant 16bits of
        histogram bin sum.

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
    """Try to autodetect a device from info string

    :param spi: SPI device instance as returned by SpiDev or USBiss

    :returns: an OPC(N3,N2,R1) instance, check type() to see if the
    device was properly detected
    """
    o = _OPC(spi)
    info = o.info()
    if "OPC-N3" in info:
        return OPCN3(spi)
    elif "OPC-R1" in info:
        return OPCR1(spi)
    elif "OPC-N2" in info:
        return OPCN2(spi)
    else:
        return None
