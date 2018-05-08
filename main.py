#!/usr/bin/env python3
# Main program, including UI

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
# Checkbox callback: Toggle continuous view refresh
#
def continuousCB ():
	if continuousVar.get()==1:
		viewButton["state"] = tkinter.DISABLED
	else:
		viewButton["state"] = tkinter.NORMAL

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
			brainSliders[i].set (pad.currentState.data[i] * 100)

		# Placeholder, intend to be getting this from physio or other sensor
		pad.currentInterest = random.random()
		
		if continuousVar.get()==1: viewCB()

# When a brainSlider is changed
# NB our sliders run 0..100 but data from brainClient assumed to run 0..1
def brainSliderCB (ignorearg):
	for i in range (len (pad.currentState.data)):
		pad.currentState.data[i] = brainSliders[i].get()/100.0

	if continuousVar.get()==1: viewCB()

############################################################
# OTHER UI FUNCTIONS
############################################################

###/// layout: some padding or margin??

###/// ALSO CAN USE
###/// height in lines (else fits to contents)
###/// width (chars not pixels)
###/// textvariable instead of text: You can set its textvariable option to a StringVar. Then any call to the variable's .set() method will change the text displayed on the label. This is not necessary if the label's text is static; use the text attribute for labels that don't change while the application is running.
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
		self.main.bind ("<Button-1>", self.callback)
		self.main.pack (side="top", fill="both", expand=True)

		self.urlw = tkinter.Label (self.main, font=('', '10', ''))
###/// do I really have to set the callback on every widget,
###/// or is there an easier way
###/// or at least enumerate children
###///    for child in widget.children.values():

		self.urlw.bind ("<Button-1>", self.callback)
		self.urlw.pack (side="top", fill="both", expand=True)

		self.titlew = tkinter.Label (self.main, font=('', '12', 'bold'))
		self.titlew.bind ("<Button-1>", self.callback)
		self.titlew.pack (side="top", fill="both", expand=True)

		self.selectionw = tkinter.Label (self.main)
		self.selectionw.bind ("<Button-1>", self.callback)
		self.selectionw.pack (side="top", fill="both", expand=True)

		self.thumbw = tkinter.Label (self.main)
		self.thumbw.bind ("<Button-1>", self.callback)
		self.thumbw.pack (side="top", fill="both", expand=True)

		self.timew = tkinter.Label (self.main)
		self.timew.bind ("<Button-1>", self.callback)
		self.timew.pack (side="top", fill="both", expand=True)

		self.distw = tkinter.Label (self.main)
		self.distw.bind ("<Button-1>", self.callback)
		self.distw.pack (side="top", fill="both", expand=True)

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
		self.timew["text"] = self.bookmark.time
		###/// color or other way to display
		self.distw["text"] = str(self.bookmark.statePoint.data) + "   " + str(self.bookmark.distCS())

		self.main.pack()

	# Hide the widget, for those we currently don't need
	def hideBookmark (self):
		self.main.pack_forget()

	def callback (self, ignoreevent):
		pad.sendBookmark (self.bookmark.url)

############################################################
# WINDOW AND WIDGET SETUP
############################################################

# Main window
top = tkinter.Tk()
top.title ("Brain Scratchpad Prototype")

buttonFont = ('', '36', 'bold')

# Control panel area
controlPanel = tkinter.Frame (top)
controlPanel.pack (side="top")

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
continuousBox["command"] = continuousCB
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
###/// could try again 0..1 slider, problem was parse?
###/// maybe use Var()'s for them?
brainSliders = []
for i in range (5):
	s = tkinter.Scale (slidersPanel, from_=100, to_=0)
	s["command"] = brainSliderCB
	brainSliders.append (s)
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
