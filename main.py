#!/usr/bin/env python3
# Main program, including UI and callbacks

import random
import threading
import tkinter   

import pad
import brainclient

############################################################
# SEMANTIC CALLBACKS
############################################################

#
# Save button callback: Save current page in allBookmarks
#
def saveCB ():
	pad.allBookmarks.append (pad.getBookmark())

	# Update bookmarks display (optional)
	viewCB()

#
# View button callback: displays all bookmarks, sorted by distance to current state
# is also used in some other places
# 
def viewCB ():
	# Sort by distance, into new temporary list
	bookmarks = sorted (pad.allBookmarks, key=lambda b: b.distCS())

	# Save max distance^2 for graphic display
	maxDist = bookmarks[-1].distCS()
# 		// Shading based on distance squared,
# 		// want "decrement" from pure white when you hit maxDist
# 		var decrement = 0.2		
# 		var brightness = Math.floor (255 * (1 - b.distCS() * (decrement / maxDist)))
# 		bhtml.getElementsByClassName("bookmarkBackground")[0].style.backgroundColor =
# 			"rgb(" + brightness + "," + brightness + "," + brightness + ")"

# 		// Make the bar graph
# 		var rect = bhtml.getElementsByClassName("bar")[0]
# 		rect.y.baseVal.value = 60*(1.-b.interest); // This "60" also appears in front.html
# 		rect.height.baseVal.value = 60*b.interest;

	# Plug the bookmarks into the bookmark widgets
	ndraw = min (len(bookmarks), len(bookmarkWidgets))

	for i in range (ndraw):
		bookmarkWidgets[i].showBookmark (bookmarks[i])

	# Make the rest of them, if any, invisible
	for i in range (ndraw, len(bookmarkWidgets)):
		bookmarkWidgets[i].hideBookmark()

#
# Observer callback, ie when value changes: Toggle continuous view refresh.
# Actually simply setting continousVar itself is what does the job,
# we just disable/enable the view button here
#
def continuousVarCB (*ignoreargs):
	if continuousVar.get()==1:
		viewButton["state"] = tkinter.DISABLED
	else:
		viewButton["state"] = tkinter.NORMAL

############################################################
# OTHER UI-RELATED FUNCTIONS
############################################################

###/// layout: some padding or margin??

###/// ALSO CAN USE
###/// height in lines (else fits to contents)
###/// width (chars not pixels)
###/// wraplength (chars) default = break only at newlines

# An initially blank widget that can show data for a bookmark,
# can be changed subsequently to show a different bookmark.
# Doing it this way, rather than deleting the widgets and making new ones,
# seems to avoid flashing in the UI
class BookmarkW:
	# Make the blank widget
	def __init__ (self, bookmarksPanel):
		self.bookmark = None
		
		self.main = tkinter.Frame (bookmarksPanel, borderwidth=1, background="grey")
		self.main.pack (side="top", fill="both", expand=True)

		self.urlw = tkinter.Label (self.main, font=('', '10', ''))
		self.urlw.pack (side="top", fill="both", expand=True)

		self.titlew = tkinter.Label (self.main, font=('', '12', 'bold'))
		self.titlew.pack (side="top", fill="both", expand=True)

		self.selectionw = tkinter.Label (self.main)
		self.selectionw.pack (side="top", fill="both", expand=True)

		self.thumbw = tkinter.Label (self.main)
		self.thumbw.pack (side="top", fill="both", expand=True)

		self.timew = tkinter.Label (self.main)
		self.timew.pack (side="top", fill="both", expand=True)

		self.distw = tkinter.Label (self.main)
		self.distw.pack (side="top", fill="both", expand=True)

		# Attach our callback to our widget and everything inside
		self.main.bind ("<Button-1>", self.callback)
		for child in self.main.children.values():
			child.bind ("<Button-1>", self.callback)

		# Hide ourself until someone uses us
		self.main.pack_forget()

	# Populate this widget with data from the given bookmark
	def showBookmark (self, bookmark):
		self.bookmark = bookmark

		self.urlw["text"] = self.bookmark.url
		self.titlew["text"] = self.bookmark.title
		self.selectionw["text"] = self.bookmark.selection
		###///	image = tkinter.PhotoImage (file=bookmark.thumb)
		###///	self.thumb["image"] = image
		self.thumbw["text"] = bookmark.thumb
		###/// better way to show time
### Python time interval
### Python human readable time
		self.timew["text"] = self.bookmark.time
		###/// color or other way to display
###Python scalar display Widget
		self.distw["text"] = str(self.bookmark.statePoint.data) + "   " + str(self.bookmark.distCS())

		self.main.pack()

	# Hide the widget, for those we currently don't need
	def hideBookmark (self):
		self.main.pack_forget()

	def callback (self, ignoreevent):
		pad.sendBookmark (self.bookmark.url)

############################################################
# COMMUNICATE WITH BRAIN DEVICE
############################################################

###/// Test with brainclient, is continuous viewCBtoo jarring, prefer old timer approach??

# Call from brainclient, arg = line of text from matlab
# This is coming from a separate thread,
# both threads access currentBrainState and currentInterest
# we set them, others just read them (except the GUI slider)
# and it's a single atomic setting of a variable,
# so synchronization issues should be ok
def brainCB (line):
###///	global currentState
###///	global currentInterest

	tokens = line.strip().split (",")
	if len(tokens) < 1:
		print ("brainCB: can't parse input line: " + line, file=sys.stderr)

	else:
		print (tokens) ###/// is this stuff working ok, still need print stmts?
		pad.currentState = StatePoint (list (map (float, tokens)))

		# Optional: display it back to user via the sliders
		print (pad.currentState.data) ###///
		for i in range (len (pad.currentState.data)):
			print (pad.currentState.data[i]) ###///
			brainVars[i].set (pad.currentState.data[i]) #/// does this trigger another callback or many?

		# Placeholder, intend to be getting this from physio or other sensor
		pad.currentInterest = random.random()
		
		if continuousVar.get()==1: viewCB()

# Observer callback, ie when value of a brain slider changes
def brainVarCB (var, index):
	print ("brainVarCB", var, index) #/// TO TEST ABOVE --does this trigger another callback
	pad.currentState.data[index] = var.get()

	if continuousVar.get()==1: viewCB()

############################################################
# WINDOW AND WIDGET SETUP
############################################################

# Main window
top = tkinter.Tk()
top.title ("Brain Scratchpad Prototype")

# Control panel area
controlPanel = tkinter.Frame (top)
controlPanel.pack (side="top")
buttonFont = ('', '36', 'bold')

# Save button
saveButton = tkinter.Button (controlPanel, text="Save", font=buttonFont)
saveButton["command"] = saveCB
saveButton.pack(side="left")

# View button, only applies if not in continuous update mode
viewButton = tkinter.Button (controlPanel, text = "View", font=buttonFont)
viewButton["command"] = viewCB
viewButton.pack(side="left")

# Toggle continuous update mode
continuousVar = tkinter.IntVar()
continuousBox = tkinter.Checkbutton (controlPanel, text="Update continuously", variable=continuousVar)
continuousVar.trace ("w", continuousVarCB)
continuousBox.pack(side="top")

# Bookmarks panel area
bookmarksPanel = tkinter.Frame (top)
bookmarksPanel.pack (side="top")

# Empty widgets, each can show a bookmark, max of 5
bookmarkWidgets = []
for i in range (5):
	bookmarkWidgets.append (BookmarkW (bookmarksPanel))

# Sliders panel area
slidersPanel = tkinter.Frame (top, borderwidth=2, background="black")
slidersPanel.pack (side="top")

# Sliders
# NB subscripts in brainVars match those in currentState
brainVars = []
for i in range (5):
	v = tkinter.DoubleVar()
	v.trace ("w", lambda *args, v=v, index=i: brainVarCB(v, index))
	brainVars.append (v)
	s = tkinter.Scale (slidersPanel, variable=v, from_=1.0, to_=0, resolution=0.1)
	s.pack(side="left")

############################################################
# MAIN LOOP
############################################################

# Start up brainclient
bclientThread = threading.Thread (target=brainclient.mainloop, args=[brainCB])
bclientThread.start()

# Start this one off
viewCB()

# Run our GUI loop
top.mainloop()

# Also quit brainclient cleanly, when our window closes
brainclient.quit = True
