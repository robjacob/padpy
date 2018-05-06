# UI code is separated out here, just for modularity

import tkinter

### layout: some padding or margin??

# Remove old bookmarks
def resetBookmarksPanel ():
	if bookmarksPanel:
		for c in bookmarksPanel.winfo_children():
			c.destroy()

### ALSO CAN USE
### height in lines (else fits to contents)
### width (chars not pixels)
### textvariable instead of text: You can set its textvariable option to a StringVar. Then any call to the variable's .set() method will change the text displayed on the label. This is not necessary if the label's text is static; use the text attribute for labels that don't change while the application is running.
### wraplength (chars) default = break only at newlines

# Draw a given bookmark, by creating some widgets for it,
# and give it arg callback
# and install it under our bookmarksPanel
def drawBookmark (bookmark, callback):
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

# Sliders panel area
slidersPanel = tkinter.Frame (top, borderwidth=2, background="black")
slidersPanel.pack (side="top")

# Sliders
brainSliders = []
for i in range (5):
	s = tkinter.Scale (slidersPanel, from_=100, to_=0)
	brainSliders.append (s)
	s.pack(side="left")
