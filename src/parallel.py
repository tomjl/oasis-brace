import time
from threading import Thread, Event
from queue import Queue

class Motor_Queue:
	'''
	Making a wrapper with more concise put/gets for this application
	I'm basically only doing this as a way to use block = True.
	If I had more time I'd make a better state object with thread blocking

	Purpose: stores only up to most recent state that hasn't been processed yet
	'''
	def __init__(self):
		self.q = Queue(maxsize=1)

	def get(self):
		return self.q.get(block=True)

	def put(self, item):
		if self.q.full(): # empty queue before adding next item
			_ = self.q.get()
		self.q.put(item)
		return

class IMU_Queue:
	'''
	Making a wrapper just to be consistent with Motor_Queue
	'''
	def __init__(self):
		self.q = Queue()

	def get(self):
		return self.q.get(block=True)

	def put(self, item):
		self.q.put(item)
		return

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

	def __init__(self, imu1, imu2, imu_q):
		Thread.__init__(self)
		self.imu1 = imu1
		self.imu2 = imu2
		self.q = imu_q
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
	def __init__(self, motors, motor_q):
		Thread.__init__(self)
		self.motors = motors
		self.q = motor_q
		self.finished = Event()

	def cancel(self):
		self.finished.set()

	def run(self):
		while not self.finished.is_set():
			position = self.q.get() # wait on new samples, block=True
			self.motors.movetoPosition(position)

		self.motors.abort() # stop motors from running if cancel() is called

class Classifier_Thread(Thread):
	"""
	The wrapper that automatically updates the motion state when a new IMU sample arrives.
	each operation takes order 1e-5 seconds so the thread blocks between IMU samples (0.023 s average)

	Right now it doesn't do anything with the values

	TODO: Issue state commands to motor thread via output queue
	"""
	def __init__(self, classifier, imu_q, motor_q):
		Thread.__init__(self)
		self.classifier = classifier
		self.imu_q  = imu_q
		self.motor_q = motor_q
		self.finished = Event()
		self.state = None

	def cancel(self):
		self.finished.set()

	def run(self):
		# REMOVE THESE PRINTS EVENTUALLY
		t0 = time.time()
		t1 = time.time()
		COOLDOWN  = 4 # 4 second cooldown after state switch
		ANGLE_MAX = 15 # knee less than 30˚ to move 
		while not self.finished.is_set():
			sample = self.imu_q.get() # wait on new samples, block=True
			knee_angle = self.classifier.addSample(sample)

			state = self.classifier.getState()
			cooldown_condition = time.time()-t1 >= COOLDOWN
			angle_condition = knee_angle <= ANGLE_MAX

			if state != self.state and cooldown_condition and angle_condition: # command new state under certain conditions
				self.motor_q.put(state)
				self.state = state
				t1 = time.time() 

			print(time.time()-t0, state)
			#print('stairs' if state else 'walking')
			t0 = time.time()


