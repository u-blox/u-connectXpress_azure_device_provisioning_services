from asyncio.windows_events import NULL
from ctypes import sizeof
import sys
import json
import serial
import time
import struct
import string
import msvcrt

EDM_START = b'\xAA'
EDM_STOP = b'\x55'

# Packet type strings
CONNECT_EVENT = '\x00\x11'
DISCONNECT_EVENT = '\x00\x21'
DATA_EVENT = '\x00\x31'
DATA_COMMAND = '\x00\x36'
AT_EVENT = '\x00\x41'
AT_REQUEST = '\x00\x44'
AT_CONFIRMATION = '\x00\x45'
RESEND_CONNECT_EVENT_COMMAND = '\x00\x56'
IPHONE_EVENT = '\x00\x61'
START_EVENT = '\x00\x71'

# BLUETOOTH = '\x01'
BLUETOOTH = 1
IPv4 = 2
IPv6 = 3

SPP = 0
DUN = 1
SPS = 14

# Packet types
connect_event = 0x11
disconnect_event = 0x21
data_event = 0x31
data_command = 0x36
at_event = 0x41
at_request = 0x44
at_confirmation = 0x45
resend_connect_event_command = 0x56
iphone_event = 0x61
start_event = 0x71
no_event = 0x00

# Global variable
g_packet_type = no_event
g_channel_id = 0xFF
g_at_response_string = ''

# Device configuration, change the following values accordingly:
SSID = "SSID"
PASSWORD = "PASSWORD"
iothubhostname = "global.azure-devices-provisioning.net"
registration_Id = "registration_Id"
idScope = "0ne0067E45C"
path_to_CA = "C:\\azure\\ca.pem"
path_to_Cert = "C:\\azure\\cert.pem"
path_to_key = "C:\\azure\\key.pem"

start_time = int(round(time.time() * 1000))


def millis():
    end_time = int(round(time.time() * 1000))
    return end_time - start_time


def send_at_command(com, cmd, is_pem: bool = False):
    # Send at command
    print(" %dms -> %s" % (millis(), cmd))
    com.write(cmd.encode() + b'\r')
    com.flush()

    if is_pem:
        r = com.readall()
    else:
        # Search the response for the sent at command to be sure
        # that it has been sent before we proceed
        r = com.read()
        while str.find(r.decode(), cmd) < 0:
            r = r + com.read()

    # Read response until OK or ERROR received
    while r.find(b'OK') < 0 and r.find(b'ERROR') < 0 and r.find(b'>') < 0:
        r = r + com.readline()

    print(" %dms <- " % millis() + r.decode().strip('\r\n'))

    if r.find(b'ERROR') > 0:
        print('ERROR: {}'.format(cmd))
        sys.exit()
    return r


def wait_for_startup(com):
    # Read response until +STARTUP received
    r = com.read()
    while r.find(b'+STARTUP') < 0:
        r = r + com.read()
    return r


def check_for_incoming_edm_packet(com, verb: bool = False):

    global g_packet_type
    global g_channel_id
    global g_at_response_string

    # Read response until EDM_START received
    r = b''
    while r.find(EDM_START) < 0:
        ch = com.read()
        if not ch:
            if verb:
                print("no data")
            return
        if verb:
            print(ch)
            print("\n")
        r = r + ch

    # Read the EDM packet
    payload_length = com.read(2)
    length_int = struct.unpack('>H', payload_length)[0]
    payload = com.read(length_int)
    stop_byte = com.read(1)

    if stop_byte == EDM_STOP:
        payload_id_type = payload[:2]
        payload_data = payload[2:]
        print(" %dms " % millis(), end='')

        if payload_id_type.decode() == AT_CONFIRMATION:
            g_packet_type = at_confirmation
            print('AT response: ' + payload_data.decode().strip('\r\n'))
            g_at_response_string = payload_data.decode()
            return 0

        elif payload_id_type.decode() == AT_EVENT:
            g_packet_type = at_event
            print('AT event: ' + payload_data.decode().strip('\r\n'))
            return 2

        elif payload_id_type.decode() == CONNECT_EVENT:
            g_packet_type = connect_event
            g_channel_id = payload_data[0]
            connect_type = payload_data[1]
            if connect_type == BLUETOOTH:
                bt_profile = payload_data[2]
                if bt_profile == SPS:
                    bd_address = payload_data[3:9]
                    frame_size = payload_data[9:]
                    print('Connect event Bluetooth SPS:')
                    print('Channel id: ' + str(g_channel_id))
                    print('BD Address: ')
                    for x in (bd_address):
                        print(hex(x)[2:].zfill(2) + ':', end='')
                    print('Frame size: ')
                    for x in frame_size:
                        print(hex(x)[2:].zfill(2) + ':', end='')
                else:
                    print('Packet type not implemented')
            elif connect_type == IPv4:
                print('Connect event IPv4')
                print('\tChannel id: ' + str(g_channel_id))
            else:
                print('Packet type not implemented')
                return 99
            return 1

        elif payload_id_type.decode() == DISCONNECT_EVENT:
            g_packet_type = disconnect_event
            g_channel_id = payload_data[0]
            print('Disconnect event:')
            print('Channel id: ' + str(g_channel_id) + '\n')
            return 9

        elif payload_id_type.decode() == DATA_EVENT:
            g_packet_type = data_event
            g_channel_id = payload_data[0]
            data = payload_data[1:]
            print('Data event:')
            print('\tChannel id: ' + str(g_channel_id))
            print('\tData: ' + data.decode() + '\n')
            return data

        elif payload_id_type.decode() == START_EVENT:
            g_packet_type = start_event
            print('Start event\n')

        else:
            print('Packet type not implemented')

    else:
        print('Invalid packet')


def send_edm_packet(com, payload):
    _length = len(payload)
    payload_length = struct.pack('>H', _length)
    packet = EDM_START + payload_length + payload + EDM_STOP
    print(" %dms -> 0x%02X%02X%02X%02X%02X %s 0x%02X" %
          (millis(), packet[0], packet[1], packet[2], packet[3], packet[4], repr(packet[5:-1].decode()), packet[-1]))
    com.write(packet)


def generate_edm_at_request(at_command):
    payload_id_type = AT_REQUEST
    payload = payload_id_type + at_command
    return payload.encode()


def generate_edm_data_payload(ch, data):
    payload_id_type = DATA_COMMAND
    channel_byte = struct.pack('>B', ch)
    payload = payload_id_type.encode() + channel_byte + data
    return payload


def wait_edm_ok_response(ch):
    global g_at_response_string
    g_at_response_string = ''
    while (g_at_response_string != '\r\nOK\r\n'):
        check_for_incoming_edm_packet(ch)
        time.sleep(0.1)
        if(g_at_response_string == '\r\nERROR\r\n'):
            return
    return


def main(argv):

    global g_packet_type
    global g_channel_id
    global g_at_response_string

    comport = sys.argv[1]

    # Open COMx at 115200 8-N-1, read timeout set to 1s
    ser = serial.Serial(port=comport, baudrate=115200,
                        rtscts=True, timeout=1)

    while(True):
        print(ser.name + ' open')
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        # Factory reset to start fresh
        send_at_command(ser, 'AT+UFACTORY')
        send_at_command(ser, 'AT+CPWROFF')
        wait_for_startup(ser)

        # For NINA-W15 and NINA-W13, clean ROM bootloader print
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        f = open(path_to_CA)
        ca = f.read()
        f.close()

        send_at_command(ser, 'AT+USECMNG=0,0,ca.pem,' + str(len(ca)) + '\r')
        send_at_command(ser, ca.strip('\n'), True)

        f = open(path_to_Cert)
        cert = f.read()
        f.close()

        send_at_command(ser, 'AT+USECMNG=0,1,cert.pem,' +
                        str(len(cert)) + '\r')
        send_at_command(ser, cert.strip('\n'), True)

        f = open(path_to_key)
        key = f.read()
        f.close()

        send_at_command(ser, 'AT+USECMNG=0,2,key.pem,' + str(len(key)) + '\r')
        send_at_command(ser, key.strip('\n'), True)

        # Enter Extended Data Mode
        send_at_command(ser, "ATO2")
        time.sleep(2)
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        at_payload = generate_edm_at_request('AT+UWSC=0,2,' + SSID + '\r')
        send_edm_packet(ser, at_payload)
        check_for_incoming_edm_packet(ser)

        at_payload = generate_edm_at_request('AT+UWSC=0,5,2\r')
        send_edm_packet(ser, at_payload)
        check_for_incoming_edm_packet(ser)

        at_payload = generate_edm_at_request('AT+UWSC=0,8,' + PASSWORD + '\r')
        send_edm_packet(ser, at_payload)
        check_for_incoming_edm_packet(ser)

        at_payload = generate_edm_at_request('AT+UWSCA=0,3\r')
        send_edm_packet(ser, at_payload)
        check_for_incoming_edm_packet(ser)

        # +UUWLE:0,A281F1CC3782,6
        while check_for_incoming_edm_packet(ser) != 2:
            time.sleep(1)

        # +UUNU:0
        while check_for_incoming_edm_packet(ser) != 2:
            time.sleep(1)

        # +UUNU:0
        while check_for_incoming_edm_packet(ser) != 2:
            time.sleep(1)

        time.sleep(3)

        at_payload = generate_edm_at_request('AT+UDCP=mqtt://' + iothubhostname + ':8883/?' +
                                             'client=' + registration_Id +
                                             '&user=' + idScope + '/registrations/' + registration_Id + '/api-version=2019-03-31' +
                                             '&pt=$dps/registrations/PUT/iotdps-register/?$rid={request_id}' +
                                             '&st=$dps/registrations/res/#' +
                                             '&encr=3' +
                                             '&keepAlive=60' +
                                             '&ca=ca.pem' +
                                             '&cert=cert.pem' +
                                             '&privKey=key.pem\r')
        send_edm_packet(ser, at_payload)
        check_for_incoming_edm_packet(ser)

        while check_for_incoming_edm_packet(ser) != 2:
            time.sleep(1)

        data_payload = generate_edm_data_payload(0,
                                                 "{\"payload\":\"\",\"registrationId\":\"ninadps\"}".encode())
        send_edm_packet(ser, data_payload)
        operationId = check_for_incoming_edm_packet(ser)
        operationId = json.loads(operationId.decode())
        operationId = operationId["operationId"]

        status_topic = "$dps/registrations/GET/" + \
            "iotdps-get-operationstatus/?$rid={request_id}&operationId=" + \
            operationId

        at_payload = generate_edm_at_request(
            'AT+UDUV=0,' + status_topic + "\r")
        send_edm_packet(ser, at_payload)
        check_for_incoming_edm_packet(ser)

        at_payload = generate_edm_at_request('AT+UDCP=mqtt://' + iothubhostname + ':8883/?' +
                                             'client=' + registration_Id +
                                             '&user=' + idScope + '/registrations/' + registration_Id + '/api-version=2019-03-31' +
                                             "&pt=%%0" +
                                             '&encr=3' +
                                             '&keepAlive=60' +
                                             '&ca=ca.pem' +
                                             '&cert=cert.pem' +
                                             '&privKey=key.pem\r')
        send_edm_packet(ser, at_payload)
        check_for_incoming_edm_packet(ser)

        while check_for_incoming_edm_packet(ser) != 2:
            time.sleep(1)

        data_payload = generate_edm_data_payload(
            1, "get operationstatus".encode())

        dps_status = ""
        for i in range(3):
            send_edm_packet(ser, data_payload)
            dps_status = check_for_incoming_edm_packet(ser)
            dps_status = json.loads(dps_status.decode())
            dps_status = dps_status["status"]
            if(dps_status == "assigned"):
                break
            time.sleep(2)

        if(dps_status == "assigned"):
            print("Successfully Assigned")
        else:
            print("DPS fail")

        # Power off to get back to AT mode
        at_payload = generate_edm_at_request('AT+UFACTORY\r')
        at_payload = generate_edm_at_request('AT+CPWROFF\r')
        send_edm_packet(ser, at_payload)
        check_for_incoming_edm_packet(ser)
        wait_for_startup(ser)

        sys.stdout.flush()
        ser.close()
        exit()


if __name__ == '__main__':
    main(sys.argv)
