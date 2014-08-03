#!/usr/bin/env python

# browser simulation of user interacting with 300x255px ad on this page: http://www.moat.com/search/results?q=Google&ad=499142
# user moves towards the ad, going slower as to make sure they hit it.
# threading is used to log every .1 second
# random integer is used to make imperfection in the motion towards button.
# __author: Jonathan Kiritharan : June 2014

import time, sys, threading, random
from datetime import datetime, date
global user_excitement

class Browser:#the environment for the simulation
	width="bb"
	height=0
	ad = {}
	ad_button = {}
	def __init__(self,width,height):
		self.width = width
		self.height = height

	def drawAd(self,xpos,ypos,width,height):
		self.ad['xpos'] = 800
		self.ad['ypos'] = 17
		self.ad['width'] = 300
		self.ad['height'] = 255
	def drawAdButton(self,ad,button_xpos,button_ypos,button_width,button_height):
		self.ad_button['xpos'] = ad['xpos'] + button_xpos
		self.ad_button['ypos'] = ad['ypos'] + button_ypos
		self.ad_button['width'] = button_width
		self.ad_button['height'] = button_height
	def makePartition(self):
		self.right_of_ad = self.ad['xpos'] + self.ad['width']
		self.right_of_ad_button = self.ad_button['xpos'] + self.ad_button['width']
		self.below_ad = self.ad['ypos'] + self.ad['height']
		self.below_ad_button = self.ad_button['ypos'] + self.ad_button['height']


class Cursor:#the cursor for simulation
	xpos = 0
	ypos = 0
	position = [xpos,ypos]
	def moveCursor(self,input_xpos,input_ypos):#returns array of cursor's xpos and ypos
		self.xpos += input_xpos
		self.ypos += input_ypos
		self.position = [self.xpos,self.ypos]
		return self.position
	def curPosition(self):
		return self.position
	def deviateCursor(self,upper):#add a bit of random/imperfect motion towards button
		x = random.randrange(0,upper)
		return float(x)/1000



class User(Browser,Cursor):#User uses both Browser and Cursor. it is playing off of both
	def __init__(self,time_limit):
		self.time_limit = time_limit
		self.in_button_x = False
		self.been_in_button_x = False
		self.in_button_y = False
		self.been_in_button_y = False
		if Browser.width < 0 or Browser.height < 0:
			print "Your browser size contains a negative number"
			sys.exit()
		if Cursor.xpos > Browser.width or Cursor.xpos < 0 or Cursor.ypos > Browser.height or Cursor.ypos < 0:
			print "Your cursor is outside of the browser"
			sys.exit()

	def evalPosition(self,Browser,Cursor):#evaluate the position of cursor and return the suggested coordinates
		if 0 <= Cursor.xpos <= Browser.ad['xpos']:
			input_x = user_excitement + Cursor.deviateCursor(3)#initially fast-moving, getting to ad
		elif Browser.ad['xpos'] <= Cursor.xpos <= Browser.ad_button['xpos']:
			input_x = user_excitement + Cursor.deviateCursor(2)#slow down for mouseover
		#in the button
		elif Browser.ad_button['xpos'] <= Cursor.xpos <= Browser.right_of_ad_button:
			input_x = (user_excitement/2) + Cursor.deviateCursor(1)
			self.in_button_x = True
		#slow while close to the ad then speed up
		elif Browser.right_of_ad_button <= Cursor.xpos <= Browser.right_of_ad:
			self.been_in_button_x = True
			input_x = user_excitement + Cursor.deviateCursor(2)
		elif Browser.right_of_ad <= Cursor.xpos <= Browser.width-20:#until 20px from edge
			input_x = (user_excitement + Cursor.deviateCursor(4))
		else:
			input_x = (user_excitement+Cursor.deviateCursor(3))*-1#start going other direction
		
		#ypos

		if 0 <= Cursor.ypos <= Browser.ad['ypos']:
			input_y = user_excitement + Cursor.deviateCursor(3)
		elif Browser.ad['ypos'] <= Cursor.ypos <= Browser.ad_button['ypos']:
			input_y = user_excitement + Cursor.deviateCursor(2)
		#in the button
		elif Browser.ad_button['ypos'] <= Cursor.ypos <= Browser.below_ad_button:
			input_y = (user_excitement/2) + Cursor.deviateCursor(1)
			self.in_button_y = True
		#leave slow then speed up
		elif Browser.below_ad_button <=  Cursor.ypos <= Browser.below_ad:
			self.been_in_button_y = True
			input_y = user_excitement + Cursor.deviateCursor(2)
		elif Browser.below_ad <= Cursor.ypos <= Browser.height-20:
			input_y = (user_excitement + Cursor.deviateCursor(4))
		else:
			input_y = (user_excitement + Cursor.deviateCursor(3))*-1

		#check if cursor is in button. If one axis is, and the other has never been, the other one should catch up
		if self.in_button_y == True and self.in_button_x == False:
			if self.been_in_button_x == False:
				input_x += .3
		if self.in_button_x == True and self.in_button_y == False:
			if self.been_in_button_y == False:
				input_y += .3

		return [input_x,input_y]


	def logCursor(self,Cursor):#this could go into an sql db
		a = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
		print str(Cursor.curPosition()) + " @ " + str(a)

	def buildLog(self,Cursor):
		x = 0#iterator
		milli = .1#add per iteration
		while x < self.time_limit * 10:
			threading.Timer(milli, self.logCursor,(Cursor,)).start()
			milli += .1
			x += 1
		
	

user_excitement = .0005#how quickly the user gets to the ad.
web = Browser(1366,768)#width and height
#draw ad on in there
web.drawAd(800,17,300,255)#xposition,yposition,width and height
web.drawAdButton(web.ad,105,195,80,25)#place button within ad
web.makePartition()#function for making variables and partitions a bit more legible
usr = User(15)#int passed is time limit in seconds
cur = Cursor()#cursor position
start_time = round(time.time()*10)#start the timer so program knows when to end
stop_time = start_time + (usr.time_limit*10)#x seconds from RIGHT NOW-- static var
usr.buildLog(cur)#build and begin the threading log
m = 0
while 1:
	cur_time = round(time.time()*10)#time right now to see if we should continue
	if stop_time >= cur_time:
		to_move = usr.evalPosition(web,cur)
		cur.moveCursor(to_move[0],to_move[1])
	else:
		print "simulation over"
		sys.exit()

	