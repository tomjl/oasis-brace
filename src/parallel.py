import time
from threading import Thread, Event
from queue import Queue

class IMU_Thread(Thread):
	"""
	The wrapper that lets us order motors to do things and not wait for it to complete 
	
	Repeats as fast as possible
			t = IMU_Thread(imu)
			t.start()
			t.cancel()     # stop the thread's action if it's still waiting

	modified from https://github.com/python/cpython/blob/master/Lib/threading.py
	to repeat instead of being one-off.

	"""

	def __init__(self, imu1, imu2, queue=Queue()):
		Thread.__init__(self)
		self.imu1 = imu1
		self.imu2 = imu2
		self.q = queue
		self.finished = Event()

	def cancel(self):
		"""Stop the timer if it hasn't finished yet."""
		self.finished.set()

	def run(self):
		while not self.finished.is_set():
			
			readings1 = self.imu1.all_readings
			readings2 = self.imu2.all_readings

			self.q.put((time.time(),readings1, readings2))


class Motor_Thread(Thread):
	"""
	The wrapper that lets us order motors to do things and not wait for it to complete 
	Runs until you stop it
	Accepts motor position commands into a queue.

	TODO: change queue to accept state commands instead of positional ones
	"""
	def __init__(self, motors, queue=Queue()):
		Thread.__init__(self)
		self.motors = motors
		self.q = queue
		self.finished = Event()

	def cancel(self):
		self.finished.set()

	def run(self):
		while not self.finished.is_set():
			position = self.q.get(block=True) # oh my god this actually worked
			self.motors.movetoPosition(position)

		self.motors.abort() # stop motors from running if cancel() is called


class Classifier_Thread(Thread):
	"""
	The wrapper that automatically updates the motion state when a new IMU sample arrives.
	each operation takes order 1e-5 seconds so the thread blocks between IMU samples (0.023 s average)

	Right now it doesn't do anything with the values

	TODO: Issue state commands to motor thread via output queue
	"""
	def __init__(self, classifier, input_q, output_q):
		Thread.__init__(self)
		self.classifier = classifier
		self.input_q  = input_q
		self.output_q = output_q
		self.finished = Event()

	def cancel(self):
		self.finished.set()

	def run(self):
		# REMOVE THESE PRINTS EVENTUALLY
		t0 = time.time()
		while not self.finished.is_set():
			sample = self.input_q.get(block=True) # wait on new samples
			self.classifier.addSample(sample)
			state = self.classifier.getState()
			print(time.time()-t0, state)
			t0 = time.time()


