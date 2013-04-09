jared.hockey
============

This was my senior design project which was to make a robot that played air hockey.  We named it Jared.  I used a CMUCAM2 to do the color tracking of the puck and control the servos.  It was the perfect device for the job.  It was one of my first python projects and a lot of fun.

I've got a full blog post and video on the project and the results here:

[http://thingsilearned.com/2007/06/25/jaredhockey-air-hockey-robotic-opponent/](http://thingsilearned.com/2007/06/25/jaredhockey-air-hockey-robotic-opponent/)

There are three files:

  - cmucam.py - a python wrapper for the CMUCAM2 serial port connector
  - bestfit.py - the algorithms to detect where the puck was going to go.  This included the infamous DT (Dave Transform) :)
  - jared.py - the main program that controlled the whole thing.

The project was quite a success.  It had been assigned for 6 years before us and I believe we were the only ones to have any success.  Unfortunately, mostly due to the arm (built by another team) not being powerful enough it didn't play offence at all.  We proved in a seperate experiment that it could block pretty much everything we threw at it.

<iframe width="100%" height="500" src="http://www.youtube.com/embed/YNbE-JMBF88" frameborder="0" allowfullscreen></iframe>

