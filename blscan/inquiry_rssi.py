"""PyBluez advanced example inquiry-with-rssi.py

Perform a simple device inquiry, followed by a remote name request of each
discovered device
"""

import struct
import sys

import bluetooth
import bluetooth._bluetooth as bluez  # low level bluetooth wrappers

def printpacket(pkt):
    for c in pkt:
        sys.stdout.write("{%02x} ".format(struct.unpack("B", c)[0]))

def read_inquiry_mode(sock):
    """returns the current mode, or -1 on failure"""
    # save current filter
    old_filter = sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    # Setup socket filter to receive only events related to the
    # read_inquiry_mode command
    flt = bluez.hci_filter_new()
    opcode = bluez.cmd_opcode_pack(bluez.OGF_HOST_CTL,
                                   bluez.OCF_READ_INQUIRY_MODE)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    bluez.hci_filter_set_event(flt, bluez.EVT_CMD_COMPLETE)
    bluez.hci_filter_set_opcode(flt, opcode)
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt)

    # first read the current inquiry mode.
    bluez.hci_send_cmd(sock, bluez.OGF_HOST_CTL,
                       bluez.OCF_READ_INQUIRY_MODE)

    pkt = sock.recv(255)
    status, mode = struct.unpack("xxxxxxBB", pkt)

    # restore old filter
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, old_filter)

    return mode

def write_inquiry_mode(sock, mode):
    """returns 0 on success, -1 on failure"""
    # save current filter
    old_filter = sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    # Setup socket filter to receive only events related to the
    # write_inquiry_mode command
    flt = bluez.hci_filter_new()
    opcode = bluez.cmd_opcode_pack(bluez.OGF_HOST_CTL,
                                   bluez.OCF_WRITE_INQUIRY_MODE)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    bluez.hci_filter_set_event(flt, bluez.EVT_CMD_COMPLETE)
    bluez.hci_filter_set_opcode(flt, opcode)
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt)

    # send the command!
    bluez.hci_send_cmd(sock, bluez.OGF_HOST_CTL,
                       bluez.OCF_WRITE_INQUIRY_MODE,
                       struct.pack("B", mode))

    pkt = sock.recv(255)
    status = struct.unpack("xxxxxxB", pkt)[0]

    # restore old filter
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, old_filter)
    if not status:
        return -1

    return 0

def device_inquiry_with_rssi(devices, sock):
    # save current filter
    old_filter = sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    # perform a device inquiry on bluetooth device #0
    # The inquiry should last 8 * 1.28 = 10.24 seconds
    # before the inquiry is performed, bluez should flush its cache of
    # previously discovered devices
    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt)

    duration = 4
    max_responses = 255
    cmd_pkt = struct.pack("BBBBB", 0x33, 0x8b, 0x9e, duration, max_responses)
    bluez.hci_send_cmd(sock, bluez.OGF_LINK_CTL, bluez.OCF_INQUIRY, cmd_pkt)

    while True:
        pkt = sock.recv(255)
        ptype, event, plen = struct.unpack("BBB", pkt[:3])
        #print("Event: {}".format(event))
        if event == bluez.EVT_INQUIRY_RESULT_WITH_RSSI:
            pkt = pkt[3:]
            nrsp = bluetooth.get_byte(pkt[0])
            for i in range(nrsp):
                addr = bluez.ba2str(pkt[1+6*i:1+6*i+6])
                if addr in devices:
                    rssi = bluetooth.byte_to_signed_int(
                        bluetooth.get_byte(pkt[1 + 13 * nrsp + i]))
                    devices[addr]["rssi"] = rssi
        elif event == bluez.EVT_INQUIRY_COMPLETE:
            break
        elif event == bluez.EVT_CMD_STATUS:
            status, ncmd, opcode = struct.unpack("BBH", pkt[3:7])
            if status:
                printpacket(pkt[3:7])
                break
        elif event == bluez.EVT_INQUIRY_RESULT:
            pkt = pkt[3:]
            nrsp = bluetooth.get_byte(pkt[0])
            for i in range(nrsp):
                addr = bluez.ba2str(pkt[1+6*i:1+6*i+6])
                if addr in devices:
                    devices[addr]["rssi"] = None
        else:
            print("Unrecognized packet type 0x{:02x}.".format(ptype))

    # restore old filter
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, old_filter)

def get_rssi_for_devices(devices):
    dev_id = 0
    sock = bluez.hci_open_dev(dev_id)
    mode = read_inquiry_mode(sock)
    #print("Current inquiry mode is", mode)
    if mode != 1:
        write_inquiry_mode(sock, 1)

    device_inquiry_with_rssi(devices, sock)
