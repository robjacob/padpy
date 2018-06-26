# Apply filter to stream of raw numerical brain data

# This is currently a no-op placeholder
# for a simple low pass/moving average filter.
# But if it's better to do the filtering inside of neuracle, can forget about this.

# Send each new multidimensional data point to us (as a list of floats)
# we send back the appropriate new point to use.
# We retain as much data as we need to do the filtering.

import pad

class MAvgFilter:
	def __init__ (self, nwindow=5):
		self.nwindow = nwindow

		# Saves as much recent input data as we'll use,
		# latest value at beginning
		self.data = []

	def process (self, inp):
		self.data.insert (0, inp)

		# Truncate to how many we use
		# BTW this creates new copy, can use "del" to delete in place
		self.data = self.data[:self.nwindow]

		# Does nothing for now
		return inp

#
# SIMPLE UNIT TEST
#

if __name__=="__main__":
	import sys

	myfilter = MAvgFilter()

	# Not implemented
