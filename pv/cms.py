# Copyright (c) 2010-2011 Edmund Tse
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from __future__ import print_function
import struct
import pv


def bin2hex(data):
    """
    Converts binary data to hex
    """
    return data.encode('hex_codec')


def checksum(data):
    """
    (bytes) -> (2 bytes)
    Computes the checksum for the given data.
    """
    return struct.pack('!H', sum(map(ord, data)))


def parse_frame(data):
    """
    Converts a frame in binary format into a Frame object
    """
    if len(data) < 11:  # 2B sync 2B src 2B dst 2B cmd 1B len 0B data 2B checksum
        raise ValueError("Frame too short (%d B)" % len(data))

    if not checksum(data[0:-2]) == data[-2:]:
        raise ValueError("Bad checksum")

    (preamble, src, dst, cmd, size) = struct.unpack('!HHHHB', data[0:9])
    if preamble != Frame.SYNC:
        raise ValueError("Bad preamble")

    payload = data[9:-2]
    if len(payload) != size:
        raise ValueError("Bad payload size: expected %d, actual %d" % (size, len(payload)))

    return Frame(cmd, payload, dst, src)


def interpret_data(data, layout, dictionary):
    try:
        numbers = struct.unpack('!' + 'H'*len(layout), data)
    except struct.error as e:
        print("Error unpacking data:", e)
        return None

    values = dict(zip(layout, numbers))
    return [(name, reduce(lambda x, y:(x << 16) + y, map(values.get, code)) / divisor)
            for name, (code, divisor) in dictionary.items()
            if reduce(lambda x, y: x and y, map(values.has_key, code))]


class Frame(object):
    """
    <sync> <src> <dst> <cmd> <len> <payload> <checksum>
      2B    2B    2B    2B    1B     len B       2B
    """
    MAX_SIZE =      256			# Arbitrary max frame size
    SYNC =          0xaaaa		# 2 sync bytes preamble "1010101010101010"
    ADDR_DEFAULT =	0x0000		# Broadcast address
    ADDR_HOST =		0x0100		# Default host address
    ADDR_DEV =		0x0001		# Default device address
    # Commands
    CMD_DSC =   0x0000		# Computer discovers devices
    CMD_DSC_R =	0x0080		# Inverter advertises its serial number
    CMD_REG =	0x0001		# Address registration
    CMD_REG_R =	0x0081		# Acknowledge the assigned address
    CMD_RMV =	0x0002		# Disconnect
    CMD_RMV_R =	0x0082		# Disconnect ACK
    CMD_RCT =	0x0003		# Reconnect all devices
    CMD_RST =	0x0004		# Reset communications
    CMD_STL =	0x0100		# Status frame structure request
    CMD_STL_R =	0x0180		# Status frame structure reply
    CMD_PRL =	0x0101		# Parameter frame structure request
    CMD_PRL_R =	0x0181		# Parameter frame structure reply
    CMD_STA =	0x0102		# Status request
    CMD_STA_R =	0x0182		# Status reply
    CMD_VER =	0x0103		# Version string request
    CMD_VER_R =	0x0183		# Version string reply
    CMD_PRM =	0x0104		# Parameter request
    CMD_PRM_R =	0x0184		# Parameters reply
    CMD_SP0 =	0x0200		# Set Vpv-Start
    CMD_SP0_R =	0x0280		# Set Vpv-Start ACK
    CMD_SP1 =	0x0201		# Set T-Start
    CMD_SP1_R =	0x0281		# Set T-Start ACK
    CMD_SP2 =	0x0204		# Set Vac-Min
    CMD_SP2_R =	0x0284		# Set Vac-Min ACK
    CMD_SP3 =	0x0205		# Set Vac-Max
    CMD_SP3_R =	0x0285		# Set Vac-Max ACK
    CMD_SP4 =	0x0206		# Set Fac-Max
    CMD_SP4_R =	0x0286		# Set Fac-Max ACK
    CMD_SP5 =	0x0207		# Set Fac-Min
    CMD_SP5_R =	0x0287		# Set Fac-Min ACK
    CMD_SP6 =	0x0208		# Set DZac-Max
    CMD_SP6_R =	0x0288		# Set DZac-Max ACK
    CMD_SP7 =	0x0209		# Set DZac
    CMD_SP7_R =	0x0289		# Set DZac ACK
    CMD_ZRO =	0x0300		# Reset inverter E-Total and h-Total
    CMD_ZRO_R =	0x0380		# Reset inverter E-Total and h-Total ACK

    def __init__(self, cmd, payload='', dst=ADDR_DEFAULT, src=ADDR_DEFAULT):
        assert(type(src) == int)
        assert(type(cmd) == int)
        assert(type(payload) == str)
        assert(type(dst) == int)
        assert(type(src) == int)
        (self.src, self.dst, self.cmd, self.payload) = (src, dst, cmd, payload)

    def __repr__(self):
        return bin2hex(self.bytes())

    def colorize(self):
        """
        Returns ANSI coloured hex representation of the frame
        """
        string = str(self)
        if len(string) < 22:
            return string
        return '\033[90m' + string[0:4] + '\033[93m' + string[4:8] + \
            '\033[94m' + string[8:12] + '\033[97m' + string[12:16] + \
            '\033[91m' + string[16:18] + '\033[00m' + string[18:-4] + \
            '\033[92m' + string[-4:] + '\033[00m'

    def bytes(self):
        """
        Returns the bytes of this frame including preamble and checksum.
        """
        data = struct.pack('!HHHHB', Frame.SYNC, self.src, self.dst, self.cmd, len(self.payload)) + self.payload
        return data + checksum(data)


class Device:
    """
    Device is a base class that provides physical and link layer operations
    """
    STATUS = {
        # Field		Code			Divisor
        'Temp-inv':	('\x00',		10.0),		# Inverter internal temperature (deg C)
        'Vpv1':		('\x01',		10.0),		# PV1 Voltage (V)
        'Vpv2':		('\x02',		10.0),		# PV2 Voltage (V)
        'Vpv3':		('\x03',		10.0),		# PV3 Voltage (V)
        'Ipv1':		('\x04',		10.0),		# PV1 Current (A)
        'Ipv2':		('\x05',		10.0),		# PV2 Current (A)
        'Ipv3':		('\x06',		10.0),		# PV3 Current (A)
        'Vpv':		('\x40',		10.0),		# PV Voltage (V)
        'Iac':		('\x41',		10.0),		# Current to grid (A)
        'Vac':		('\x42',		10.0),		# Grid voltage (V)
        'Fac':		('\x43',		100.0),		# Grid frequency (Hz)
        'Pac':		('\x44',		1),			# Power to grid (W)
        'Zac':		('\x45',		1),			# Grid impedance (mOhm)
        'E-Total':	('\x47\x48',	10.0),		# Total energy to grid (kWh)
        'h-Total':	('\x49\x4a',	1),			# Total Operation hours (Hr)
        'Mode':		('\x4c',		1),			# Operation mode
        'Error':	('\x7e\x7f',	1)			# Error
    }

    PARAM = {
        'Vpc-start':	('\x40',    10.0),  # PV Start-up voltage (V)
        'T-start':		('\x41',	1),	    # Time to connect grid (Sec)
        'Vac-Min':		('\x44',	10.0),  # Minimum operational grid voltage
        'Vac-Max':		('\x45',	10.0),  # Maximum operational grid voltage
        'Fac-Min':		('\x46',	100.0), # Minimum operational frequency
        'Fac-Max':		('\x47',	100.0), # Maximum operational frequency
        'Zac-Max':		('\x48',	1),	    # Maximum operational grid impedance
        'DZac':			('\x49',	1),     # Allowable Delta Zac of operation
    }

    MODE = {0: 'Wait', 1: 'Normal', 2: 'Fault', 3: 'Permenant Fault'}

    ERROR = {		# The 2 error bytes are bit fields, e.g. ERROR[16] = 0x0100
        0: ('The GFCI detection circucit is abnormal', 'GFCI ckt fails'),
        1: ('The DC output sensor is abnormal', 'DC sensor fails'),
        2: ('The 2.5V reference inside is abnormal', 'Ref 2.5V fails'),
        3: ('Different measurements between Master and Slave for output DC current', 'DC inj. differs for M-S'),
        4: ('Different measurements between Master and Slave for GFCI', 'Ground I differs for M-S'),
        5: ('DC Bus voltage is too low', 'Bus-Low-Fail'),
        6: ('DC Bus voltage is too High', 'Bus-High-Fail'),
        7: ('Device Fault', 'Device-Fault'),
        8: ('Delta GridZ is too high', 'Delta Z high'),
        9: ('No grid voltage detected', 'No-Utility'),
        10: ('Ground current is too high', 'Ground I high'),
        11: ('DC bus is not correct', 'DC BUS fails'),
        12: ('Master and Slave firmware version is unmatch', 'M-S Version Fail'),
        13: ('Internal temperature is high', 'Temperature high'),
        14: ('AutoTest failed', 'Test Fail'),
        15: ('PV voltage is too high', 'Vpv high'),
        16: ('Fan Lock', 'FanLock-Warning'),
        17: ('The measured AC voltage is out of tolerable range', 'Vac out of range'),
        18: ('Isulation resistance of PV to earth is too low', 'PV insulation low'),
        19: ('The DC injection to grid is too high', 'DC injection high'),
        20: ('Different measurements between Master and Slave for dl, Fac, Uac or Zac', 'Fac,Zac,Vac differs for M-S'),
        21: ('Different measurements between Master and Slave for grid impedance', 'Zac differs for M-S'),
        22: ('Different measurements between Master and Slave for grid frequency', 'Fac differs for M-S'),
        23: ('Different measurements between Master and Slave for grid voltage', 'Vac differs for M-S'),
        24: ('Memory space is full', 'MemFull-Warning'),
        25: ('Test of output AC relay fails', 'AC relay fails'),
        26: ('The slave impedance is out of tolerable range', 'Zac-Slave out of range'),
        27: ('The measured AC impedance is out of range', 'Zac-Master out of range'),
        28: ('The slave frequency is out of tolerable range', 'Fac-Slave out of range'),
        29: ('The master frequency is out of tolerable range', 'Fac-Master out of range'),
        30: ('EEPROM reading or writing error', 'EEPROM fails'),
        31: ('Communication between microcontrollers fails', 'Comm fails between M-S'),
    }

    def __init__(self, port, addr):
        self.addr = addr
        self.port = port

    def send(self, frm, use_frame_src=False):
        """
        Writes a frame to the port
        """
        if not use_frame_src:
            frm.src = self.addr
        if pv._DEBUG:
            if pv._ANSI_COLOR:
                print("\033[96mSEND\033[00m ->", frm.colorize())
            else:
                print("SEND ->", frm)

        self.port.write(frm.bytes())

    def receive(self):
        """
        Returns a valid incoming frame, or None if no valid frames received
        within the timeout period
        """
        sync = struct.pack('!H', Frame.SYNC)
        frm = None

        while frm is None:
            byte = self.port.read()
            if len(byte) != 1:
                break
            if byte != sync[0]:
                continue

            byte = self.port.read()
            if len(byte) != 1:
                break
            if byte != sync[1]:
                continue

            src_dst_cmd = self.port.read(6)
            if len(src_dst_cmd) != 6:
                break

            length = self.port.read()
            if len(length) != 1:
                break

            payload_checksum = self.port.read(ord(length) + 2)
            if len(payload_checksum) != ord(length) + 2:
                break

            buf = sync + src_dst_cmd + length + payload_checksum
            if pv._DEBUG:
                if pv._ANSI_COLOR:
                    print("\033[95mRECV\033[00m <-", bin2hex(buf),)
                else:
                    print("RECV <-", bin2hex(buf),)

            try:
                frm = parse_frame(buf)
                if pv._DEBUG:
                    print("OK")
            except ValueError as e:
                if pv._DEBUG:
                    print(e)
        return frm


class Inverter(Device):
    """
    Contains methods to interact with a PV inverter
    """
    def __init__(self, port, my_addr=Frame.ADDR_HOST):
        Device.__init__(self, port, my_addr)

    def reset(self):
        """
        Resets the communication protocol
        """
        self.send(Frame(Frame.CMD_RST))

    def discover(self):
        """
        Looks for an available inverter
        Returns the inverter serial number as string, or None if offline
        """
        self.send(Frame(Frame.CMD_DSC))
        frm = self.receive()
        return frm.payload if frm is not None and frm.cmd == Frame.CMD_DSC_R else None

    def register(self, sn, addr=Frame.ADDR_DEV):
        """
        Registers an inverter for direct communication
        Returns True if the inverter acknowledges registration
        """
        self.send(Frame(Frame.CMD_REG, sn + struct.pack('!H', addr)))
        frm = self.receive()
        return True if frm is not None and frm.cmd == Frame.CMD_REG_R else False

    def version(self, dst=Frame.ADDR_DEV):
        """
        Queries an inverter for an extended identification string
        Returns the device identification string, or None
        """
        self.send(Frame(Frame.CMD_VER, dst=dst))
        frm = self.receive()
        return frm.payload if frm is not None and frm.cmd == Frame.CMD_VER_R else None

    def status_layout(self, dst=Frame.ADDR_DEV):
        """
        Queries an inverter for the layout of its status frame
        Returns a string of bytes representing the status layout, or None
        """
        self.send(Frame(Frame.CMD_STL, dst=dst))
        frm = self.receive()
        return frm.payload if frm is not None and frm.cmd == Frame.CMD_STL_R else None

    def param_layout(self, dst=Frame.ADDR_DEV):
        """
        Queries an inverter for the layout of its parameters frame
        Returns a string of bytes representing the parameters layout, or None
        """
        self.send(Frame(Frame.CMD_PRL, dst=dst))
        frm = self.receive()
        return frm.payload if frm is not None and frm.cmd == Frame.CMD_PRL_R else None

    def parameters(self, layout, dst=Frame.ADDR_DEV):
        """
        Queries an inverter for its parameters
        Returns a list of device parameters, or None
        """
        self.send(Frame(Frame.CMD_PRM, dst=dst))
        frm = self.receive()
        return interpret_data(frm.payload, layout, Device.PARAM) if \
            frm is not None and frm.cmd == Frame.CMD_PRM_R else None

    def status(self, layout, dst=Frame.ADDR_DEV):
        """
        Queries an inverter for its status, given the layout of response frame
        Returns a list of device status, or None
        """
        self.send(Frame(Frame.CMD_STA, dst=dst))
        frm = self.receive()
        return interpret_data(frm.payload, layout, Device.STATUS) if \
            frm is not None and frm.cmd == Frame.CMD_STA_R else None
