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
OPC_N3_POPT_FAN_POT      = 1
OPC_N3_POPT_LASER_POT    = 2
OPC_N3_POPT_LASER_SWITCH = 3
OPC_N3_POPT_GAIN_TOGGLE  = 4

OPC_N3_POPT_MAP =      [['FanON',               'uint8'],
                        ['LaserON',             'uint8'],
                        ['FanDACVal',           'uint8'],
                        ['LaserDACVal',         'uint8'],
                        ['LaserSwitch',         'uint8'],
                        ['GainToggle',          'uint8']]

#[*[['Bin {}'.format(b), t] for b, t in zip(range(24), ["uint16"]*24)],
OPC_N3_HISTOGRAM_MAP = [['Bin 0',              'uint16'],
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

OPC_N3_PM_MAP =        [['PM1',               'float32'],
                        ['PM2.5',             'float32'],
                        ['PM10',              'float32'],
                        ['Checksum',           'uint16']]

OPC_R1_PM_MAP = OPC_N3_PM_MAP

OPC_R1_HISTOGRAM_MAP = [['Bin 0',              'uint16'],
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
                        ['#RejectLongTOF',       'uint8'],
                        ['PM1',               'float32'],
                        ['PM2.5',             'float32'],
                        ['PM10',              'float32'],
                        ['Checksum',           'uint16']]


def _unpack(t, x):
    if t == 'uint8':
        return x[0]
    elif t == 'uint16':
        return (x[1] << 8) | x[0]
    elif t == 'float32':
        return struct.unpack('f', struct.pack('4B', *x))[0]
    else:
        raise ValueError

def _len(t):
    if t == 'uint8':
        return 1
    elif t == 'uint16':
        return 2
    elif t == 'float32':
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

    def _convert_temperature(self, x):
        return -45. + 175. * x / (float(1<<16) - 1.)

    def _convert_humidity(self, x):
        return 100. * x / (float(1<<16) - 1.)

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

    def checksum(self, data):
        poly = 0xA001
        init_crc_val = 0xFFFF

        crc = init_crc_val

        for i in range(len(data)):
            crc ^= data[i]
            for bit in range(8):
                if (crc & 1):
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

    def pm(self):
        return self._read_map(OPC_CMD_READ_PM, self.pm_map)

    def power_state(self):
        raise NotImplementedError


class OPCN3(OPC):
    def __init__(self, spi):
        super().__init__(spi)

        self.histogram_map = _data_map(OPC_N3_HISTOGRAM_MAP)
        self.popt_map = _data_map(OPC_N3_POPT_MAP)
        self.pm_map = _data_map(OPC_N3_PM_MAP)

    def power_state(self):
        return self._read_map(OPC_CMD_READ_POWER_STATE, self.popt_map)

    def fan_off(self):
        self._wait_for_command(OPC_CMD_WRITE_POWER_STATE)
        self._send_command(OPC_N3_POPT_FAN_POT << 1 | 0)

    def fan_on(self):
        self._wait_for_command(OPC_CMD_WRITE_POWER_STATE)
        self._send_command(OPC_N3_POPT_FAN_POT << 1 | 1)
        sleep(1)

    def laser_off(self):
        self._wait_for_command(OPC_CMD_WRITE_POWER_STATE)
        self._send_command(OPC_N3_POPT_LASER_SWITCH << 1 | 0)

    def laser_on(self):
        self._wait_for_command(OPC_CMD_WRITE_POWER_STATE)
        self._send_command(OPC_N3_POPT_LASER_SWITCH << 1 | 1)

    def on(self):
        self.laser_on()
        self.fan_on()

    def off(self):
        self.laser_off()
        self.fan_off()

    def histogram_post_process(self, hist):
        hist['Temperature'] = self._convert_temperature(hist['Temperature'])
        hist['Relative humidity'] = self._convert_temperature(hist['Relative humidity'])
        hist['Sampling Period'] = hist['Sampling Period'] / 100.
        hist['SFR'] = hist['SFR'] / 100.

        ml_per_bin = hist['SFR'] * hist['Sampling Period']
        for k in self.histogram_map.keys:
            if 'Bin ' in k:
                hist[k] = hist[k] / ml_per_bin

        for k in self.histogram_map.keys:
            if 'MToF' in k:
                hist[k] = hist[k] / 3.

        for k in self.histogram_map.keys:
            print('{}: {}'.format(k, hist[k]))




class OPCR1(OPC):
    def __init__(self, spi):
        super().__init__(spi)

        self.histogram_map = _data_map(OPC_R1_HISTOGRAM_MAP)
        self.pm_map = _data_map(OPC_R1_PM_MAP)

    def on(self):
        self._wait_for_command(OPC_CMD_WRITE_POWER_STATE)
        self._send_command(0x03)

    def off(self):
        self._wait_for_command(OPC_CMD_WRITE_POWER_STATE)
        self._send_command(0x00)

    def histogram_post_process(self, hist):
        hist['Temperature'] = self._convert_temperature(hist['Temperature'])
        hist['Relative humidity'] = self._convert_temperature(hist['Relative humidity'])

        return hist



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
    pprint(opc.power_state())
    sleep(3)
    for i in range(5):
        opc.histogram()
        sleep(1)
        pprint(opc.pm())
        sleep(1)
    print('off')
    opc.off()
    pprint(opc.power_state())