#!/usr/bin/env python

# browser simulation of user interacting with 300x255px ad on this page: http://www.moat.com/search/results?q=Google&ad=499142
import time, sched, math, sys, threading
from datetime import datetime, date
global user_excitement #for how eager the individual is to get to the button

class Browser:
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
	def __init__(self,width,height):
		self.width = width
		self.height = height
	def move_cursor(self,input_xpos,input_ypos):#returns array of cursor's xpos and ypos
		self.xpos += input_xpos
		self.ypos += input_ypos
		self.position = [self.xpos,self.ypos]
		#print str(self.position) + " current position"
		return self.position
	def cur_position(self):
		return self.position

class User(Browser,Cursor):#User uses both Browser and Cursor
	def __init__(self,time_limit):
		self.time_limit=time_limit
		self.s = sched.scheduler(time.time, time.sleep)
		self.in_button_x = False
		self.in_button_y = False
		self.in_button = False


	def eval_position(self,Browser,Cursor):#evaluate the position of cursor. each iteration should bring the cursor closer to the button
		if 0 <= Cursor.xpos <= Browser.ad['xpos']:
			input_x = user_excitement
		elif Browser.ad['xpos'] <= Cursor.xpos <= Browser.ad_button['xpos']:
			input_x = user_excitement/2
		#if cursor is further over than it should be (to the right of the button and ad)
		elif Browser.right_of_ad <= Cursor.xpos <= Browser.width:
			input_x = user_excitement*-1
		elif Browser.right_of_ad_button <= Cursor.xpos <= Browser.right_of_ad:
			input_x = user_excitement/-2
		#if cursor is within the ad_button keep it there
		elif Browser.ad_button['xpos'] <= Cursor.xpos <= Browser.ad_button['width']:
			input_x = 0
			self.in_button_x = True
		else:
			input_x=0
		#ypos
		if 0 <= Cursor.xpos <= Browser.ad['ypos']:
			input_y = user_excitement
		elif Browser.ad['ypos'] <= Cursor.ypos <= Browser.ad_button['ypos']:
			input_y = user_excitement/2
		elif Browser.below_ad <= Cursor.ypos <= Browser.height:
			input_y=user_excitement*-1
		elif Browser.below_ad_button <=  Cursor.ypos <= Browser.below_ad:
			input_y=user_excitement/-2
		#if cursor is within the ad_button keep it
		elif Browser.ad_button['ypos'] <= Cursor.ypos <= Browser.ad_button['height']:
			input_y = 0
			self.in_button_y = True
		else:
			input_y =0
		#print "input x suggestion: " + str(input_x) + " input y sug: " + str(input_y)
		return [input_x,input_y]


	def log_cursor(self,Cursor):#this could go into an sql database or something
		a = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
		print str(Cursor.cur_position()) + " @ " + str(a)

	def build_log(self,Cursor):
		#build the schedule up to fire the log function every 100 miliseconds. 
		#amt is the amount of seconds you want to run fo
		x=0
		i=.1
		# self.s.enter(0,1,self.eval_position,(Browser,Cursor,))
		while x<self.time_limit*10:#ten miliseconds in 1 second.
			self.s.enter(i, 8, self.log_cursor, (Cursor,))
			i+=.1
			x+=1
		# self.eval_position(Browser,Cursor)#evaluate position and move cursor accordingly
		return self.s
		
		
	

user_excitement = .0005
web = Browser(1366,768)
#draw ad on in there
web.draw_ad(800,17,300,255)
web.draw_ad_button(web.ad)
web.make_partition()
usr = User(2)
cur = Cursor(1,1)
schedule  = usr.build_log(cur)

milli_time = round(time.time()*10)

while 1:
	cur_time = round(time.time()*10)
	schedule.run()
	if milli_time+150 >= cur_time:
		# new_time = round(time.time()*10)
		# if new_time >= cur_time+1:
			# print usr.log_cursor(cur)
		to_move = usr.eval_position(web,cur)
		cur.move_cursor(to_move[0],to_move[1])
		# print " new time  " + str(new_time) + "compared to old time:" + str(cur_time+1)
	else:
		print cur_time
		sys.exit()

	