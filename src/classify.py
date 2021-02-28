import time
import numpy as np
from bno08x import (
	BNO_REPORT_LINEAR_ACCELERATION,
	BNO_REPORT_ROTATION_VECTOR,
	BNO_REPORT_GEOMAGNETIC_ROTATION_VECTOR,
)

_TIME_DELAY = 1.35 # 1.35 seconds from test data seems to work well 
_BUFFER_SIZE = 300 # 0.023s unimpeded average = 6.89 second buffer. should be more than enough
_THRESHOLDS = [50, 45] # upper, lower

_WALKING_STATE = 0
_STAIRS_STATE  = 1

class SimpleMotionClassifier:

	'''
	Classify between walking and climbing stairs. 
	Would eventually be extended to include running and more

	initial concept for moving average thresholding:
	- create big buffer and rolling index
	- two columns: timestamp and angle value
	- every step logically index buffer to last 4 seconds and np.mean
	
	'''

	def __init__(self, thresholds=_THRESHOLDS, buffersize=_BUFFER_SIZE, window=_TIME_DELAY):
		self.buffersize = buffersize
		self.data = np.zeros((buffersize,2))
		self.window = window
		self.thresholds = thresholds

		self.idx = 0
		self.state = _WALKING_STATE
		self.time = time.time()

	def _recalculate_state(self):
		# This is the function that would be reimplimented with a different classifier type

		logical_slice = self.data[:,0] >= self.time - self.window # get indices of all angles in time window
		val = np.mean(self.data[logical_slice,1]) # get average of all angles in window

		if val >= self.thresholds[0] and self.state==_WALKING_STATE:
			self.state = _STAIRS_STATE
		elif val < self.thresholds[1] and self.state==_STAIRS_STATE:
			self.state = _WALKING_STATE
		return 

	def addSample(self,readings):
		self.time = readings[0]
		angle1 = readings[1][BNO_REPORT_ROTATION_VECTOR][0] # first imu, rotation vector, x axis 
		angle2 = readings[2][BNO_REPORT_ROTATION_VECTOR][0] # second imu, rotation vector, x axis 
		val = angle1-angle2 # knee angle + some offset

		self.data[self.idx] = [self.time,val]
		self.idx = (self.idx + 1)%self.buffersize # will just keep overwriting the oldest data in the buffer
		return

	def getState(self):
		self._recalculate_state()
		return self.state







