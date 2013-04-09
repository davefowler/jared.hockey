#! /usr/bin/env python

import serial

class cmucam:
    """Simple Cmucam2 interface"""
    def __init__(self):
        """Initializes serial interface"""
        self.CMUserial =  serial.Serial(port = 0, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1)
        self.CMUserial.open() #start serial interface

        #cmucam initializations
        self.sendCMD('CR 17 0') #this is default sets camera to 50fps
        self.sendCMD('DS 1 1') #Down Sampling (should increase speed but decrease res)
        self.sendCMD('ST 200 240 200 240 100 240') #sets the color to track
        self.sendCMD('OM 0 3')   #puts a mask on the output, to only get Mx, My
        self.sendCMD('PM 1') #turns on single poll mode
        self.sendCMD('VW 1 1 72 142') #Virtual Window to get rid of lame area
        for i in range(20):  #loop
            self.getPos()    #20 fake getpos

        print "CMUcam2 initialize"

    def color(self, minR, maxR, minB, maxB, minG, maxG):
        """Change the color to track
        USAGE:  self.color(minR, maxR, minB, maxB, minG, maxG)"""
        return self.sendCMD('ST ' + str(minR) + ' ' + str(maxR) + ' ' + str(minB) + ' ' + str(maxB) + ' ' + str(minG) + ' ' + str(maxG))

    def open(self):
        self.CMUserial.open()

    def close(self):
        self.CMUserial.close()

    def sendCMD(self, s, tries=10):
        """Sends the command <s>.
        WARNING: DO NOT USE THIS FOR RETRIEVING CONTINUOUS DATA INSTEAD USE getData.
        Example: self.send('GV')   Gets the Version"""
        line = ''
        cnt = 0
        while line.find('ACK') < 0 and cnt < tries: #loop until 'ACK'nowledge or loop 10 times
            cnt = cnt + 1
            self.CMUserial.write(s+'\r')  #send the command
            line = self.CMUserial.readline(None, ':') #clean up response

        if line.find('ACK') < 0:
            return 'WARNING:  ' + s + ' NOT ACKNOWLEDGED AFTER ' + str(tries) + ' TRIES'

        return line.replace('ACK', '').replace('\r', '').replace(':', '')


    def getPos(self, s = 'TC'):
        """Sends the command <s> to retrive looped data."""
        self.CMUserial.write(s+'\r')
        self.CMUserial.readline(None, ' ')
        return [int(a) for a in self.CMUserial.readline(None,'\r').split(' ')]

    def __del__(self):
        self.close()

