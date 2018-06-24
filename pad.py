# Back end data structures and functions,
# separated out to here just for modularity

import time, datetime, sys
import subprocess
import tempfile

# Parameter
thumbSize =  70

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

	# Return a deep copy
	def copy (self):
		return StatePoint (self.data)

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
		else: self.thumb = "dummy.gif"

		# Brain/body state measurement to be associated with this bookmark
		# need a deep copy, otherwise all the bookmarks point to same currentState object
		self.statePoint = currentState.copy()

		# An optional feature, you can ignore it.
		# Could hold 1 scalar of other brain or body state info,
		# for gradient bookmark retrieval
		self.interest = 0

		# We set this one ourselves upon creation
		self.time = datetime.datetime.today()

	# Squared distance to currentState, calculated on the fly
	def distCS (self):
		return self.statePoint.dist(currentState)

############################################################
# COMMUNICATE WITH BROWSER
############################################################

# Collects data for making a bookmark
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
	temppngfilename = tempfile.mkstemp(prefix="proj.brain.proto.pad", suffix=".png")[1]
	tempgiffilename = tempfile.mkstemp(prefix="proj.brain.proto.pad", suffix=".gif")[1]
	err = callShell ("screencapture -l" + windowid + " " + temppngfilename)
	if err!="": print ("Error from screencapture: " + err, file=sys.stderr)
	callShell ("sips " + temppngfilename + " -Z " + str(thumbSize) + " -s format gif --out " + tempgiffilename)

	# Create a new Bookmark and return it
	return Bookmark (url, title, tempgiffilename, selection)

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
# OUR GLOBALS AND INITIALIZATIONS
############################################################

# Latest measurement, i.e., what we would act upon for Save or View
currentState = StatePoint ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

# The main list
allBookmarks = []

# Some miscellaneous initialization to start us up
allBookmarks.append (Bookmark ("http://www.tufts.edu/", "Tufts University", None, None))
currentState = StatePoint ([.8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
allBookmarks.append (Bookmark ("http://www.cs.tufts.edu/~jacob/", "Rob Jacob Home Page", None, None))
currentState = StatePoint ([.4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
allBookmarks.append (Bookmark ("http://www.tufts.edu/home/visiting_directions/", "Visiting, Maps & Directions - Tufts University", None, None))
currentState = StatePoint ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
