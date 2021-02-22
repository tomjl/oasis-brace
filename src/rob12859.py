import pigpio
import time

_STEPS_PER_REV 	  = 200
_DISTANCE_PER_REV = 2 # 2mm 


_FULL_STEP = {
			'ticks_per_step': 1,
			'pins': (0,0,0)
}
_HALF_STEP = {
			'ticks_per_step': 2,
			'pins': (1,0,0)
}
_QUARTER_STEP = {
			'ticks_per_step': 4,
			'pins': (0,1,0)
}
_EIGHTH_STEP = {
			'ticks_per_step': 8,
			'pins': (1,1,0)
}
_SIXTEENTH_STEP = {
			'ticks_per_step': 16,
			'pins': (1,1,1)
}

_FORWARD  = 1
_BACKWARD = 0

_MOTOR_ON  = 0
_MOTOR_OFF = 1

_MAX_DISTANCE = 10 # 10 mm
_MIN_DISTANCE = 0  # 0 mm

_SPEED = 8000 # PWM speed in Hz


"""
TODO:
2 Objects: 
- ROB12859 handles single moves
- BraceMotors handles position tracking and macro moves

NOTE: redefine move units as ticks (1/16 STEP) to avoid confusion with steps
"""

_PIN_CONFIG_1 = {
	'STEP':   12,
	'DIR':	  17,
	'MS1': 	  27,
	'MS2':	  22,
	'MS3':	  23,
	'ENABLE': 24
}

_PIN_CONFIG_2 = {
	'STEP':   13,
	'DIR':	  10,
	'MS1': 	   9,
	'MS2':	  11,
	'MS3':	  25,
	'ENABLE':  8
}

class ROB12859:
	'''
	pi = pigpio.pi()
	motor = ROB12859(pi, _PIN_CONFIG_1)
	motor.setDirection(_FORWARD)
	motor.moveStep()
	'''
	def __init__(self, gpio, pin_config):
		self._pin_config = pin_config
		self.gpio  		 = gpio
		self.stepsize 	 = _EIGHTH_STEP
		self.DIR 		 = _FORWARD
		self.speed 		 = _SPEED
		self._initialize_driver()

	def _initialize_driver(self):
		self._disable()
		self._stop()
		self._write_stepsize()
		self._write_direction()
		self._write_speed()
		self._enable()

	def _stop(self):
		self.gpio.set_PWM_dutycycle(self._pin_config['STEP'],0)

	def _start(self):
		self.gpio.set_PWM_dutycycle(self._pin_config['STEP'],128) # 50% duty cycle

	def _write_stepsize(self):
		self.gpio.write(self._pin_config['MS1'],self.stepsize['pins'][0])
		self.gpio.write(self._pin_config['MS2'],self.stepsize['pins'][1])
		self.gpio.write(self._pin_config['MS3'],self.stepsize['pins'][2])

	def _write_direction(self):
		self.gpio.write(self._pin_config['DIR'],self.DIR)

	def _write_speed(self):
		self.gpio.set_PWM_frequency(self._pin_config['STEP'], self.speed)

	def _enable(self):
		self.gpio.write(self._pin_config['ENABLE'],_MOTOR_ON)

	def _disable(self):
		self.gpio.write(self._pin_config['ENABLE'],_MOTOR_OFF)

	def setStepSize(self,stepsize):
		'''
		User facing. 
		Can be called mid-operation to change step size.
		'''
		self.stepsize = stepsize
		self._write_stepsize() # write step size to GPIO pins

	def setDirection(self,direction):
		self.DIR = direction
		self._write_direction()

	def setSpeed(self,speed):
		self.speed = speed
		self._write_speed()

	def moveStep(self):
		# NOTE: this function is unsafe by itself. doesn't keep track of where the motor is. position tracking is higher up
		self.gpio.write(self._pin_config['STEP'],1)
		self.gpio.write(self._pin_config['STEP'],0)
		

# TODO make start/stop method here for when thing errors out/ is cancelled

class BraceMotors:
	'''
	handles moving motors simultaneously.
	why does this exist? if we thread motors separately we aren't guaranteeing they move at same time. might break someone's knee :)
	this also dissalows busy wait moves. 

	FOR NOW we'll just assume one distance (uniform deloading), but this structure can be easily updated to do differential unloading as well
	'''
	def __init__(self, motor1, motor2):
		assert motor1.stepsize == motor2.stepsize # could also have this class init the motors but that's a little messier
		assert motor1.speed == motor2.speed

		self.pos = 0 # position in ticks
		self.M1 = motor1
		self.M2 = motor2
		self.speed = motor1.speed
		
		self.ticks_per_mm = motor1.stepsize['ticks_per_step']*_STEPS_PER_REV/_DISTANCE_PER_REV

	def setSpeed(self,speed):
		self.M1.setSpeed(speed)
		self.M2.setSpeed(speed)
		self.speed = speed
		return

	def _mm_to_ticks(self,d):
		return(int(self.ticks_per_mm*d)) # int() is a floor

	def _in_range(self,d):
		return (_MIN_DISTANCE <= d <= _MAX_DISTANCE)

	def _move_ticks_BB(self, dticks, direction):
		# do the ticks manually
		# No thread suspension so will be less efficient but more accurate
		# Not currently in use
		delay = 0.001
		self.M1.setDirection(direction)
		self.M2.setDirection(direction)

		for i in range(dticks):
			self.M1.moveStep()
			self.M2.moveStep()	
			time.sleep(delay)
		return


	def _move_ticks_delay(self, dticks, direction):
		delta_t  = float(dticks)/self.speed 

		self.M1.setDirection(direction)
		self.M2.setDirection(direction)

		# Some error associated with doing this. _start + _stop takes average 1.8 ms max 4.5 ms on 10k trials
		# This leads to potential max error of 5% of a mm per move. theoretically 0% average error over long period using correction -1.8ms
		# might need to make pulse function. or we just don't care. 

		t0 = time.time()
		self.M1._start()
		self.M2._start()
		time.sleep(delta_t - 0.0018)
		self.M1._stop()
		self.M2._stop()
		print(time.time()-t0)

		return

	def movetoPosition(self, d):

		if not self._in_range(d):
			print('setPosition(): Commanded position %.1f is out of range [%d, %d]. No distance moved.' %(d, _MIN_DISTANCE, _MAX_DISTANCE))
			return
		# convert from mm to ticks
		new_pos = self._mm_to_ticks(d)

		if new_pos == self.pos: # could be a threshold
			print('setPosition(): Already in commanded position')
			return

		# get motor commands
		dticks = abs(new_pos-self.pos)
		direction = _FORWARD if new_pos >= self.pos else _BACKWARD

		# move specified number of ticks 
		self._move_ticks_delay(dticks, direction)

		self.pos = new_pos # update current position
		print('Successfully moved to %.1f mm' %d)



if __name__=='__main__':
	pi = pigpio.pi()

	motor1 = ROB12859(pi, _PIN_CONFIG_1)
	motor2 = ROB12859(pi, _PIN_CONFIG_2)

	motors = BraceMotors(motor1, motor2)



