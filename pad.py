#!/usr/bin/env python3

import time, datetime, sys, random
import subprocess
import tempfile
import threading
import tkinter   

import ui, brainclient

############################################################
# BOOKMARK AND RELATED CLASSES
############################################################

# Object to hold a single brain/body state reading
# (a point in the feature space), holds raw features, no classifier.
# Sort of assume each feature is 0..1
class StatePoint:
	# Arg is an array of numbers
	def __init__ (self, args):
		self.data = args[0:] # To get kind of a deep copy

	# Square of Euclidean distance to point p
	def dist (self, p):
		return sum (map (lambda x, y: (x-y) * (x-y), self.data, p.data))

class Bookmark:
	def __init__ (self, url, title, thumb=None, selection=None):
		self.url = url
		self.title = title

		# Specific selection if applicable (vice just save URL)
		# text or None
		self.selection = selection

		# Filename (temporary file) of thumbnail
		# or placeholder dummy file
		if thumb: self.thumb = thumb
		else: self.thumb = "dummy.png"

		# Brain/body state measurement to be associated with this bookmark
		self.statePoint = currentState;

		# An optional feature, you can ignore it.
		# Holds 1 scalar of other brain or body state info,
		# for gradient bookmark retrieval
		self.interest = currentInterest;

		# We set this one ourselves
		self.time = datetime.datetime.today()

	# Squared distance to currentState, calculated on the fly
	def distCS (self):
		return self.statePoint.dist(currentState)

############################################################
# COMMUNICATE WITH BROWSER
############################################################

# Collects data for making a bookmark and adds the new bookmark
# This is Mac OS-specific, if using another OS, write an equivalent function.
def getBookmark ():
	# Fetch URL from applescript
	# these assume there's only one Safari window
	url = callApplescript ('tell application "Safari" to do JavaScript "window.document.URL" in item 1 of (get every document)')

	# Fetch page "name" from applescript
	title = callApplescript ('tell application "Safari" to do JavaScript "window.document.title" in item 1 of (get every document)')

	# Fetch clipboard selection if any
	selection = callShell ("pbpaste -Prefer txt ; pbcopy </dev/null")
	if selection == "": selection = None

	# Fetch thumbnail (screendump the window, save to file, scale image, save file name to pass to front end)
	windowid = callApplescript ('tell application "Safari" to get id of item 1 of (get every window)')
	tempfilename = tempfile.mkstemp(prefix="proj.brain.proto.pad.", suffix=".png")[1]
	err = callShell ("screencapture -l" + windowid + " " + tempfilename)
	if err!="": print ("Error from screencapture: " + err, file=sys.stderr)
	callShell ("sips " + tempfilename + " -Z 70")

	# Save the bookmark
	allBookmarks.append (Bookmark (url, title, tempfilename, selection))

# Send a URL (given as arg) to our main browser window
# This is Mac OS-specific, if using another OS, write an equivalent function.
def sendBookmark (url):
	callApplescript ('tell application "Safari" to do JavaScript "window.location.href = ' + "'" + url + "'" + '"in item 1 of (get every document)')

# Utility function, arg = the script as text
# Should be no need to escape double quotes or other shell metacharacters
# We return stdout, converted to a python3 text string if nec.
def callApplescript (script):
	ans = subprocess.check_output (["osascript", "-e", script])
	ans = ans.strip()
	if type(ans)!=type(""): return ans.decode("utf-8", "ignore")
	else: return ans

# Ditto, for shell script
def callShell (script):
	ans = subprocess.check_output (script, shell=True)
	ans = ans.strip()
	if type(ans)!=type(""): return ans.decode("utf-8", "ignore")
	else: return ans

############################################################
# COMMUNICATE WITH BRAIN DEVICE
############################################################

### TRY IT ONCE: could do it wihtout timer, just viewCB() every reading below
###	expect too jarring


# Call from brainclient, arg = line of text from matlab
# This is coming from a separate thread,
# both threads access currentBrainState and currentInterest
# we set them, others just read them (except the GUI slider)
# and it's a single atomic setting of a variable,
# so synchronization issues should be ok
def brainCB (line):
	global currentState
	global currentInterest

	tokens = line.strip().split (",")
	if len(tokens) < 1:
		print ("brainCB: can't parse input line: " + line, file=sys.stderr)

	else:
		print (tokens) ### is this stuff working ok, still need print stmts?
		currentState = StatePoint (list (map (float, tokens)))

		# Optional: display it back to user via the sliders
		print (currentState.data) ###
		for i in range (len (currentState.data)):
			print (currentState.data[i]) ###
			ui.brainSliders[i].set (currentState.data[i] * 100)

		# Placeholder, intend to be getting this from physio or other sensor
		currentInterest = random.random()
		
# When a brainSlider is changed
# NB our sliders run 0..100 but data from brainClient assumed to run 0..1
def brainSliderCB (ignorearg):
	for i in range (len (currentState.data)):
		currentState.data[i] = ui.brainSliders[i].get()/100.0

############################################################
# UI COMMAND CALLBACKS
############################################################

#
# Save button callback: Save current page in allBookmarks
#
def saveCB ():
	pass
# 		doXML ("getbookmark", function (responseText) {
# 			// Parse the returned data
# 			var url = responseText.split("\n")[0]
# 			var title = responseText.split("\n")[1]
# 			var tempfilename = responseText.split("\n")[2]
# 			var selection = responseText.split("\n").slice(3).reduce (function (a,b) { return a + "\n" + b; }, "").slice (0, 200)
# 			if (selection.trim() == "") selection = null;

# 			// Save a bookmark (using current state)
# 			allBookmarks.push (new Bookmark (url, title, tempfilename, selection))

# 			// Optional: Update bookmarks display
# 			viewCB();
# 		})
# 	})


#
# View button callback: displays all bookmarks, sorted by distance to current state
# also used in some other places
# 
### improve on this rather awkward passing of sendBookmark
def viewCB ():
	# Sort by distance, into new temporary list, then tell UI to do it
	ui.showBookmarks (sorted (allBookmarks, key=lambda b: b.distCS()), sendBookmark)

#
# Checkbox callback: Toggle continuous (ie on timer) view refresh
#
### checkbox checked
### 	other uses for Var()?
### 	probably not:
### 		c= tkinter.ttk.Checkbutton (parent, text=""")
### 		c.instate(['selected'])  # returns True if the box is checked
def continuousCB ():
# 	if (checkbox.checked) { ###
		continuous = True
		tick()
		ui.viewButton["state"] = tkinter.DISABLED
# 	else:
# 		continuous = False
#		ui.viewButton["state"] = tkinter.NORMAL

# Set up for continuous
# Alternative = no timer, just call ViewCB() from brainCB and brainSliderCB
# but could be annoying because very frequent
continuous = False
def tick ():
	if continuous:
		viewCB()
		top.after(500, tick)

# Install these as callbacks
ui.saveButton["command"] = saveCB
ui.viewButton["command"] = viewCB
ui.continuousBox["command"] = continuousCB
for s in ui.brainSliders: s["command"] = brainSliderCB

############################################################
# GLOBALS AND INITIALIZATION
############################################################
		
# Latest measurement, i.e., what we would act upon
currentState = StatePoint ([0, 0, 0, 0, 0])

# Ditto, but just a placeholder for now
currentInterest = 0.5

# The main list
allBookmarks = []

# Some miscellaneous initialization to start us up
allBookmarks.append (Bookmark ("http://www.tufts.edu/", "Tufts University", None, None))
currentState = StatePoint ([.8, 0, 0, 0, 0])
allBookmarks.append (Bookmark ("http://www.cs.tufts.edu/~jacob/", "Rob Jacob Home Page", None, None))
currentState = StatePoint ([.4, 0, 0, 0, 0])
allBookmarks.append (Bookmark ("http://www.tufts.edu/home/visiting_directions/", "Visiting, Maps & Directions - Tufts University", None, None))
currentState = StatePoint ([0, 0, 0, 0, 0])

############################################################
# MAIN LOOP
############################################################

# Start up brainclient
bclientThread = threading.Thread (target=brainclient.mainloop, args=[brainCB])
bclientThread.start()

# Start this one off
viewCB()

# Run our GUI loop
ui.top.mainloop()

# Also quit brainclient cleanly, when our window closes
brainclient.quit = True
