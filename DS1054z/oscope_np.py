#!/usr/bin/env python

from telnetlib_receive_all import Telnet
from Rigol_functions import *
import time
import StringIO
import sys
import os
import platform
import logging
import numpy as np
from io import StringIO as StringIO2
import matplotlib.pyplot as plt

__version__ = 'v1.1.0'
# Added TMC Blockheader decoding
# Added possibility to manually allow run for scopes other then DS1000Z
__author__ = 'RoGeorge'

#
# TODO: Write all SCPI commands in their short name, with capitals
# TODO: Add ignore instrument model switch instead of asking
#
# TODO: Detect if the scope is in RUN or in STOP mode (looking at the length of data extracted)
# TODO: Add logic for 1200/mdep points to avoid displaying the 'Invalid Input!' message
# TODO: Add message for csv data points: mdep (all) or 1200 (screen), depending on RUN/STOP state, MATH and WAV:MODE
# TODO: Add STOP scope switch
#
# TODO: Add debug switch
# TODO: Clarify info, warning, error, debug and print messages
#
# TODO: Add automated version increase
#
# TODO: Extract all memory datapoints. For the moment, CSV is limited to the displayed 1200 datapoints.
# TODO: Use arrays instead of strings and lists for csv mode.
#
# TODO: variables/functions name refactoring
# TODO: Fine tune maximum chunk size request
# TODO: Investigate scaling. Sometimes 3.0e-008 instead of expected 3.0e-000
# TODO: Add timestamp and mark the trigger point as t0
# TODO: Use channels label instead of chan1, chan2, chan3, chan4, math
# TODO: Add command line parameters file path
# TODO: Speed-up the transfer, try to replace Telnet with direct TCP
# TODO: Add GUI
# TODO: Add browse and custom filename selection
# TODO: Create executable distributions

# Rigol/LXI specific constants
port = 5555

big_wait = 10
smallWait = 1

company = 0
model = 1
serial = 2

# Check command line parameters
script_name = os.path.basename(sys.argv[0])

IP_DS1104Z = sys.argv[1]

#Uncomment this if ping check is to be included in the sequence
if False:
    # Check network response (ping)
    if platform.system() == "Windows":
        response = os.system("ping -n 1 " + IP_DS1104Z + " > nul")
    else:
        response = os.system("ping -c 1 " + IP_DS1104Z + " > /dev/null")

    if response != 0:
            print
            print "WARNING! No response pinging " + IP_DS1104Z
            print "Check network cables and settings."
            print "You should be able to ping the oscilloscope."


# Open a modified telnet session
# The default telnetlib drops 0x00 characters,
#   so a modified library 'telnetlib_receive_all' is used instead
tn = Telnet(IP_DS1104Z, port)
instrument_id = command(tn, "*IDN?")    # ask for instrument ID

# Check if instrument is set to accept LAN commands
if instrument_id == "command error":
    print "Instrument reply:", instrument_id
    print "Check the oscilloscope settings."
    print "Utility -> IO Setting -> RemoteIO -> LAN must be ON"
    sys.exit("ERROR")

# Check if instrument is indeed a Rigol DS1000Z series
id_fields = instrument_id.split(",")
if (id_fields[company] != "RIGOL TECHNOLOGIES") or \
        (id_fields[model][:3] != "DS1") or (id_fields[model][-1] != "Z"):
    print "Found instrument model", "'" + id_fields[model] + "'", "from", "'" + id_fields[company] + "'"
    print "WARNING: No Rigol from series DS1000Z found at", IP_DS1104Z
    print
    typed = raw_input("ARE YOU SURE YOU WANT TO CONTINUE? (No/Yes):")
    if typed != 'Yes':
        sys.exit('Nothing done. Bye!')

print "Instrument ID:",
print instrument_id

scope_data = None

# TODO: Change WAV:FORM from ASC to BYTE
if True:
    # Put the scope in STOP mode - for the moment, deal with it by manually stopping the scope
    # TODO: Add command line switch and code logic for 1200 vs ALL memory data points
    # tn.write("stop")
    # response = tn.read_until("\n", 1)

    # Scan for displayed channels
    scaleList = []
    chanList = []
    offsetList = []
    for channel in ["CHAN1", "CHAN2", "CHAN3", "CHAN4", "MATH"]:
        response = command(tn, ":" + channel + ":DISP?")

        # If channel is active
        if response == '1\n':
            chanList += [channel]
            response = command(tn,':'+channel+":SCALe?")
            print 'scale for channel %s:%s'%(channel,response)
            scaleList += [float(response)]

            response = command(tn,':'+channel+":OFFSet?")
            print 'offset for channel %s:%s'%(channel,response)
            offsetList += [float(response)]

    # the meaning of 'max' is   - will read only the displayed data when the scope is in RUN mode,
    #                             or when the MATH channel is selected
    #                           - will read all the acquired data points when the scope is in STOP mode
    # TODO: Change mode to MAX
    # TODO: Add command line switch for MAX/NORM
    command(tn, ":WAV:MODE NORM")
    command(tn, ":WAV:STAR 0")
    command(tn, ":WAV:MODE NORM")

    csv_buff = ""

    print scaleList
    print offsetList

    # for each active channel
    for (channel, scale, offset) in zip(chanList,scaleList,offsetList):
        # Set WAVE parameters
        command(tn, ":WAV:SOUR " + channel)
        command(tn, ":WAV:FORM ASC")

        # MATH channel does not allow START and STOP to be set. They are always 0 and 1200
        if channel != "MATH":
            command(tn, ":WAV:STAR 1")
            command(tn, ":WAV:STOP 1200")

        buff = ""
        print "Data from channel '" + str(channel) + "', points " + str(1) + "-" + str(1200) + ": Receiving..."
        buffChunk = command(tn, ":WAV:DATA?")

        # Just in case the transfer did not complete in the expected time
        while buffChunk[-1] != "\n":
            logging.warning("The data transfer did not complete in the expected time of " +
                            str(smallWait) + " second(s).")

            tmp = tn.read_until("\n", smallWait)
            if len(tmp) == 0:
                break
            buffChunk += tmp
            logging.warning(str(len(tmp)) + " leftover bytes added to 'buff_chunks'.")

        # Append data chunks
        # Strip TMC Blockheader and terminator bytes
        buff += buffChunk[tmc_header_bytes(buffChunk):-1] + ","

        # Strip the last \n char
        buff = buff[:-1]

        # Process data
        buff_list = buff.split(",")
        io_buff = StringIO2(unicode(buff))
        chan_data = (1/scale)*np.genfromtxt(io_buff,delimiter=',')
        chan_data = chan_data + offset

        if scope_data is None:
            scope_data = np.array([chan_data])
        else:
            scope_data = np.append(scope_data,[chan_data],axis=0)
        print chan_data

print scope_data

plt.plot(scope_data[0])
plt.plot(scope_data[1])
plt.show()
tn.close()
