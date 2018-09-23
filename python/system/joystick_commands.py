from sense_hat import SenseHat
from time import sleep
import os
import subprocess

# Constants
SPEED = 0.02


O=[0,0,0]
X=[255,0,0]

connector = [
O, O, O, O, O, O, O, O,
O, O, X, O, X, O, O, O,
O, O, X, O, X, O, O, O,
O, X, X, X, X, X, O, O,
O, X, O, O, O, X, O, O,
O, X, O, O, O, X, O, O,
O, O, X, X, X, O, O, O,
O, O, O, X, O, O, O, O
]

# Commands definition

sense = SenseHat()
#sense.set_rotation(180)

def shutdown():
	'''
	Shuts down Raspberry Pi
	'''
	sense.show_message('Shutting down...', scroll_speed=SPEED, text_colour=[255,0,0])
	sense.set_pixels(connector)
	os.system('sudo shutdown now')
	return

def matrixOff():
	'''
	Turns off LED matrix.
	'''
	sense.show_message('Screen off', scroll_speed=SPEED)
	sense.clear()
	return

def backupPhotos():
	'''
	Calls the photo backup script.
	'''
	subprocess.call(['python3', '/home/pi/scripts/photos/backup_photos-hat.py'])
	return


# Dictionary holding info to be executed in a list:
# a) Direction.
# b) Times pressed.
# c) Function name
operations = {
	'shutdown': ['down', 3, shutdown],
	'matrixOff': ['up', 2, matrixOff],
	'backupPhotos': ['right', 2, backupPhotos]
}

# ALL counters should be initialized here.
# Keep in mind when adding more commands.
counters = {
	'shutdown': 1,
	'matrixOff': 1,
	'backupPhotos': 1
}



while True:

	# "emptybuffer=True" so that the first movement after waiting for an event (i.e. pressed),
	# will be recorded instead of the "released" that might have been recorded in the
	# previous iteration.
	event = sense.stick.wait_for_event(emptybuffer=True)
	sleep(0.2)


	print("The joystick was {} {}".format(event.action, event.direction))

	for operation,value in operations.items():

		
		if (event.direction == value[0]) and (event.action == 'pressed'):


			if counters[operation] == value[1]: # number of times the key should be **consecutively** pressed.
				
				counters[operation] = 1
				value[2]() #'()' Executes the function in the list.
				
			else:
				counters[operation] += 1


		else:

			counters[operation] = 1
