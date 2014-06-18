#!/usr/bin/env python

# browser simulation of user interacting with 300x255px ad on this page: http://www.moat.com/search/results?q=Google&ad=499142
# user moves towards the ad, going slower as to make sure they hit it.
# threading is used to log every .1 second
# random integer is used to make imperfection in the motion towards button.
import time, sys, threading, random
from datetime import datetime, date
global user_excitement #for how eager the individual is to get to the button

class Browser:#the environment for the simulation
	ad = {}
	ad_button = {}
	def __init__(self,width,height):
		self.width = width
		self.height = height

	def draw_ad(self,xpos,ypos,width,height):
		self.ad['xpos'] = 800
		self.ad['ypos'] = 17
		self.ad['width'] = 300
		self.ad['height'] = 255
	def draw_ad_button(self,ad):
		self.ad_button['xpos']=ad['xpos']+105
		self.ad_button['ypos']=ad['ypos']+195
		self.ad_button['width']=80
		self.ad_button['height']=25
	def make_partition(self):
		self.right_of_ad=self.ad['xpos']+self.ad['width']
		self.right_of_ad_button=self.ad_button['xpos']+self.ad_button['width']
		self.below_ad = self.ad['ypos']+self.ad['height']
		self.below_ad_button = self.ad_button['ypos']+self.ad_button['height']


class Cursor:
	xpos = 0
	ypos = 0
	position = [xpos,ypos]
	def __init__(self,xpos,ypos):#make size of cursor
		self.xpos = xpos
		self.ypos = ypos
	def move_cursor(self,input_xpos,input_ypos):#returns array of cursor's xpos and ypos
		self.xpos += input_xpos
		self.ypos += input_ypos
		self.position = [self.xpos,self.ypos]
		return self.position
	def cur_position(self):
		return self.position
	def deviate_cursor(self,upper):#add a bit of random/imperfect motion towards button
		x = random.randrange(0,upper)
		return float(x)/1000



class User(Browser,Cursor):#User uses both Browser and Cursor
	def __init__(self,time_limit):
		self.time_limit=time_limit
		self.in_button_x = False
		self.in_button_y = False
		self.in_button = False


	def eval_position(self,Browser,Cursor):#evaluate the position of cursor and return the suggested coordinates
		if 0 <= Cursor.xpos <= Browser.ad['xpos']:
			input_x = user_excitement+Cursor.deviate_cursor(4)
		elif Browser.ad['xpos'] <= Cursor.xpos <= Browser.ad_button['xpos']:
			input_x = (user_excitement/2)+Cursor.deviate_cursor(3)
		#if cursor is further over than it should be (to the right of the button and ad)
		elif Browser.right_of_ad <= Cursor.xpos <= Browser.width:
			input_x = (user_excitement+Cursor.deviate_cursor(2))*-1
		elif Browser.right_of_ad_button <= Cursor.xpos <= Browser.right_of_ad:
			input_x = (Cursor.deviate_cursor(2)+user_excitement)/-2
		#if cursor is within the ad_button keep it there
		elif Browser.ad_button['xpos'] <= Cursor.xpos <= Browser.ad_button['width']:
			input_x = Cursor.deviate_cursor(2)
		else:
			input_x= Cursor.deviate_cursor(2)
		#ypos
		if 0 <= Cursor.xpos <= Browser.ad['ypos']:
			input_y = user_excitement+Cursor.deviate_cursor(4)
		elif Browser.ad['ypos'] <= Cursor.ypos <= Browser.ad_button['ypos']:
			input_y = (user_excitement+Cursor.deviate_cursor(3))/2
		elif Browser.below_ad <= Cursor.ypos <= Browser.height:
			input_y=(user_excitement+Cursor.deviate_cursor(2))*-1
		elif Browser.below_ad_button <=  Cursor.ypos <= Browser.below_ad:
			input_y=(Cursor.deviate_cursor(2)+user_excitement)/-2
		#if cursor is within the ad_button keep it relatively close
		elif Browser.ad_button['ypos'] <= Cursor.ypos <= Browser.ad_button['height']:
			input_y = Cursor.deviate_cursor(2)
		else:
			input_y = Cursor.deviate_cursor(2)
		return [input_x,input_y]


	def log_cursor(self,Cursor):#this could go into an sql db
		a = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
		print str(Cursor.cur_position()) + " @ " + str(a)

	def build_log(self,Cursor):
		x = 0#iterator
		milli = .1#add per iteration
		while x < self.time_limit*10:
			threading.Timer(milli, self.log_cursor,(Cursor,)).start()
			milli+=.1
			x+=1
		
	

user_excitement = .0015#how quickly the user gets to the ad
web = Browser(1366,768)#width and height
#draw ad on in there
web.draw_ad(800,17,300,255)#xposition,yposition,width and height
web.draw_ad_button(web.ad)#place that
web.make_partition()#function for making variables and partitions a bit more legible
usr = User(15)#int passed is time limit in seconds
cur = Cursor(1,1)#cursor position
start_time = round(time.time()*10)#start the timer so program knows when to end
stop_time = start_time + (usr.time_limit*10)#x seconds from RIGHT NOW-- static var

usr.build_log(cur)#build and begin the threading log

while 1:
	cur_time = round(time.time()*10)
	if stop_time >= cur_time:
		to_move = usr.eval_position(web,cur)
		cur.move_cursor(to_move[0],to_move[1])
	else:
		sys.exit()

	