# Apply filter to stream of raw numerical brain data

# This is a simple low pass/moving average or box filter.
# For more sophisticated filters, can use numpy.convolve()
# If it's better to do the filtering inside of neuracle, can forget about this.

# Send each new multidimensional data point to us (as a list of floats)
# we send back the appropriate new point to use.
# We retain as much data as we need to do the filtering.

import pad

class MAvgFilter:
	def __init__ (self):
		# User-settable parameter
		self.nwindow = 5

		# Saves as much recent input data as we'll use,
		# array of multi-dimensional data points,
		# latest value at beginning
		self.data = []

	def process (self, inp):
		self.data.insert (0, inp)

		# Truncate to how many we use
		# BTW this creates new copy, can use "del" to delete in place
		self.data = self.data[:self.nwindow]

		# Mean value for each dimension,
		# in slighly weird semi-functional programming style.
		# Can also do this easily with numpy.
		return [ float(sum(l)) / len(l) for l in zip(*self.data) ]

#
# SIMPLE UNIT TEST
#

if __name__=="__main__":
	import sys

	myfilter = MAvgFilter()

	inp = [.0, 0, 0, 0, 0] ; print (inp, "->", myfilter.process(inp))
	inp = [.0, 0, 0, 0, 0] ; print (inp, "->", myfilter.process(inp))
	inp = [.4, .1, 0, 0, 0] ; print (inp, "->", myfilter.process(inp))
	inp = [.4, 0, .2, 0, 0] ; print (inp, "->", myfilter.process(inp))
	inp = [.4, 0, 0, .3, 0] ; print (inp, "->", myfilter.process(inp))
	inp = [.4, 0, 0, 0, .5] ; print (inp, "->", myfilter.process(inp))
	inp = [.4, 0, .2, 0, 0] ; print (inp, "->", myfilter.process(inp))
	inp = [.4, .1, 0, 0, 0] ; print (inp, "->", myfilter.process(inp))
	inp = [.4, 0, .2, 0, 0] ; print (inp, "->", myfilter.process(inp))
	inp = [.4, .1, 0, 0, 0] ; print (inp, "->", myfilter.process(inp))
	inp = [.4, 0, .2, 0, 0] ; print (inp, "->", myfilter.process(inp))
	inp = [.4, .1, 0, 0, 0] ; print (inp, "->", myfilter.process(inp))
	inp = [.4, 0, .2, 0, 0] ; print (inp, "->", myfilter.process(inp))
	inp = [.4, .1, 0, 0, 0] ; print (inp, "->", myfilter.process(inp))
	inp = [.4, 0, .2, 0, 0] ; print (inp, "->", myfilter.process(inp))
	inp = [.4, .1, 0, 0, 0] ; print (inp, "->", myfilter.process(inp))
	inp = [.4, 0, .2, 0, 0] ; print (inp, "->", myfilter.process(inp))
