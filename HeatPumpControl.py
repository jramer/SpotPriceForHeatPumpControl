# -*- coding: utf-8 -*-
"""
Created on Sun Feb  8 23:38:32 2015

HeatPumpControl 0.4

This is a python3 program that will read a list of commands from a file and
will then control a Thermia heatpump, with a thermiq controller card, according to the data.

Author:
Arttu Huttunen
Oulu, Finland
Created in 2015, changed 2021 by Joakim Ramer

/*
 * ----------------------------------------------------------------------------
 * The MIT License (MIT)
 * Copyright (c) 2015 Arttu Huttunen
 * Anyone is free to do whatever they want with this code, at their own risk.
 * ----------------------------------------------------------------------------
 */


"""

#config file
configFile = './Settings.txt'


#Actual code starts here
#---------------------------------------------------------------------------
import sys, configparser, datetime, serial, os, requests

# Get current time and start a log line
currentTime = datetime.datetime.now()
logLine = []
logLine.append(str(currentTime) + ' HPC: ')
currentHour = datetime.datetime.now().hour


#A method for writing the log file, default to log.txt
def WriteLog(logLine, logFile = 'log.txt',logState = 'on'):
    logLine.append('\n')
    logLine = ''.join(logLine)
    if logState == 'on':
        with open(logFile, "a") as fol:
            fol.write(logLine)
    sys.exit()


try:
    # Read settings from a file
    config = configparser.ConfigParser()
    config.read(configFile)

    # Get settings *********************************** hardcoded stuff
    inputFile = config['Settings']['OutputFile']
    logState = config['Settings']['Log']
    logFile = config['Settings']['LogFile']
    serialPort = config['Settings']['SerialPort']
    serialBaudrate = config['Settings']['Baudrate']
    serialTimeout = config['Settings']['Timeout']
    roomTemp = config['Settings']['RoomTemp']
    minRoomTemp = config['Settings']['MinRoomTemp']
    poolTemp = config['Settings']['PoolTemp']
    waitPoolTemp = config['Settings']['WaitPoolTemp']
    roomReg = config['Settings']['RoomReg']
    poolReg = config['Settings']['PoolReg']
    sendCmdToPump = config['Settings']['SendCmdToPump']
    homeyURL = config['Settings']['HomeyURL']

    # Set up commands
    cmdRoomHeat = sendCmdToPump + ' ' + roomReg + ' ' + roomTemp
    cmdRoomWait = sendCmdToPump + ' ' + roomReg + ' ' + minRoomTemp
    cmdPoolHeat = sendCmdToPump + ' ' + poolReg + ' ' + poolTemp
    cmdPoolWait = sendCmdToPump + ' ' + poolReg + ' ' + waitPoolTemp

except:
    print(str(currentTime) + 'Error in reading configuration file. ')
    logLine.append('Error in reading configuration file. ')
    WriteLog(logLine)


try:
    isLowPriceArr = {}
    with open(inputFile) as f:
        for line in f:
           (key, val) = line.split(':')
           val = val.rstrip('\n')
           isLowPriceArr[int(key)] = val

except:
    print(str(currentTime) + 'Error in reading input file. ')
    logLine.append('Error in reading input file. ')
    WriteLog(logLine)

heatOrWait = isLowPriceArr[currentHour]
logLine.append(str(currentHour) + ':')
try:
    if heatOrWait == 'Heat':
        os.system(cmdRoomHeat)
        os.system(cmdPoolHeat)
        requests.get(homeyURL + roomTemp) #Send set room temp to homey virtual device
        logLine.append(' heating')
    else:
        os.system(cmdRoomWait)
        os.system(cmdPoolWait)
        requests.get(homeyURL + minRoomTemp) #Send set room temp to homey virtual device
        logLine.append(' waiting')
except:
    print(str(currentTime) + 'Error when running heatpump command. ')
    logLine.append('Error when running heatpump command. ')
    WriteLog(logLine)

# Finish by writing the a line to the log file if log in 'on'
logLine.append(' OK.')
WriteLog(logLine,logFile, logState )

# END OF PROGRAM
