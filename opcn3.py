import struct
from usbiss.spi import SPI
from time import sleep
from pprint import pprint

OPC_READY = 0xF3
OPC_BUSY  = 0x31

OPC_CMD_WRITE_POWER_STATE   = 0x03
OPC_CMD_READ_POWER_STATE    = 0x13
OPC_CMD_READ_INFO_STRING    = 0x3F
OPC_CMD_READ_SERIAL_STRING  = 0x10
OPC_CMD_READ_FW_VERSION     = 0x12
OPC_CMD_READ_HISTOGRAM      = 0x30
OPC_CMD_READ_PM             = 0x32
OPC_CMD_CHECK_STATUS        = 0xCF
OPC_N3_POWER_OPTION_FAN_POT      = 1
OPC_N3_POWER_OPTION_LASER_POT    = 2
OPC_N3_POWER_OPTION_LASER_SWITCH = 3
OPC_N3_POWER_OPTION_GAIN_TOGGLE  = 4

OPC_N3_POWER_OPTION_MAP = [['FanON',              'uchar'],
                           ['LaserON',            'uchar'],
                           ['FanDACVal',          'uchar'],
                           ['LaserDACVal',        'uchar'],
                           ['LaserSwitch',        'uchar'],
                           ['GainToggle',         'uchar']]

OPC_N3_PM_MAP =           [['PM1',                'float'],
                           ['PM2.5',              'float'],
                           ['PM10',               'float'],
                           ['Checksum',          'ushort']]

OPC_N3_HISTOGRAM_MAP    = [['Bin 0',             'ushort'],
                           ['Bin 1',             'ushort'],
                           ['Bin 2',             'ushort'],
                           ['Bin 3',             'ushort'],
                           ['Bin 4',             'ushort'],
                           ['Bin 5',             'ushort'],
                           ['Bin 6',             'ushort'],
                           ['Bin 7',             'ushort'],
                           ['Bin 8',             'ushort'],
                           ['Bin 9',             'ushort'],
                           ['Bin 10',            'ushort'],
                           ['Bin 11',            'ushort'],
                           ['Bin 12',            'ushort'],
                           ['Bin 13',            'ushort'],
                           ['Bin 14',            'ushort'],
                           ['Bin 15',            'ushort'],
                           ['Bin 16',            'ushort'],
                           ['Bin 17',            'ushort'],
                           ['Bin 18',            'ushort'],
                           ['Bin 19',            'ushort'],
                           ['Bin 20',            'ushort'],
                           ['Bin 21',            'ushort'],
                           ['Bin 22',            'ushort'],
                           ['Bin 23',            'ushort'],
                           ['Bin1 MToF',          'uchar'],
                           ['Bin3 MToF',          'uchar'],
                           ['Bin5 MToF',          'uchar'],
                           ['Bin7 MToF',          'uchar'],
                           ['Sampling Period',   'ushort'],
                           ['SFR',               'ushort'],
                           ['Temperature',       'ushort'],
                           ['Relative humidity', 'ushort'],
                           ['PM1',                'float'],
                           ['PM2.5',              'float'],
                           ['PM10',               'float'],
                           ['#RejectGlitch',     'ushort'],
                           ['#RejectLongTOF',    'ushort'],
                           ['#RejectRatio',      'ushort'],
                           ['#RejectOutOfRange', 'ushort'],
                           ['Fan rev count',     'ushort'],
                           ['Laser status',      'ushort'],
                           ['Checksum',          'ushort']]



def _unpack(t, x):
    if t == 'uchar':
        return x[0]
    elif t == 'ushort':
        return (x[1] << 8) | x[0]
    elif t == 'float':
        return struct.unpack('f', struct.pack('4B', *x))[0]
    else:
        raise ValueError

def _len(t):
    if t == 'uchar':
        return 1
    elif t == 'ushort':
        return 2
    elif t == 'float':
        return 4
    else:
        raise ValueError


class _data_map(object):
    def __init__(self, m):
        self.data_map = m
        self.size = self._map_size(self.data_map)
        self.keys = self._keys()

    def _map_size(self, m):
        l = 0
        for k, t in m:
            l += _len(t)
        return l

    def _keys(self):
        return [k for k, t in self.data_map]

    def unpack(self, raw_bytes):
        data = dict()
        c = 0
        for k, t in self.data_map:
            l = _len(t)
            data[k] = _unpack(t, raw_bytes[c:c+l])
            c += l

        return data


class OPC(object):
    def __init__(self, spi):
        self.spi = spi
        self.histogram_map = _data_map(OPC_N3_HISTOGRAM_MAP)
        self.popt_map = _data_map(OPC_N3_POWER_OPTION_MAP)
        self.pm_map = _data_map(OPC_N3_PM_MAP)

    def _send_command(self, cmd):
        r = self.spi.xfer([cmd])[0]
        # print('cmd: 0x{:02X} r: 0x{:02X}'.format(cmd, r))
        sleep(0.02)
        return r

    def _wait_for_command(self, cmd):
        r = OPC_BUSY
        attempts = 0

        while (r != OPC_READY):
            if attempts >= 20:
                if attempts >= 20+5:
                    print('something wrong, aborting')
                    return None

                print('opc not responding, let\'s wait...')
                sleep(3)  # > 2s ( < 10s)

            r = self._send_command(cmd)

            attempts = attempts + 1

        return r

    def info(self):
        self._wait_for_command(OPC_CMD_READ_INFO_STRING)
        info = ''
        for i in range(60):
            info += chr(self._send_command(OPC_CMD_READ_INFO_STRING))

        return info

    def serial(self):
        self._wait_for_command(OPC_CMD_READ_SERIAL_STRING)
        info = ''
        for i in range(60):
            info += chr(self._send_command(OPC_CMD_READ_SERIAL_STRING))

        return info

    def fwversion(self):
        self._wait_for_command(OPC_CMD_READ_FW_VERSION)
        major = self._send_command(OPC_CMD_READ_FW_VERSION)
        minor = self._send_command(OPC_CMD_READ_FW_VERSION)

        return major, minor

    def ping(self):
        r = self._wait_for_command(OPC_CMD_CHECK_STATUS)
        if r == OPC_READY:
            return True
        else:
            return False

    def fan_off(self):
        self._wait_for_command(OPC_CMD_WRITE_POWER_STATE)
        self._send_command(OPC_N3_POWER_OPTION_FAN_POT << 1 | 0)

    def fan_on(self):
        self._wait_for_command(OPC_CMD_WRITE_POWER_STATE)
        self._send_command(OPC_N3_POWER_OPTION_FAN_POT << 1 | 1)
        sleep(1)

    def laser_off(self):
        self._wait_for_command(OPC_CMD_WRITE_POWER_STATE)
        self._send_command(OPC_N3_POWER_OPTION_LASER_SWITCH << 1 | 0)

    def laser_on(self):
        self._wait_for_command(OPC_CMD_WRITE_POWER_STATE)
        self._send_command(OPC_N3_POWER_OPTION_LASER_SWITCH << 1 | 1)

    def on(self):
        self.laser_on()
        self.fan_on()

    def off(self):
        self.laser_off()
        self.fan_off()

    def checksum(self, data):
        poly = 0xA001
        init_crc_val = 0xFFFF

        crc = init_crc_val

        for i in range(len(data)):
            crc ^= data[i]
            for bit in range(8):
                if (crc & 1): # if bit 0 of crc is 1
                    crc >>= 1
                    crc ^= poly
                else:
                    crc >>= 1

        return crc

    def _read_map(self, cmd, m):
        self._wait_for_command(cmd)
        raw_bytes = []
        for i in range(m.size):
            raw_bytes += [self._send_command(cmd)]

        data = m.unpack(raw_bytes)

        if 'Checksum' in m.keys:
            crc = self.checksum(raw_bytes[:-2])
            if data['Checksum'] != crc:
                print('checksum error!')
                return None

        return data

    def histogram(self):
        data = self._read_map(OPC_CMD_READ_HISTOGRAM, self.histogram_map)
        return self.histogram_post_process(data)

    def histogram_post_process(self, hist):
        hist['Temperature'] = -45. + 175. * hist['Temperature'] / (float(1<<16) - 1.)
        hist['Relative humidity'] = 100. * hist['Relative humidity'] / (float(1<<16) - 1.)
        hist['Sampling Period'] = hist['Sampling Period'] / 100.
        hist['SFR'] = hist['SFR'] / 100.

        ml_per_bin = hist['SFR'] * hist['Sampling Period']
        for k, t in OPC_N3_HISTOGRAM_MAP:
            if 'Bin ' in k:
                hist[k] = hist[k] / ml_per_bin

        for k, t in OPC_N3_HISTOGRAM_MAP:
            if 'MToF' in k:
                hist[k] = hist[k] / 3.

        for k, t in OPC_N3_HISTOGRAM_MAP:
            print('{}: {}'.format(k, hist[k]))

    def pm(self):
        return self._read_map(OPC_CMD_READ_PM, self.pm_map)

    def power_status(self):
        return self._read_map(OPC_CMD_READ_POWER_STATE, self.popt_map)

if __name__ == '__main__':
    spi = SPI('/dev/ttyACM0')
    spi.mode = 1
    spi_max_speed_hz = 500000

    opc = OPC(spi)

    print('ping?')
    print('pong!' if opc.ping() else 'timeout!')
    print('info:      {}'.format(opc.info()))
    print('serial:    {}'.format(opc.serial()))
    print('fwversion: {}.{}'.format(*opc.fwversion()))
    print('on')
    opc.on()
    pprint(opc.power_status())
    sleep(3)
    for i in range(5):
        opc.histogram()
 #        sleep(1)
#        pprint(opc.pm())
        sleep(1)
    print('off')
    opc.off()
    pprint(opc.power_status())

    # wait_for_command(OPC_CMD_WRITE_POWER_STATE)
    # r = send_command(OPC_N3_POWER_OPTION_FAN_POT << 1 | 1)

    # sleep(1)

    # print('dac and power status')

    # wait_for_command(OPC_CMD_READ_POWER_STATE)
    # keys = ['FanON', 'LaserON', 'FanDACVal', 'LaserDACVal', 'LaserSwitch', 'GainToggle']
    # r = dict()
    # for k in keys:
    #     r[k] = send_command(OPC_CMD_READ_POWER_STATE)

    # pprint(r)

    # wait_for_command(OPC_CMD_WRITE_POWER_STATE)
    # r = send_command(OPC_N3_POWER_OPTION_FAN_POT << 1 | 0)

    # sleep(1)

    # print('dac and power status')

    # wait_for_command(OPC_CMD_READ_POWER_STATE)
    # keys = ['FanON', 'LaserON', 'FanDACVal', 'LaserDACVal', 'LaserSwitch', 'GainToggle']
    # r = dict()
    # for k in keys:
    #     r[k] = send_command(OPC_CMD_READ_POWER_STATE)

    # pprint(r)
