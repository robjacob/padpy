# Multi-state Scratchpad Prototype

## Usage (on Mac)

Run Safari with one window

python3 main.py

### Compatibility and porting:

* This system is currently implemented for Mac, using Safari.

    * You may need to set 'Allow JavaScript from Apple Events' option in
Safari's Develop menu

* Should work with different browsers on Mac: 

    * Change the Applescript commands as noted

* Should work on windows:

    * Replace the Applescript commands
with powerscript or any other code that will
perform the same tasks

## Conceptual Design

You have a list of web browser bookmarks

* Each is associated with a raw brain state or other passive reading.
There are no classifiers, we just index the bookmarks by the raw set of features of the data.

* Bookmarks are displayed continuously, in our window,
ordered by how close they are to your current state.

* You can bookmark additional pages and have them associated
with your state at the time of bookmarking.

### Brain:

The selection by brain state applies to both input and output:

* Save: when you bookmark something, brain state determines
where in the ordered list it goes.

* View: When you request information, brain state determines
the ordering of the bookmarks, ie the ones associated
with similar (nearest neighbor) states to your current
state come first.

### View:

Press View button = displays the bookmarks ordered by distance
to current brain state. 

Displays the top five items, ordered by distance from the current state.

Changes in brain state never directly cause a change in the browser window,
which would be disruptive.

### Save:

Press Save button = saves with the current brain state.

And the displayed list reorders itself.

Nearest neighbor approach:
Save each bookmark along with its raw data, no classifier

### Update continuously checkbox (experimental):

When selected, the system behaves as though the View button were pressed every time a change
occurs in input from the brain sensor or the sliders. This way
the display is always up to date, but it may be a distracting biofeedback
effect because
the bookmarks will be rearranged frequently based on their distance to
the current brain state.

### Save continuously checkbox (experimental):

When selected, the system behaves roughly as though the Save button were pressed
every second. The currently viewed page is added to the bookmark list,
unless the same URL was already bookmarked. In that case the brain
state stored with the previous bookmark is not updated, i.e., the brain state
for any URL remains what it was when it was first
bookmarked. This is a compromise intended avoid frequent shuffling of
the displayed bookmark list creating a biofeedback effect.

### Other plans:

The length of the bookmark list could be changeable, determined by

* Must be within RADIUSFAR otherwise forget it.

* And, even if there are many, want ALL entries that are
very close (ie within RADIUSNEAR), so I don't lose something I
thought I filed

Some of the state info could be physiological and some could be brain.

The bookmarks could also be marked with a separate orthogonal
dimension giving interest or arousal (placeholder is implemented).

Maybe we use context and other information as well as
brain state to choose among several bookmarks or group or
configurations, thinking again back to
activity-based window managers as an analogy

## Versions

See "padjs" for a browser-based javascript implementation.
This is a new, simpler, non-browser python version,
which is probably more useful.

It runs as a standalone main program,
so it can do polling, applescript, etc more easily than the browser/javascript version.
No front end/back end, everything is in one process (but it starts and owns a thread for brainclient).

However, without HTML/CSS/Javascript we are constrained to python's GUI toolkits.

## UI Implementation

Main window = vanilla Safari, running independently

Bookmark window =

* "Save" button

* "View" button

* Bookmarks display

* Sliders window = like other prototypes, not intended to be in final system

    * Also shows brain state back to the user

Bookmarks display

* Shows list of bookmarks, ordered.

* If you click a bookmark it sends main browser there.

* If you had copied a text region to the system clipboard, we save that (along
with URL of the page it was on) when you Save, otherwise we just save the
URL.


## Code Files

### main.py

Main program, including:

* UI and its commands and supporting code

* Communicate with brain device

* Main loop, including starting brainclient thread

### pad.py

Back end data structures and support functions, including:

* Bookmark and related classes

* Communicate with browser

### brainclient.py

Runs in separate thread, calls back to pad.py when it gets data

## Miscellaneous

Thumbnail stuff leaves junk files in $TMPDIR
