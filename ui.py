# UI code is separated out here, just for modularity

import tkinter
import time, datetime, sys, random ###

### layout: some padding or margin??

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

	# Populate the widget with given bookmark
	def showBookmark (self, bookmark, sendBookmark):
		self.bookmark = bookmark
		self.sendBookmark = sendBookmark

		self.urlw["text"] = self.bookmark.url
		self.titlew["text"] = self.bookmark.title
		self.selectionw["text"] = self.bookmark.selection
		###	image = tkinter.PhotoImage (file=bookmark.thumb)
		###	self.thumb["image"] = image
		self.thumbw["text"] = bookmark.thumb
		### better way to show time
		self.timew["text"] = self.bookmark.time
		### color or other way to display
		self.distw["text"] = self.bookmark.distCS()

		self.main.pack()

	# Hide the widget, for those we currently don't need
	def hideBookmark (self):
		self.main.pack_forget()

	def callback (self, ignoreevent):
		self.sendBookmark (self.bookmark.url)

# Plug the bookmarks into the bookmark widgets
def showBookmarks (bookmarks, sendBookmark):
	ndraw = min (len(bookmarks), len(bookmarkWidgets))

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

	for i in range (ndraw):
		bookmarkWidgets[i].showBookmark(bookmarks[i], sendBookmark)

	# Make the rest of them, if any, invisible
	for i in range (ndraw, len(bookmarkWidgets)):
		bookmarkWidgets[i].hideBookmark()

### ALSO CAN USE
### height in lines (else fits to contents)
### width (chars not pixels)
### textvariable instead of text: You can set its textvariable option to a StringVar. Then any call to the variable's .set() method will change the text displayed on the label. This is not necessary if the label's text is static; use the text attribute for labels that don't change while the application is running.
### wraplength (chars) default = break only at newlines

# Draw a given bookmark, by creating some widgets for it,
# and give it arg callback
# and install it under our bookmarksPanel
def drawBookmarkNOT (bookmark, callback):
	main = tkinter.Frame (bookmarksPanel, borderwidth=1, background="grey")
	# Pass our "bookmark" in to the callback
	main.bind ("<Button-1>", lambda event, bookmark=bookmark: callback (event, bookmark))
	main.pack (side="top", fill="both", expand=True)

	w = tkinter.Label (main, text=bookmark.url, font=('', '10', ''))
	w.bind ("<Button-1>", lambda event, bookmark=bookmark: callback (event, bookmark))
	w.pack (side="top", fill="both", expand=True)

	w = tkinter.Label (main, text=bookmark.title, font=('', '12', 'bold'))
	w.bind ("<Button-1>", lambda event, bookmark=bookmark: callback (event, bookmark))
	w.pack (side="top", fill="both", expand=True)

	w = tkinter.Label (main, text=bookmark.selection)
	w.bind ("<Button-1>", lambda event, bookmark=bookmark: callback (event, bookmark))
	w.pack (side="top", fill="both", expand=True)

	w = tkinter.Label (main)
	w.bind ("<Button-1>", lambda event, bookmark=bookmark: callback (event, bookmark))
###	image = tkinter.PhotoImage (file=bookmark.thumb)
###	w["image"] = image
	w["text"] = bookmark.thumb
	w.pack (side="top", fill="both", expand=True)

	### better way to show time
	w = tkinter.Label (main)
	w.bind ("<Button-1>", lambda event, bookmark=bookmark: callback (event, bookmark))
	w["text"] = bookmark.time
	w.pack (side="top", fill="both", expand=True)

	### color or other way to display
	w = tkinter.Label (main)
	w.bind ("<Button-1>", lambda event, bookmark=bookmark: callback (event, bookmark))
	w["text"] = bookmark.distCS()
	w.pack (side="top", fill="both", expand=True)

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
saveButton.pack(side="left")

# View button, only applies if not in continuous update mode
viewButton = tkinter.Button (controlPanel, text = "View", font=buttonFont)
viewButton.pack(side="left")

# Toggle continuous update mode
continuousBox = tkinter.Checkbutton (controlPanel, text="Update continuously")
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
### could try again 0..1 slider, problem was parse?
### maybe use Var()'s for them?
brainSliders = []
for i in range (5):
	s = tkinter.Scale (slidersPanel, from_=100, to_=0)
	brainSliders.append (s)
	s.pack(side="left")
