#!/usr/bin/env python3
# Main program, including UI and callbacks

import time, datetime, sys
import random
import threading
import tkinter as tk
import tkinter.ttk as ttk

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
# Actually simply setting continousViewVar itself is what does the job,
# we just disable/enable the view button here
#
def continuousViewVarCB (*ignoreargs):
	if continuousViewVar.get()==1:
		# Optional if brain data is streaming anyway, just to start us off
		viewCB()

	viewButton["state"] = tk.DISABLED if continuousViewVar.get()==1 else tk.NORMAL

#
# Similar, for save
#
def continuousSaveVarCB (*ignoreargs):
	if continuousSaveVar.get()==1:
		continuousSaveTick ()

	saveButton["state"] = tk.DISABLED if continuousSaveVar.get()==1 else tk.NORMAL

#
# Timer callback for continousSave
# Receive tick, do the job, then set up the next callback
#
def continuousSaveTick ():
	if continuousSaveVar.get()==1:
		bookmark = pad.getBookmark()
		if bookmark.url not in map (lambda b: b.url, pad.allBookmarks):
			pad.allBookmarks.append (bookmark)
			viewCB()
		# else: maybe update brain state data of this bookmark in allBookmarks (or delete and replace it)

		top.after (1000, continuousSaveTick)

############################################################
# OTHER UI-RELATED FUNCTIONS
############################################################

# Layout parameters
# NB See pad.thumbSize for pixel size of our [square] thumbnails
buttonPadding=[30, 20, 30, 20]
padding = 3
allPadding = [padding, padding, padding, padding]
xPadding = [padding, 0, padding, 0]
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
		
		style = ttk.Style()

		self.main = ttk.Frame (bookmarksPanel)
		# We will set our grid() parameters below not here
		self.main.grid (row=0, column=0)

		self.main.grid_rowconfigure(0, weight=1)
		sep = ttk.Separator (self.main, orient="horizontal")
		sep.grid (row=0, column=0, sticky="ew", columnspan=2)

		style.configure ("bm.TFrame", padding=allPadding)
		leftGrid = ttk.Frame (self.main, style="bm.TFrame")
		leftGrid.grid (row=1, column=0)

		rightGrid = ttk.Frame (self.main, style="bm.TFrame")
		rightGrid.grid (row=1, column=1)

		self.distw = tk.Canvas (leftGrid, width=barWidth, height=barHeight)
		self.distw.grid (row=0, column=0, padx=padding, pady=padding)

		self.thumbw = tk.Canvas (leftGrid, width=pad.thumbSize, height=pad.thumbSize)
		self.thumbw.grid (row=0, column=1, padx=padding, pady=padding)

		style.configure ("title.TLabel", padding=xPadding, font=('', '16', 'bold'))
		self.titlew = ttk.Label (rightGrid, style="title.TLabel")
		self.titlew.grid (sticky=tk.W+tk.N)

		style.configure ("time.TLabel", padding=xPadding, foreground="grey50")
		self.timew = ttk.Label (rightGrid, style="time.TLabel")
		self.timew.grid (sticky=tk.W+tk.N)

		style.configure ("url.TLabel", padding=xPadding, font=('', '10', ''))
		self.urlw = ttk.Label (rightGrid, style="url.TLabel")
		self.urlw.grid (sticky=tk.W+tk.N)

		style.configure ("selection.TLabel", font=('', '10', 'italic'), fg="grey40", padding=allPadding)
		self.selectionw = ttk.Label (rightGrid, style="selection.TLabel")
		self.selectionw.grid (sticky=tk.W+tk.N)

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
		self.distw.delete(tk.ALL)
		# 2 is arbitrary fudge factor
		cutoffDist = len(brainVars)/2
		y = barHeight * (self.bookmark.distCS()/cutoffDist)
		# Seems to need 3 pixels padding else outline doesn't show up
		self.distw.create_rectangle(3, 3, barWidth, barHeight)
		self.distw.create_rectangle(3, y, barWidth, barHeight, fill="indian red", outline="")

		# Thumbnail
		# Preserve image as ivar, cause canvas only keeps pointer to it
		self.thumbImage = tk.PhotoImage (file=bookmark.thumb)
		self.thumbw.delete(tk.ALL)
		self.thumbw.create_image (0, 0, image=self.thumbImage, anchor=tk.NW)

		# Text fields
		self.titlew["text"] = self._shorten (self.bookmark.title, titleWidth)
		self.urlw["text"] = self._shorten (self.bookmark.url, urlWidth)
		self.selectionw["text"] = self._shorten (self.bookmark.selection, selectionWidth)
		self.timew["text"] = "%.0f sec. ago" % (datetime.datetime.today() - self.bookmark.time).total_seconds()

		# Set our parameters here not above
		self.main.grid (sticky=tk.E + tk.W)

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
# manually or because brainCB() above changes it
def brainVarCB (var, index):
	pad.currentState.data[index] = var.get()

	if continuousViewVar.get()==1: viewCB()

############################################################
# WINDOW AND WIDGET SETUP
############################################################

# Main window
top = tk.Tk()
top.title ("Brain Scratchpad Prototype")

# Control panel area
controlPanel = ttk.Frame (top)
controlPanel.grid (row=0, column=0)

# Our button style
style = ttk.Style()
style.configure ("cp.TButton",
	 font=('', 24, 'bold'), foreground="saddlebrown", padding=buttonPadding)

# View button, only applies if not in continuous view update mode
viewButton = ttk.Button (controlPanel, text = "View", style="cp.TButton")
viewButton["command"] = viewCB
viewButton.grid (row=0, column=0)

# Save button
saveButton = ttk.Button (controlPanel, text="Save", style="cp.TButton")
saveButton["command"] = saveCB
saveButton.grid (row=0, column=1)

# Toggle continuous update mode
continuousViewVar = tk.IntVar()
style.configure ("cp.TCheckbutton", foreground="saddlebrown")
continuousViewBox = ttk.Checkbutton (controlPanel, text="Update continuously", variable=continuousViewVar, style="cp.TCheckbutton")
continuousViewVar.trace ("w", continuousViewVarCB)
continuousViewBox.grid (row=1, column=0)

# Toggle continuous save mode
continuousSaveVar = tk.IntVar()
style.configure ("cp.TCheckbutton", foreground="saddlebrown")
continuousSaveBox = ttk.Checkbutton (controlPanel, text="Save continuously", variable=continuousSaveVar, style="cp.TCheckbutton")
continuousSaveVar.trace ("w", continuousSaveVarCB)
continuousSaveBox.grid (row=1, column=1)

# Bookmarks panel area
bookmarksPanel = ttk.Frame (top)
bookmarksPanel.grid (row=2, column=0, pady=20)

# Empty widgets, each can show a bookmark, max of 5 for now
bookmarkWidgets = []
for i in range (5):
	bookmarkWidgets.append (BookmarkW (bookmarksPanel))

# Sliders panel area
slidersFrame = tk.LabelFrame (top, text="Brain input")
slidersFrame.grid (row=3, column=0, pady=20, sticky="we")

# Sliders
# NB subscripts in brainVars match those in currentState
brainVars = []
for i in range (5):
	v = tk.DoubleVar()
	v.trace ("w", lambda *args, v=v, index=i: brainVarCB(v, index))
	brainVars.append (v)
	s = tk.Scale (slidersFrame, variable=v, from_=1.0, to_=0, resolution=0.1)
	s.grid (row=0, column=i)

############################################################
# MAIN LOOP
############################################################

# Start up brainclient
bclientThread = threading.Thread (target=brainclient.mainloop, args=[brainCB])
bclientThread.start()

# Start things off
viewCB()

# Run our GUI loop
top.mainloop()

# To quit brainclient cleanly, after our main window closes
brainclient.quit = True
