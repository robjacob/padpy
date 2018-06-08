#!/usr/bin/env python3
# Main program, including UI and callbacks

import time, datetime, sys
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
# is also called from some other places
# 
def viewCB ():
	# Sort by distance, into new temporary list
	bookmarks = sorted (pad.allBookmarks, key=lambda b: b.distCS())

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

# Layout parameters
# NB See pad.thumbSize for pixel size of our [square] thumbnails
padding = 3
barWidth = 15
barHeight = pad.thumbSize - 10
titleWidth = 30
urlWidth = 40
selectionWidth = 40

# An initially-blank widget that can show data for a bookmark,
# can be changed subsequently to show a different bookmark.
# Doing it this way, rather than deleting the widgets and making new ones,
# seems to avoid flashing in the UI
class BookmarkW:
	# Make the blank widget
	def __init__ (self, bookmarksPanel):
		self.bookmark = None
		
		# Gives nicer looking grey border than usual tkinter.Frame (..., relief="solid", borderwidth=1)
		self.main = tkinter.LabelFrame (bookmarksPanel, borderwidth=1)
		# Set our grid() parameters below not here
		self.main.grid (row=0, column=0)

		leftGrid = tkinter.Frame (self.main)
		leftGrid.grid (row=0, column=0, padx=padding, pady=padding)

		rightGrid = tkinter.Frame (self.main)
		rightGrid.grid (row=0, column=1, padx=padding, pady=padding)

		self.distw = tkinter.Canvas (leftGrid, width=barWidth, height=barHeight)
		self.distw.grid (row=0, column=0, padx=padding, pady=padding)

		self.thumbw = tkinter.Canvas (leftGrid, width=pad.thumbSize, height=pad.thumbSize)
		self.thumbw.grid (row=0, column=1, padx=padding, pady=padding)

		self.titlew = tkinter.Label (rightGrid, font=('', '18', ''))
		self.titlew.grid (sticky=tkinter.W+tkinter.N, padx=padding)
		
		self.timew = tkinter.Label (rightGrid, foreground="grey50")
		self.timew.grid (sticky=tkinter.W+tkinter.N, padx=padding)

		self.urlw = tkinter.Label (rightGrid, font=('', '10', ''))
		self.urlw.grid (sticky=tkinter.W+tkinter.N, padx=padding)

		self.selectionw = tkinter.Label (rightGrid, font=('', '10', 'italic'), fg="grey40")
		self.selectionw.grid (sticky=tkinter.W+tkinter.N, padx=padding)

		# Attach our callback to our widget and everything inside
		self._bindAll (self.main, "<Button-1>")

		# Hide ourself until someone uses us
		self.main.grid_forget()

	# Private helper function, for recursive binding
	def _bindAll (self, root, event):
		root.bind (event, self.callback)
		if len(root.children.values())>0:
			for child in root.children.values():
				self._bindAll (child, event)

	# Populate this widget with data from the given bookmark
	def showBookmark (self, bookmark):
		self.bookmark = bookmark

		# Make bar graph for distance
		self.distw.delete(tkinter.ALL)
		# 2 is arbitrary fudge factor
		cutoffDist = len(brainVars)/2
		y = barHeight * (self.bookmark.distCS()/cutoffDist)
		# Seems to need 3 pixels padding else outline doesn't show up
		self.distw.create_rectangle(3, 3, barWidth, barHeight)
		self.distw.create_rectangle(3, y, barWidth, barHeight, fill="indian red", outline="")

		# Thumbnail
		# Preserve image as ivar, cause canvas only keeps pointer to it
		self.thumbImage = tkinter.PhotoImage (file=bookmark.thumb)
		self.thumbw.delete(tkinter.ALL)
		self.thumbw.create_image (0, 0, image=self.thumbImage, anchor=tkinter.NW)

		# Text fields
		self.titlew["text"] = self._shorten (self.bookmark.title, titleWidth)
		self.urlw["text"] = self._shorten (self.bookmark.url, urlWidth)
		self.selectionw["text"] = self._shorten (self.bookmark.selection, selectionWidth)
		self.timew["text"] = "%.0f sec. ago" % (datetime.datetime.today() - self.bookmark.time).total_seconds()

		# Set our parameters here not above
		self.main.grid (sticky=tkinter.E + tkinter.W)

	# Hide the widget, for those we currently don't need
	def hideBookmark (self):
		self.main.grid_forget()

	# Tell browser to go to our bookmarked page
	def callback (self, ignoreevent):
		pad.sendBookmark (self.bookmark.url)

	# Private helper function, truncates string to width,
	# adding "..." if appropriate
	# also turns None into ""
	# Similar to textwrap.shorten()
	def _shorten (self, string, width):
		if string==None:
			return ""
		elif len(string)<width:
			return string
		else:
			return string[:width] + "..."

############################################################
# COMMUNICATE WITH BRAIN DEVICE
############################################################

# Call from brainclient, arg = line of text from matlab
# This is coming from a separate thread,
# both threads access currentBrainState
# we set it, others just read it (except the GUI slider)
# and it's a single atomic setting of a variable,
# so synchronization issues should be ok
def brainCB (line):
	tokens = line.strip().split (",")
	if len(tokens) < 1:
		print ("brainCB: can't parse input line: " + line, file=sys.stderr)

	else:
		pad.currentState = pad.StatePoint (list (map (float, tokens)))

		# Display it back to user via the sliders
		for i in range (len (pad.currentState.data)):
			brainVars[i].set (pad.currentState.data[i])

		# ...which will also trigger a viewCB() so no need for us to call it

# Observer callback, ie when value of a brain slider variable changes
def brainVarCB (var, index):
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
controlPanel.grid (row=0, column=0)
buttonFont = ('', '24', 'bold')

# Save button
saveButton = tkinter.Button (controlPanel, text="Save", font=buttonFont)
saveButton["command"] = saveCB
saveButton.grid (row=0, column=0)

# View button, only applies if not in continuous update mode
viewButton = tkinter.Button (controlPanel, text = "View", font=buttonFont)
viewButton["command"] = viewCB
viewButton.grid (row=0, column=1)

# Toggle continuous update mode
continuousVar = tkinter.IntVar()
continuousBox = tkinter.Checkbutton (controlPanel, text="Update continuously", variable=continuousVar)
continuousVar.trace ("w", continuousVarCB)
continuousBox.grid (row=0, column=2)

# Bookmarks panel area
bookmarksPanel = tkinter.Frame (top)
bookmarksPanel.grid (row=1, column=0)

# Empty widgets, each can show a bookmark, max of 5 for now
bookmarkWidgets = []
for i in range (5):
	bookmarkWidgets.append (BookmarkW (bookmarksPanel))

# Sliders panel area
slidersFrame = tkinter.LabelFrame (top, text="Brain input")
slidersFrame.grid (row=2, column=0)

# Sliders
# NB subscripts in brainVars match those in currentState
brainVars = []
for i in range (5):
	v = tkinter.DoubleVar()
	v.trace ("w", lambda *args, v=v, index=i: brainVarCB(v, index))
	brainVars.append (v)
	s = tkinter.Scale (slidersFrame, variable=v, from_=1.0, to_=0, resolution=0.1)
	s.grid (row=0, column=i)

############################################################
# MAIN LOOP
############################################################

# Start up brainclient
b = bclientThread = threading.Thread (target=brainclient.mainloop, args=[brainCB])
bclientThread.start()

# Start things off
viewCB()

# Run our GUI loop
top.mainloop()

# To quit brainclient cleanly, after our main window closes
brainclient.quit = True
