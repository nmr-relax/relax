#!/usr/bin/python
# PySamVi
#
# Copyright (C) 2002 Andrew J. Perry
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of version 2.1 of the GNU Lesser General Public
# License as published by the Free Software Foundation.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Date: 05-May-02
# Author: Andrew Perry
# Desc: Skeleton example code for PySamVi
#       Should become the vi of live sample performance - (not too) hard to learn, powerful to use.
#
# Dependancies: pygame-1.4, (and it's deps), PyUI-0.9
#
# Notes: PyUI Buttons are extended with .sound and .channel attributes, which contain their associated sounds.
#
# 'Mission goals [:)]':
# (a 'vi' for live samplists . . ie driven by tricky cryptic but powerful but keyboard commands [cf Delfin])
# ("to allow the PC to become respected as a live instrument [using linux of course .. ]")
#       
#       * make a simple phrase sampler (full screen UI) using pygame with keyboard commands
#  	* modulate samples based on key combinations (ie ctrl / shift / alt, or other multiple keypresses)
#  	* sync samples to the tempo (bar / beat / no-sync based on key combination)
#       * other key combos might modulate effects, panning, volume, global effects#         
#
# TODO:
#      pretty much everything at the moment . . .

#      NEED TO GET MODIFIER KEYS (ie MOD_CONTROL) WORKING

#      10-May-2002 - fixed problem in pyui.init() not returning its Desktop (gDesktop) object (as 'desktop' in my code below)
#                  - got key presses working by using desktop.registerHandler(KEYDOWN, onKeyDown)
#                    and made onKeyDown function which gets the key identity and acts on this info...
#      13-May-2002 - fixed pygame mixer.c channel volume problem (was setting vol to 0 when get_volume called)
#    
#      14-May-2002 - fixed GLOBAL_VOLUME - need to declare it as global inside functions so they
#                    can see the global variable, and don't just make a local version of the name
#                  - made a slider which fires off the last sample played as it moves. 
#                    . . good for 'machine gun' type rolls
#      26-May-2002 - implemented simple sequencer with (supposedly) constant timing (fps).
#                    this should become the basis of timing for quantising & looping samples
#                    and my become the 'tick' for a simple pattern sequencer (aka tracker . . .not the aim of this project but. . . )
#      01-June-02  - changed the sample_keys dictionary of key mappings->sounds to a
#                    dictionary of key mappings (character) -> action objects.
#                    action objects have a .sound which can be played, and a .do that can
#                    be tied to any function. (should actually set it up with only a .do,
#                    which can play the .sound as it's action if thats what you want. 
#                    That way every key press just maps to an action [which may or may not
#                    be a sound.play() or playSound(sound) event.] )
#                    SOMETHING IS BROKEN - KEY PRESSES NOT CAUGHT ANYMORE :(
#                    Fixed - seems KEYDOWN / KEYUP constants are stuffed up / changed ??
#
#                  - made Sequence and Pattern objects. NEED TO MAKE THESE WORK WITH THE
#                    TICK LOOPING 'mainloop' in loopTurn() now. . . .
#      early-June  - Fixed up Sequence & Pattern objects . . .complete rewrite of these
#                  - Sequence is now a mutable-sequence object (behaves like a list)
#                  - Pattern should be made this way eventually too
#      15-Jun-02   - Fixed up fullscreen display by changing the pyui.init(*opts) to have (1024, 768)
#                    using new global tuple RESOLUTION
#                  - Made a few cosmetic changes to the little app gui (this will be scraped and remade later NEway)
#      21-Jun-02   - Added a pulldown menu (mostly just stubs to fill out currently)
#                  - Added an Edit box (text) for typing in sequences (eg 5 6 7 4 9-* 5-# )
#      06-Jul-02   - Have hacked out the GUI for now and reverted back to pygame key handling 
#                    (trying to get better latency & more consistent timing)
#                  - Added repeat and quantize (unfinished) to the 'action' object, 
#                      - think i need to modify Sequence to cope with the needs of quantize better.
#                  - set up more key bindings (just slurps up a wav file directory and haphazardly assigns them to keys)
#                  - played around with timing of the main loop (loopTurn). It's looking like the timing will be very flaky. :(
#                  - added an example of external application launching (in this case RTcmix playing)
#
# Current TODO notes:
#                  - WORK TOWARD A TRACKER TYPE THING NOW.-CAN CODE THE 'LIVE-sequencing' on top of that once its working well
#                  - Try to figure out a way of handling:
#                     - playing mulptiple samples simultaneously (modification to Sequence)
#                     - disinguishing between the proper Sequence ('static' & editable), and events that just need to be
#                       quantized (dynamic, played live and expire after play)
#                  - Optimise the loopTurn() - make it faster.
#                  - Start making the triggerMods (ie delays) and work this into the action class
#                  - use chan.get_busy() where chan is the channel playing a sound returned by playSound
#                    to allow looping independant of tempo (or setting tempo to a loop length) ... will
#                    be useful for setting a drum loop as the base loop & forcing tempo to match this loop
#                    length automatically
#
#      * still need to get keyboard MODs working.. .. 
#      * graphic window of the keyboard ?
#      * currently using pygames autoassignment of channels. need to get fixed channels (one per sound) working 
#        - may actually make this optional - 1. samples can cut themselves (ie have one channel which they always play on) or 2. take new channels for each instance, so they can have multiple copies of the sample going simultaneously, or 3. be quantised so that the sample plays multiple times but waits for one instance to finish before another starts. . . there may be other interesting options also.
#      (using 'mode' 3. would allow for say 4 fast keypresses to set a 4 X loop of the sample)
#      * can easily implement a delay with initial vol and decay. . .
#      * a file-like (sine) wave generator ?
#      * a file selection box (contrib to PyUI. . ?)
#      * configure keyboard commands through a PyUI python console ?? can this be done ??
#      * PYGAME WILL TAKE FILE-LIKE OBJECTS as SOUNDFILE TO LOAD - EXPLOIT THIS TO DO SAMPLE MANIPULATION / SFX / SIMPLE LADSPA PLUGINS ??
#        - CAN WE LOOK IN THE PYGAME SOURCE AND SEE IF THERE IS A WAY OF FIDDLING THE LOADED SAMPLE ARRAYS DIRECTLY FROM PYTHON ?

__DEBUG__ = 0

import os, sys, time
import string
import pyui
#from pyui.locals import *

import pygame
from pygamehelper import *
from pygame.locals import *
from pytimer_mod import *

from pySamViConfig import *  # loads variables and does some startup stuff

# this may give a speed up if used correctly. . .
import psyco
from psyco.classes import *

##### Not sure why these needed to be changed. . #####
# just stopped working one day. . .(think constants in pyui.locals are diff to pygame.locals ?? )
#KEYDOWN = 8193
#KEYUP = 8194
######################################################


# list of sounds (actions) to be played on the bar . .
# has a position pointer 'pos' which is the current bar
# TODO: should eventually implement all the methods of a mutable sequence type -> * MOSTLY DONE NOW *
#       - implement setEndLoopPos (self.end_loop_pos) for end position looping. need to think about how this pointer moves
#         upon append / extend / insert / pop / remove / add .. etc .. operations
class Sequence:
	def __init__(self):
		self.pos = 0
		self.pats = []
		self.setStartLoopPos(0)
		self.looping = 1   	# 1 = sequence will loop around loop points (start_loop_pos, end_loop_pos) 
					# (when calling next()), 0 = will loop on last bar when it hits it
		
	#def __repr__(self):
	#	return str(self.pats)
	#def __str__(self):
	#	return str(self.pats)

	# adds a sequence.
	def append(self, p):
		self.pats.append(p)
	def insert(self, i, p):
        	self.pats.insert(i, p)
    	def pop(self, i = (-1)):
        	p = self.pats[i]
        	del self.pats[i]
        	return p
	def remove(self, item):
        	for i in range(len(self.pats)):
            		if self.pats[i] == item:
                		del self.pats[i]
                		return
        	raise ValueError, "Sequence.remove(x): x not in list"
	def count(self, item):
        	count = 0
        	for c in self.pats:
           		if c == item:
                		count = count + 1
        	return count
	
    	def index(self, item):
        	for i in range(len(self.pats)):
            		if self.pats[i] == item:
                		return i
        	raise ValueError, "Sequence.index(x): x not in list"
	
    	def reverse(self): self.pats.reverse()
	
	def extend(self, p):
        	if isinstance(p, Sequence):
            		for c in p.pats:
                		self.pats.append(c)
        	else:
            		for c in p:
                		self.pats.append(c)
		
	def __getitem__(self, i): return self.pats[i]
    	def __setitem__(self, i, item): self.pats[i] = item
    	def __delitem__(self, i): del self.pats[i]
    	def __getslice__(self, i, j):
        	i = max(i, 0); j = max(j, 0)
		n = self.__class__()
        	n.pats = self.pats[i:j]
		return n
    	def __setslice__(self, i, j, other):
        	i = max(i, 0); j = max(j, 0)
            	self.pats[i:j] = pts
	def __delslice__(self, i, j):
        	i = max(i, 0); j = max(j, 0)
        	del self.pats[i:j]
	
	# only seem to work with the long-winded n = . . . , return n type thing.
	def __add__(self, pts):
		n = self.__class__()
		n.pats = (self.pats + pts)
		return n
	def __radd__(self, pts):
		n = self.__class__()
		n.pats = (self.pats + pts)
		return n

	# return the pattern at pos
	def pat(self):
		try:
			#if __DEBUG__: print "Sequence.pat(): sequence index : "+`self.pos`
			return self.pats[self.pos]
		except IndexError:
			if __DEBUG__: print "Sequence.pat(): ERROR: Sequence pos > than number of patterns in Sequence !!"
			return Pattern(None,(0,))
		
	# add pattern(s) - current .pos used unless defined
	#def add_pat(self, p, pos=None):
	#	if pos == None:
	#		pos = self.pos
	#	try:
	#		self.pats[pos].extend(p)
	#	except:
	#		self.pats[pos] = p
	
	# return the actual sequence length
	def len(self):
		return len(self.pats)

	def __len__(self):
		return len(self.pats)
	
	def setStartLoopPos(self, ps):
		
		# special case used during __init__
		if ps == 0:
			self.start_loop_pos = 0
			return 0
		
		if ps >= 0 and ps <= (len(self) - 1):
			self.start_loop_pos = ps
			return ps
		else:
			if __DEBUG__: print "Sequence.setStartLoopPos(ps): ps not within range of pats - max index: ", len(self)
			sys.exit()
			#return None
		
	def getStartLoopPos(self):
		return self.start_loop_pos
	
	# set pos to the start_loop_pos.
	def gotoStartLoopPos(self):
		self.pos = self.start_loop_pos
		if __DEBUG__: print "gotoStartLoopPos(): ", (self.pos), (len(self) - 1), self.start_loop_pos
		
	# move pos one bar forward if there is a place in pats to move forward to
	# if looping is on, loop back to the position of the first loop position (default bar 0)
	# return the pattern at the current position
	# TODO: handle end looping with self.end_loop_pos
	def next(self):
		self.pos = self.pos + 1
		if __DEBUG__: print "next(): increment", (self.pos), (len(self) - 1)
		if (self.pos) > (len(self) - 1):
			if self.looping:
				if __DEBUG__: print "next(): -> gotoStartLoopPos()", (self.pos), (len(self) - 1), self.start_loop_pos
				self.gotoStartLoopPos()
			else:
				if __DEBUG__: print "next(): looping off: staying at current pos"
				self.pos = self.pos - 1  # go back to last bar
		return self.pat()

# a list of 'action lists'
# time resolution = 64ths. each index contains actions to be executed
# at that 64th.
# unlike a Sequence, a Pattern is 'stateless' with respect to it's current position
# ie. no pos variable
# TODO: should eventually implement all the methods of a mutable sequence type
# eg. for a pattern p of quarternotes of the action s
#     p = Pattern(s, (0, 15, 31, 47))
class Pattern:
	def __init__(self, action, notes):
		self.beat = []
		self._patlen = 64   # internal constant - number of beats in pattern
		
		if __DEBUG__: print "Will add to :" + `notes`
		for b in range(0, self._patlen):
			if b in notes:
				if __DEBUG__: print "Adding action to pattern beat " + `b`
				self.beat.append(action)
			else:
				self.beat.append(None)
	
	# return the actual patten length
	def __len__(self):
		return len(self.beat)

# return a pattern of a particular action (sound) 's' repeated 'q' number of times,
# as evenly spaced across the pattern as pos (ie 'q = 4' means 4 quater notes)
def makePattern(s, q):
	spacing = int(64.0 / q)
	beats = []
	for j in range(0, 65, spacing):
		beats.append(j)
	beats = tuple(beats)
	return Pattern(s, beats)

########
# Sequence and pattern usage/debuging example:
#sa = Sequence()
#print sa, len(sa)
#print
#sa.append(Pattern(KEY_BINDINGS['1'], (0, 15, 31, 47)))
#print sa.pats, len(sa.pats)
#print "sa", sa, len(sa)
#print
#sb = Sequence()
#sb.append(Pattern(KEY_BINDINGS['1'], (0, 15, 31, 47)))
#print sb.pats, len(sb.pats)
#print "sb", sb, len(sb)
#print "sa", sa, len(sa)
#sc = sa + sb
#print sc, len(sc)
#sc.append(Pattern(KEY_BINDINGS['3'], (0, 15, 31, 47)))
#print sc, len(sc)
#print len(sc[0:2])
#########

# the global sequence
gSequence = Sequence()

### add one pattern for testing ###
#gSequence.append(Pattern(KEY_BINDINGS['5'], (0, 15, 31, 47)))
#gSequence.append(Pattern(KEY_BINDINGS['q'], (0,15,47)))
#print gSequence.pats[0].beat
#a = Pattern(action("004.wav"), 0)
#print "pat a", a.beat
#gSequence.append(a)
#gSequence.append(Pattern(action("007.wav"), (0,)))
#print gSequence.pats[1].beat
#print len(gSequence)
#print gSequence.pats

#CurrentPattern = Pattern(None, (0,))

#####Pattern class debuging/examples#########
#p = Pattern(action("005.wav"), 0, 15, 31, 47)
#print p.beat, len(p)
#################

global LAST_PLAYED
global LAST_PRESSED
LAST_PLAYED = None
LAST_PRESSED = None

#samplename = "001.wav"
#test_sound = load_sound(samplename)
#test_channel = pygame.mixer.Channel(0)
#test_channel = pygame.mixer.find_channel()
#test_channel.set_volume(1.0)
#print "Channel volume: ", `test_channel.get_volume()`

#########some functions########
# currently takes a sound object and plays it


# play the sound or do it's action
def playSound(s):
    if s:
	# action.do instead of play sound if there is one
	if s.do:
		return s.do()

    	global LAST_PLAYED
    	global GLOBAL_VOLUME
    	s.sound.set_volume(GLOBAL_VOLUME)
	
    	#if __DEBUG__: print "Global volume set to " + `GLOBAL_VOLUME`
    	#if __DEBUG__: print "Sound volume: " + `s.sound.get_volume()`
	chan = s.sound.play()
	LAST_PLAYED = s
    	return chan
    else:
	return None

def playSoundNoLoop(s):
    global GLOBAL_VOLUME
    s.sound.set_volume(GLOBAL_VOLUME)
    if __DEBUG__: print "Global volume set to " + `GLOBAL_VOLUME`
    if __DEBUG__: print "Sound volume: " + `s.sound.get_volume()`
    chan = s.sound.play()
    return chan

# takes an action object which has .loops attribute defined
# adds that many loops to +1 the current pos (bar) in the gSequence
#def queueSoundLoop(s):
#    global LAST_PLAYED
#    global GLOBAL_VOLUME
#    global gSequence
#    s.increment = s.loops
#    # MAKE THE PATTERN HERE
#    # quarternotes
#    #p = Pattern(s, (0, 16, 32, 64))
#    # whole note
#    p = Pattern(s, (0,))  #one hit per bar
#    for L in range(0, s.loops):
#        gSequence.insert( (gSequence.pos + L + 1), p)
#    #LAST_PLAYED = s.sound
#    #s.sound.set_volume(GLOBAL_VOLUME)
#    #if __DEBUG__: print "Global volume set to " + `GLOBAL_VOLUME`
#    #if __DEBUG__: print "Sound volume: " + `s.sound.get_volume()`
#    #chan = s.sound.play(s.loops)
#    #return chan

def reReadConfig():
    import pySamViConfig
    return
###########################

###############

# a dictionary of key constants : action objects
sample_keys = KEY_BINDINGS

############ the GUI #################
class app:
    def __init__(self):

        # create gui objects
        print "Initializing"
        self.grid = pyui.widgets.Frame(0, 20, 1000, 500, "control")
        self.grid.setLayout( pyui.layouts.GridLayoutManager(1, 7) )
        #self.grid.setBackImage("max.bmp")
        print self.grid
        
	self.b3 = pyui.widgets.Button("test", self.onButton)
	#self.b3.sound = sample_keys[K_1].sound
	#self.b3.channel = test_channel

	#self.console = pyui.dialogs.Console(30,300,500,300)
	
	self.s = pyui.widgets.SliderBar(self.onSlide, 100, (GLOBAL_VOLUME*100))
        self.sliderplayer = pyui.widgets.SliderBar(self.samplePlaySlider, 100, 100)
	self.bpmslider = pyui.widgets.SliderBar(self.bpmSlide, MAX_BPM, BPM)
	self.bpmslider.stepInterval = 0.1 
	
	self.edit = pyui.widgets.Edit("", 80, self.onEdit)
	
	self.grid.addChild(self.b3)
        self.grid.addChild(self.s)
	self.grid.addChild(self.sliderplayer)
        self.grid.addChild(self.bpmslider)
	self.grid.addChild(self.edit)
	self.grid.pack()
	
	menu1 = pyui.widgets.Menu("File")
        menu1.addItem("Load", self.onMenu)
        menu1.addItem("Save", self.onMenu)
        menu1.addItem("Exit", self.onMenu)
        
	menu2 = pyui.widgets.Menu("Help")
        menu2.addItem("About...", self.onMenu)
	
	self.menubar = pyui.widgets.MenuBar()
	self.menubar.addMenu(menu1)
	self.menubar.addMenu(menu2)

    # Parses contents of the text box and appends at appropiate patterns to the
    # global sequence (gSequence). Simple shorthand syntax for the way patterns are filled....
    # first number is the key. after the dash is the pattern filling shorthand for that key
    # eg 5 6 7 4 9-* 5-# 1-(0,15,47)
    def onEdit(self, item):
	    if __DEBUG__: print item.text
	    tokens = string.split(item.text)
	    for s in tokens:
	        p = string.split(s, '-')
		if len(p) > 1:
			if p[1] == "!":
				beats = (0,)
			if p[1] == "@":
				beats = (0, 31)
			if p[1] == "#":
				beats = (0, 15, 31, 47)
			if p[1] == "*":
				beats = []
				for j in range(0, 64):
					beats.append(j)
				beats = tuple(beats)
			if p[1][0] == "(":
				# split up the numbers seperated by commas between brackets
				# if the user make typos (too many ()()( then too bad it will
				# behave strangely
				# eg "(0,14,56)" -> the tuple (0, 14, 56) 
				pp = string.split(p[1][1: (len(p[1]) - 1) ], ',')
				# convert from single char strings to ints
				for n in range(0, len(pp)):
					pp[n] = int(pp[n])
				beats = tuple(pp)
				print beats
		else:
			beats = (0,)
		print p, beats
		if KEY_BINDINGS.has_key(p[0]):
            	    gSequence.append(Pattern(KEY_BINDINGS[p[0]], beats))
		else:
			return None
	    return len(tokens)

    def onMenu(self, item):
	    if __DEBUG__: print "Menu: " + item.text
	    if item.text == "Exit":
		    self.cleanupAndExit()
	    if item.text == "About...":
		    aboutBox = pyui.dialogs.StdDialog("About PINAS", "PINAS - By < ajperry@alphalink.com.au >")
		    self.aboutBox.alpha = 100
		    self.aboutBox.doModal()

    def samplePlaySlider(self, pos):
	try:
	    global LAST_PLAYED
	    playSound(LAST_PLAYED)
	except:
            pass

    def onSlide(self, pos):
	global GLOBAL_VOLUME
        GLOBAL_VOLUME = (pos / 100.0)
	if __DEBUG__: print "Global volume set to " + `GLOBAL_VOLUME`
	return GLOBAL_VOLUME

    def bpmSlide(self, pos):
	global BPM
	global tick_interval
	global beat_interval
	# so we never get 0 BPM . . . 
	if pos < 1:
		pos = 1
	BPM = pos
	if __DEBUG__: print "BPM set to " + `BPM`
	beat_interval = bpm2ms(BPM)
	tick_interval = (beat_interval / 64.0)
	return BPM

    def onButton(self, button):
        
	#simple old way with pygames channel managment
	#chan = playSound(button.sound)
	
	#new way Channel.play(Sound, [loops, [maxtime]])
	#print "Playing " + samplename
	#print `pygame.mixer.get_busy()` + " channels currently playing"
	#print "This channels state is " + `button.channel.get_busy()`
	#button.channel.play(button.sound)
	#chan = button.channel
	
	#return chan
	pass
	
    def cleanup(self):
        self.b3 = None
        self.grid.destroy()
        self.grid = None
	
    def cleanupAndExit(self, *partingmessage):
	self.cleanup()
	pyui.quit()
	if partingmessage: print partingmessage
	sys.exit()

#now unused ...
"""
def scan_keyboard():
	for event in pygame.event.get():
            #print event
	    if event.type is QUIT:
                return
	    for k in sample_keys.keys():
		# play sound on keypress
	        if event.type is KEYDOWN and event.key is k:
		    print "Re-reading config..."
                    reReadConfig()
		    print "Key " + `k` + " pressed. Playing " + `sample_keys[k]`
                    chan = playSound(sample_keys[k])

	    if event.type is KEYDOWN and event.key is K_r:
		print "Re-reading config..."
                reReadConfig()
		
	pyui.draw()
        pyui.update()
"""

def onKeyDown(event):
    
    #### temp for testing. . . ###3	
    #print "PRESSED " + `chr(event.key)`
    ##################################

    global LAST_PLAYED
    global LAST_PRESSED
    global g
    global gSequence
    global TickPos
    
    mods = pygame.key.get_mods()
    
    for k in sample_keys.keys():
	# play sound on keypress
	if event.key == k:
	    action = sample_keys[k]
	    # if there is an action.do, do that in pref to playing the sound - NOW HANDLED IN playSound()
	    #if action.do:
		    #if __DEBUG__: print "Key " + `k` + " pressed. Doing action " + `action.do`
                #action.do(action)
	    #else:
	    if __DEBUG__: print "Key " + `k` + " pressed. Playing " + `action.soundfilename`
            
	    # if there is a repeat defined, queue the appropriate pattern.
	    # else play the sound NOW!
	    if action.quantize:
		    ######### NOT FINISHED##########
		    ## need to find the next appropriate beat at
		    ## TickPos + (64 / action.quantize)
		    ## & 'warp' to next gSequence.pos if its > 64
		    ###############################
		    pass
		    #gSequence[gSequence.pos].beat = action
		    
	    if action.repeat:
		for b in range(action.repeat[0]):
			gSequence.append(makePattern(action, action.repeat[1]))
	        if action.repeat[2]:
	    	        playSound(action)
	    else:
		    playSound(action)

	    LAST_PRESSED = action
	    #gSequence.append(Pattern(LAST_PLAYED, 0))
	
	# can't get modifiers going !! :(
	#if event.key == K_CONTROL:
	#    print "Key CTRL-" + `k` + " pressed. Playing looped " + `sample_keys[k]`
	#    print `event.key`,`k`,`MOD_CONTROL`,`(k & MOD_CONTROL)`
        #    queueSoundLoop(action)
	#print event.key, event.mods
	if event.key == K_r:
		print "Re-reading config..."
                reReadConfig()
		return
	if event.key == K_d:
		print "Deleting bar " + `gSequence.pos`
                gSequence.next()
		gSequence.remove(gSequence[gSequence.pos - 1])
		return

	if event.key == K_ESCAPE:
		sys.exit()

	if mods == KMOD_CTRL:
		print "CONTROL-" + chr(event.key)
    #return

def onKeyUp(event):
     print "KEYUP"

# this is where the main timing loop turns, the sequence is executed
# and the GUI is updated
# 'live playing' key handling is done by the desktop object on pyui.update() calls (i think)
def loopTurn():
    global tick_time
    global t
    global desktop
    global TickPos
    global gSequence
    global LAST_PLAYED
    global LAST_PRESSED	    
    global loopsturned
    global avg_loopturn_time
    global cum_loopturn_time

    for event in pygame.event.get():
	if event.type is QUIT:
            g.cleanup()
            pyui.quit()
	    sys.exit()
	elif event.type is KEYDOWN:
	    onKeyDown(event)

    frame_dur = timer.get_frame_duration()
    tick_time += frame_dur
    
    loopsturned = loopsturned + 1
    cum_loopturn_time += frame_dur
    avg_loopturn_time = cum_loopturn_time / loopsturned
    #print frame_dur, avg_loopturn_time

    #tick_time += avg_loopturn_time

    if tick_time >= tick_interval:
	 #print tick_interval, tick_time
         tick_time = 0
	 TickPos = TickPos + 1
	 if TickPos > 63:
		TickPos = 0
		
		######## nasty testing stuff #####
		#if LAST_PRESSED: gSequence.append(Pattern(LAST_PRESSED,  (0, 15, 31, 47)))
		#if LAST_PRESSED: gSequence.append(Pattern(LAST_PRESSED,  (0,)))

		#################################
		
		gSequence.next()
		  
	 if  gSequence.pos == None: print "ERROR: Sequence.pos returned None !!" #sys.exit()
	 #print "Bar: "+ `gSequence.pos`
	 #print "pat:", gSequence.pat()
	 #print "beat:", gSequence.pat().beat[TickPos]
	 #print "TickPos:", TickPos
	 #print
	 playSound(gSequence.pat().beat[TickPos])
	 #print "tick " + `TickPos`
	 
    timer.tick()
    #pyui.update()
    #pyui.draw()

# may help speed up ?
psyco.bind(loopTurn)

import testopt
opts = testopt.parseCommandLine(RESOLUTION[0], RESOLUTION[1], FULLSCREEN)
print "Pyui init options: ", opts
pygame.init()

if FULLSCREEN: 
	winstyle = int(FULLSCREEN)  # |FULLSCREEN
else:
	winstyle = 0
bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

if FULLSCREEN: pygame.display.toggle_fullscreen()

# set key repeat rate
pygame.key.set_repeat(1, 10)  # delay, interval

#desktop = pyui.init(*opts)
#g = app()

#desktop.registerHandler(KEYDOWN, onKeyDown)
#desktop.registerHandler(KEYUP, onKeyUp)
timer = FpsClock()

# number of milliseconds (ms) per quarter beat
beat_interval = bpm2ms(BPM)
print "beat_interval: ", beat_interval

# number of milliseconds (ms) per 64th beat
tick_interval = (beat_interval / 64.0)
print "tick_interval: ", tick_interval

# accumulated time (ms) for the current beat
tick_time = 0

# some timing testing
loopsturned = 0
avg_loopturn_time = 0 
cum_loopturn_time = 0.0

# current Bar in the Sequence
#Bar = 0

# the current 64th in the Pattern
TickPos = 0

timer.begin()
#pyui.run(callback=loopTurn)
#pyui.run(callback=None)
while 1:
	loopTurn()

print "done X"
g.cleanup()
pyui.quit()
print "quit."
