import struct
from usbiss.spi import SPI
from time import sleep
from pprint import pprint

def _unpack_float(self, dword):
    assert(len(dword) == 4)
    return struct.unpack('f', struct.pack('4B', *dword))[0]

def _unpack_ushort(self, LSB, MSB):
    return (MSB << 8) | LSB


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


class OPC(object):
    def __init__(self, spi):
        self.spi = spi

    def _send_command(self, cmd):
        r = self.spi.xfer([cmd])[0]
        # print("cmd: 0x{:02X} r: 0x{:02X}".format(cmd, r))
        sleep(0.02)
        return r

    def _wait_for_command(self, cmd):
        r = OPC_BUSY
        attempts = 0

        while (r != OPC_READY):
            if attempts >= 20:
                if attempts >= 20+5:
                    print("something wrong, aborting")
                    return None

                print("opc not responding, let's wait...")
                sleep(3)  # > 2s ( < 10s)

            r = self._send_command(cmd)

            attempts = attempts + 1

        return r

    def info(self):
        self._wait_for_command(OPC_CMD_READ_INFO_STRING)
        info = ""
        for i in range(60):
            info += chr(self._send_command(OPC_CMD_READ_INFO_STRING))

        return info

    def serial(self):
        self._wait_for_command(OPC_CMD_READ_SERIAL_STRING)
        info = ""
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

if __name__ == "__main__":
    spi = SPI("/dev/ttyACM0")
    spi.mode = 1
    spi_max_speed_hz = 500000

    opc = OPC(spi)

    print("ping?")
    print("pong!" if opc.ping() else "timeout!")
    print("info:      {}".format(opc.info()))
    print("serial:    {}".format(opc.serial()))
    print("fwversion: {}.{}".format(*opc.fwversion()))

    # wait_for_command(OPC_CMD_WRITE_POWER_STATE)
    # r = send_command(OPC_POWER_OPTION_FAN_POT << 1 | 1)

    # sleep(1)

    # print("dac and power status")

    # wait_for_command(OPC_CMD_READ_POWER_STATE)
    # keys = ["FanON", "LaserON", "FanDACVal", "LaserDACVal", "LaserSwitch", "GainToggle"]
    # r = dict()
    # for k in keys:
    #     r[k] = send_command(OPC_CMD_READ_POWER_STATE)

    # pprint(r)

    # wait_for_command(OPC_CMD_WRITE_POWER_STATE)
    # r = send_command(OPC_POWER_OPTION_FAN_POT << 1 | 0)

    # sleep(1)

    # print("dac and power status")

    # wait_for_command(OPC_CMD_READ_POWER_STATE)
    # keys = ["FanON", "LaserON", "FanDACVal", "LaserDACVal", "LaserSwitch", "GainToggle"]
    # r = dict()
    # for k in keys:
    #     r[k] = send_command(OPC_CMD_READ_POWER_STATE)

    # pprint(r)
