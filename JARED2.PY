#! /usr/bin/env python
#******************************************************************************
# Senior Design RoboHockey
# Nicknamed: Jared
# Spring 2006
#
#******************************************************************************

import serial
import time
from bestfit import *
import math
from cmucam import cmucam

cmu = cmucam() #global cmu interface

class sensorclass:
    """Prediction making class.  Communicates with the CMUCam, collects the data and returns predictions."""

    def __init__(self):
        """Communicates with the CMUCam2"""
        #initialize variables
    
        self.Y = 127  #pixel width in Y direction
        self.xscale=2.2
        Y = self.Y
        self.offset = 7
        #initialize past data
        self.x = []
        self.y = []
        self.DTx = [] 
        self.DTy = []
        self.dt = []
        self.vxar = []
        self.oT = time.clock()
        self.nT = self.oT
        #begin playing the game

        #for testing purposes only
        self.xf = 0
        self.yf = 0
        self.fname = 'Final/datafile.txt'
        f = open(self.fname, 'w')
        f.write('x\ty\tDTx\tDTy\tv\ttheta\tt\txf\tyf\n')
        f.close()
       

    def prediction(self, m, b, vx, newx):
        """USAGE: theta, t = prediction(self, m, b, vx, newx)
        Returns a prediction of where the puck will end up and how long it will take it to get there.
        """
                
        Y = self.Y
        notime = 999
        maxtheta = 60
        armtogoal = -17*self.xscale
        xo = 28.0*self.xscale  #the x offset for the circle
        yo = Y/2  #the y offset for the circle
        r = 28.0*self.xscale   #the radius of the circle
        ##        b0 = mky(b, Y, b/Y)
        ##        x = armtogoal
        y = m*armtogoal+b
        ##        while pow(r,2) < pow((y-yo), 2) + pow((x+xo),2):
        ##            if y <= Y:
        ##                # will hit the flat part of the back wall
        ##                if y > Y/2: return maxtheta, notime
        ##                else: return -maxtheta, notime
        ##            else: yo = yo+Y
        ##        b_old = b
        ##        b = b0
        z=0

        order=[0,1,-1,2,-2,3,-3,4,-4,5,-5,6,-6,7,-7,8,-8]
        x1 = 0
        x2 = 0
        done = 0
        qq=0
        for q in order:
            try:
                x1=(pow((pow(m,2)+1)*pow(r,2)-pow(b,2)+2*b*(m*xo+(yo+q*Y))-pow(m,2)*pow(xo,2)-2*m*xo*(yo+q*Y)-pow((yo+q*Y),2),.5)-b*m+m*(yo+q*Y)-xo)/(pow(m,2)+1)
                x2=-(pow((pow(m,2)+1)*pow(r,2)-pow(b,2)+2*b*(m*xo+(yo+q*Y))-pow(m,2)*pow(xo,2)-2*m*xo*(yo+q*Y)-pow((yo+q*Y),2),.5)+b*m-m*(yo+q*Y)+xo)/(pow(m,2)+1)
                break 
            except:
                if y <= q*Y+Y and y>= q*Y:
                    if y > q*Y+yo: return pow(-1, q)*maxtheta, notime
                    return -pow(-1,q)*maxtheta, notime
        
        xf=max(x1,x2)
        yf=m*xf+b


        #for tests only
        self.xf = xf
        self.yf = yf
        #end for tests only        
        theta =  pow(-1, q)*math.degrees(math.atan((yf-yo-Y*q)/(xf+xo)))
        if vx == 0: vx = .0001
        t = (newx-xf)/vx

        return theta, t


    def look(self):
        """Usage: obj.look()
        Aquires new data from the CMUcam and returns a prediction angle and time (in seconds) for where and when the puck will contact the arm.

        returns theta, t
        """
    
        notime = 999
        newx, newy = cmu.getPos()
        newx=round(newx*self.xscale)
        newy = newy
        
        #print 'x = ' + str(newx) + 'y = ' + str(newy)
        #try:
        self.oT = self.nT
        #except:
        #    oldT = time.clock()
        self.nT = time.clock()	
        newdt = self.nT-self.oT

        if not (newx and newy):
            # returns 0, notime when there is no new data.
            
            #clear past data
            self.x = []
            self.y = []
            self.DTx = [] 
            self.DTy = []
            self.dt = []
            self.vxar = []
            return 0, notime*4

        elif not(self.DTx and self.DTy):
            # returns 0, notime when there is no historical data.
            
            #update historical data
            self.x.append(newx)
            self.DTx.append(newx)
            self.y.append(newy)
            self.DTy.append(newy)
            self.dt.append(newdt)
            self.vxar=[]
            return 0, notime*2

        elif newx > self.x[-1]:
            # x is increasing (moving away from arm)
            # no prediction is necessary

            #reset past data
            self.x = [newx]
            self.y = [newy]
            self.DTx = [newx] 
            self.DTy = [newy]
            self.dt = [newdt]
            self.vxar = []
            return 0, notime*3

        self.x.append(newx)
        self.y.append(newy)
        self.dt.append(newdt)
        self.vxar.append((self.x[-2]-self.x[-1])/self.dt[-1])
        self.vx = sum(self.vxar)/len(self.vxar)
        
        # the puck is comming our way!  Lets make a prediction!

        # Apply the Dave Transform for the newx and newy values
        # this will add the transposed value to the DTx and DTy transposed 
        # coordinate array
        self.DTx, self.DTy = DT(self.DTx, self.DTy, newx, newy, self.Y)
        
           
        # get the bestfit parameters of the data
        self.m, self.b, self.r = bestfit(self.DTx, self.DTy)

        
        self.theta, self.t = self.prediction(self.m, self.b, self.vx, newx)

        #START for test purposes only
        #'x\ty\tDTx\tDTy\tv\ttheta\txf\t\xy\tt\n'
        if len(self.x):
            f = open(self.fname, 'a')
            #print 'writing to file'
            f.write( str(self.x[-1])+'\t'+str(self.y[-1])+'\t'+str(self.DTx[-1])+'\t'+str(self.DTy[-1])+'\t'+str(self.vx)+'\t'+str(self.theta)+'\t'+str(self.t)+'\t'+str(self.xf)+'\t'+str(self.yf)+'\n')
            f.close()
        #END for test purposes only
            
        return self.theta, self.t
        
        #also need to apply a simple function to do conversion to cm, but perhapse more easily we could convert the theta of the arm into pixels


class armclass:
    """Arm interface to CMUCam2 servos."""
    def __init__(self):
        cmu.sendCMD('so 0 0')
        cmu.sendCMD('so 1 0')
        cmu.sendCMD('so 2 0')
        cmu.sendCMD('so 3 0')
        cmu.sendCMD('so 4 0')

    def move1(self, servo, angle):
        pos = int(round(112 +.9939*angle))
        if (pos>160): pos=170
        if (pos<100): pos=70
        cmu.sendCMD('sv ' +str(servo) + ' ' + str(pos))

    def move(self, angle):
        """Usage: arm.move(<angle>);
        Moves big servo to angle and small servo to point straight"""
        self.move1(0,angle)
        self.move1(2,-angle)

    def hit(self):
        """kick out for .05s then retract"""
        cmu.sendCMD('so 4 1')
        time.sleep(.05)
        cmu.sendCMD('so 4 0')


class brain:
    """Handles the brain activitiy of Jared.hockey"""
    def __init__(self):
        self.arm = armclass()
        self.sensor = sensorclass()
        self.actuator_delay = 0
        
    def play(self):
        """Loop to play the game"""
        cnt = 100
        actdelay = .05
        while cnt:
            #for testing use
            #cnt = cnt - 1
            
            theta, t = self.sensor.look()
    
            if t - actdelay <= (1/25):                
                #time.sleep(t-actdelay)
                self.arm.hit()
                print 'i hit'
                
            if abs(theta) > 0:
                print 'theta = ' + str(theta) + '\tt = ' + str(t)
            self.arm.move(theta)

    def test(self):
        """Used to test the accuracy of the theta predictions."""
        tarray = [];
        timear = []
        richochet = []
        bigtheta = []
        bigtime = []
        bigrico = []
        bigactual = []
        cnt = 30
        fnum = 0        
        for j in range(cnt):
            fnum = fnum+1
            richochet = []
            tarray = []
            timear = []
            while 1:            
                theta, t = self.sensor.look()
                                    
                if len(tarray) >= 1 and abs(tarray[-1])>0 and theta == 0:
                    actual = input(str(j) + '. angle: ')
                    
                    #f = open('trial'+str(fnum)+'.txt', 'w')
                    #for k in range(len(tarray)):
                        #f.write(str(tarray(k))+'\t'+str(actual)+'\t'+str(timear(k))+'\t'+str(ricochet)+'\n')
                    break

                    
                else:
                    if theta > 0:
                        tarray.append(theta)   
                        timear.append(t)
                        if not(self.sensor.DTy[-1]== self.sensor.y[-1]):
                            richochet.append(1)
                        else:
                            richochet.append(0)

            #populate 2d arrays
            #if not(actual == 999):
            bigtheta.append(tarray)
            bigtime.append(timear)
            bigrico.append(richochet)
            bigactual.append(actual)

        
        #analyze the data
        norico = []
        rico = []
        for k in range(len(bigactual)):

            #before and after richochet

            #NOTE:  The ricochet and non richoche data only collects if there was a ricochet somwewhere in the hit
            #therefore the Before Ricochet is not counting striaght line pucks.  This would not be what we want.            
            for t in range(len(bigrico[k])):
                if not(bigrico[k][t]) and sum(bigrico[k])>0:
                    norico.append(abs(bigtheta[k][t] - bigactual[k]))
                elif bigrico[k][t]:
                    #make sure that you're not counting data that never has a ricochet
                    rico.append(abs(bigtheta[k][t] - bigactual[k]))
        lens = []                       
        for k in range(len(bigactual)):
            lens.append(len(bigtheta[k]))
        maxlen = max(lens)

        points = []
        for j in range(maxlen):
            oned = []
            for k in range(len(bigactual)):
                if len(bigtheta[k]) > j:
                    oned.append(bigtheta[k][j]- bigactual[k])
            
            points.append(oned)
            
        print
        print '********************************'
        print 'TEST RESULTS'
        print
        print 'These results are the average deviation of the predicted result from the actual'
        print

              
        if len(rico) == 0:
            print 'AFTER RICHOCHET       NO DATA'
        else:
            print 'AFTER RICOCHET:       ' + str( sum(rico)/len(rico))
        if len(norico) == 0:
            print 'BEFORE RICOCHET:   NO DATA'  
        else:
            print 'BEFORE RICOCHET:   ' + str( sum(norico)/len(norico))
        print
        print 'NUMBER OF POINTS:'
        for j in range(len(points)):
            print str(j) +'\t'+str(sum(points[j])/len(points[j]))
            
        print '********************************'

    
Jared = brain()
Jared.test()
