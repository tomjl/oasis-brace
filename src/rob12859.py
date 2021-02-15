import pigpio
import time

_STEPS_PER_REV 	  = 200
_DISTANCE_PER_REV = 2 # 2mm 

_FULL_STEP		= (0,0,0)
_HALF_STEP 		= (1,0,0)
_QUARTER_STEP   = (0,1,0)
_EIGHTH_STEP 	= (1,1,0)
_SIXTEENTH_STEP = (1,1,1)

_FORWARD  = 1
_BACKWARD = 0

_MOTOR_ON  = 0
_MOTOR_OFF = 1

_MIN_STEPS = 0
_MAX_STEPS = 100*100 # 100 mm max distance

_SPEED = 800 # PWM speed in Hz


"""
TODO:
- pigpio startup in bashrc (sudo?)
- get state/position stored
	- command queue? -> object
	- allow interruptions? prob not
	- JK

what we'll do: this object will be synchroous, so if we wait IN the moves function no conflicts can occur here.
Parallelization happens higher up. that's where we might need queue or reject actions
"""

_DEFAULT_PIN_CONFIG = {
	'STEP':   12,
	'DIR':	  17,
	'MS1': 	  27,
	'MS2':	  22,
	'MS3':	  23,
	'ENABLE': 24
}

class ROB12859:
	def __init__(self, gpio, pin_config):
		self._pin_config = pin_config
		self.gpio  		 = gpio
		self.stepsize 	 = _FULL_STEP
		self.moving 	 = False
		self.position 	 = 0 # VALUE IN STEPS
		self._initialize_driver()

	def _initialize_driver(self):
		self._disable()
		self._stop()
		self._write_stepsize()

	def _stop(self):
		self.gpio.set_PWM_dutycycle(self._pin_config['STEP'],0)

	def _start(self):
		self.gpio.set_PWM_dutycycle(self._pin_config['STEP'],128) # 50% duty cycle 

	def _write_stepsize(self):
		self.gpio.write(self._pin_config['MS1'],self.stepsize[0])
		self.gpio.write(self._pin_config['MS2'],self.stepsize[1])
		self.gpio.write(self._pin_config['MS3'],self.stepsize[2])

	def _enable(self):
		self.gpio.write(self._pin_config['ENABLE'],_MOTOR_ON)

	def _disable(self):
		self.gpio.write(self._pin_config['ENABLE'],_MOTOR_OFF)

	def setStepSize(self,stepsize):
		'''
		User facing. 
		Can be called mid-operation to change step size.
		'''

		self._stop() # make sure motor is stationary (it should be already)
		self.stepsize = stepsize
		self._write_stepsize() # write step size to GPIO pins

	def _move_steps(self,N):
		if N==0:
			print('_move_steps received 0 value. no moves made. ')
			return
		if not  (_MIN_STEPS <= self.position + N <= _MAX_STEPS):
			print('_move_steps received a vlue of N that puts position outsize of allowable range. no moves made.')
			return

		self._stop()
		self._enable()

		direction = _FORWARD if N > 0 else _BACKWARD # Set direction based on sign of N
		self.gpio.write(self._pin_config['DIR'],direction)
		self.gpio.set_PWM_frequency(self._pin_config['STEP'],_SPEED)

		delta_t = float(abs(N))/_SPEED
		
		# Some error associated with doing this. _start + _stop takes average 1.8 ms max 4.5 ms on 10k trials
		# This leads to potential max error of 5% of a mm per move. theoretically 0% average error over long period using correction -1.8ms
		# might need to make pulse function. or we just don't care. 
		self._start()
		time.sleep(delta_t - 0.0018)
		self._stop()

		self._disable()
		self.position += N # update position
		print('successfully moved %d steps' %N)
		return

	def _move_to_step(self, step):
		
		if step == self.position:
			print('_move_to_step: already in position')
			return
		if not (_MIN_STEPS <= step <= _MAX_STEPS):
			print('_move_steps: commanded step %d is out of bounds. thresholding' % step)
			step = min(step,_MAX_STEPS)
			step = max(step,_MIN_STEPS) 

		delta_N = step - self.position
		self._move_steps(delta_N)
		return

	def movetoPosition(self,d):
		# d in mm

		step = int((d/_DISTANCE_PER_REV)*_STEPS_PER_REV) # int() is a floor
		self._move_to_step(step)
		return

		





if __name__=='__main__':
	pi = pigpio.pi()
	motor = ROB12859(pi, _DEFAULT_PIN_CONFIG)



