import struct
from time import sleep

_OPC_READY = 0xF3
_OPC_BUSY  = 0x31

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
_OPC_N3_POPT_FAN_POT      = 1
_OPC_N3_POPT_LASER_POT    = 2
_OPC_N3_POPT_LASER_SWITCH = 3
_OPC_N3_POPT_GAIN_TOGGLE  = 4

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

_OPC_N2_PM_STRUCT =        [['PM1',               'float32'],
                           ['PM2.5',             'float32'],
                           ['PM10',              'float32']]

_OPC_N3_PM_STRUCT =        [['PM1',               'float32'],
                           ['PM2.5',             'float32'],
                           ['PM10',              'float32'],
                           ['Checksum',           'uint16']]

_OPC_R1_PM_STRUCT = _OPC_N3_PM_STRUCT

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


def _unpack(t, x):
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

class OPC(object):
    def __init__(self, spi):
        self.spi = spi

    def _send_command(self, cmd):
        r = self.spi.xfer([cmd])[0]
        # print('cmd: 0x{:02X} r: 0x{:02X}'.format(cmd, r))
        sleep(10e-6)
        return r

    def _send_command_and_wait(self, cmd):
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

            r = self._send_command(cmd)
            sleep(0.02)   # wait > 10 ms (< 100 ms)

            attempts = attempts + 1

    def _read_bytes(self, cmd, sz):
        l = []
        try:
            self._send_command_and_wait(cmd)
            for i in range(sz):
                l += [self._send_command(cmd)]

        except OPCError as e:
            print("Error while reading bytes from the device: {}".format(e))

        return l

    def _write_bytes(self, cmd, l):
        try:
            self._send_command_and_wait(cmd)
            for c in l:
                self._send_command(c)
        except OPCError as e:
            print("Error while reading bytes from the device: {}".format(e))

    def _read_struct(self, cmd, m):
        raw_bytes = self._read_bytes(cmd, m.size)
        data = m.unpack(raw_bytes)

        if 'Checksum' in m.keys:
            crc = self.checksum(data, raw_bytes)
            if data['Checksum'] != crc:
                print('checksum error!')
                return None

        return data

    def _convert_temperature(self, x):
        return -45. + 175. * x / (float(1<<16) - 1.)

    def _convert_humidity(self, x):
        return 100. * x / (float(1<<16) - 1.)

    def _convert_hist_to_count_per_ml(self, hist):
        ml_per_period = hist['SFR'] * hist['Sampling Period']
        if ml_per_period > 0:
            for k in self.histogram_struct.keys:
                if 'Bin ' in k:
                    hist[k] = hist[k] / ml_per_period

        return hist

    def _convert_mtof(self, hist):
        for k in self.histogram_struct.keys:
            if 'MToF' in k:
                hist[k] = hist[k] / 3.
        return hist

    def info(self):
        l = self._read_bytes(_OPC_CMD_READ_INFO_STRING, 60)
        return ''.join([chr(c) for c in l])

    def serial(self):
        l = self._read_bytes(_OPC_CMD_READ_SERIAL_STRING, 60)
        return ''.join([chr(c) for c in l])

    def fwversion(self):
        major, minor = self._read_bytes(_OPC_CMD_READ_FW_VERSION, 2)
        return major, minor

    def ping(self):
        try:
            self._send_command_and_wait(_OPC_CMD_CHECK_STATUS)
            return True
        except:
            return False

    def checksum(self, data, raw_bytes):
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
        data = self._read_struct(_OPC_CMD_READ_HISTOGRAM, self.histogram_struct)
        if raw or (data is None):
            return data
        else:
            return self.histogram_post_process(data)

    def pm(self):
        return self._read_struct(_OPC_CMD_READ_PM, self.pm_struct)

class OPCN3(OPC):
    def __init__(self, spi):
        super().__init__(spi)

        self.histogram_struct = _data_struct(_OPC_N3_HISTOGRAM_STRUCT)
        self.popt_struct = _data_struct(_OPC_N3_POPT_STRUCT)
        self.pm_struct = _data_struct(_OPC_N3_PM_STRUCT)

    def power_state(self):
        return self._read_struct(_OPC_CMD_READ_POWER_STATE, self.popt_struct)

    def fan_off(self):
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [_OPC_N3_POPT_FAN_POT << 1 | 0])

    def fan_on(self):
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [_OPC_N3_POPT_FAN_POT << 1 | 1])

    def laser_off(self):
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [_OPC_N3_POPT_LASER_SWITCH << 1 | 0])

    def laser_on(self):
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [_OPC_N3_POPT_LASER_SWITCH << 1 | 1])

    def on(self):
        self.laser_on()
        self.fan_on()

    def off(self):
        self.laser_off()
        self.fan_off()

    def reset(self):
        self._send_command_and_wait(_OPC_CMD_RESET)

    def histogram_post_process(self, hist):
        hist['Temperature'] = self._convert_temperature(hist['Temperature'])
        hist['Relative humidity'] = self._convert_temperature(hist['Relative humidity'])

        hist['Sampling Period'] = hist['Sampling Period'] / 100.
        hist['SFR'] = hist['SFR'] / 100.

        hist = self._convert_hist_to_count_per_ml(hist)
        hist = self._convert_mtof(hist)

        return hist

class OPCR1(OPC):
    def __init__(self, spi):
        super().__init__(spi)

        self.histogram_struct = _data_struct(_OPC_R1_HISTOGRAM_STRUCT)
        self.pm_struct = _data_struct(_OPC_R1_PM_STRUCT)

    def on(self):
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [0x03])

    def off(self):
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [0x00])

    def reset(self):
        return self._send_command_and_wait(_OPC_CMD_RESET)

    def histogram_post_process(self, hist):
        hist['Temperature'] = self._convert_temperature(hist['Temperature'])
        hist['Relative humidity'] = self._convert_temperature(hist['Relative humidity'])

        hist = self._convert_hist_to_count_per_ml(hist)
        hist = self._convert_mtof(hist)

        return hist

class OPCN2(OPC):
    def __init__(self, spi):
        super().__init__(spi)

        self.histogram_struct = _data_struct(_OPC_N2_HISTOGRAM_STRUCT)
        self.popt_struct = _data_struct(_OPC_N2_POPT_STRUCT)
        self.pm_struct = _data_struct(_OPC_N2_PM_STRUCT)

    def on(self):
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [0x00])

    def off(self):
        self._write_bytes(_OPC_CMD_WRITE_POWER_STATE, [0x01])

    def power_state(self):
        return self._read_struct(_OPC_CMD_READ_POWER_STATE, self.popt_struct)

    def checksum(self, data, raw_bytes):
        bins = [data[k] for k in data.keys() if 'Bin ' in k]
        binsum = 0
        for b in bins:
            binsum += b

        return binsum & 0xFFFF

    def histogram_post_process(self, hist):
        # hist['Temperature'] = self._convert_temperature(hist['Temperature'])

        hist = self._convert_hist_to_count_per_ml(hist)
        hist = self._convert_mtof(hist)

        return hist
