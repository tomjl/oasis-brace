import numpy as np 
from classify import SimpleMotionClassifier
from queue import Queue
import time
import matplotlib.pyplot as plt

test_data = np.loadtxt('walkstairwalkstair3.csv',delimiter=',',dtype=np.float32)

classifier = SimpleMotionClassifier()

N = test_data.shape[0]
states = np.zeros((N,3))
for i,row in enumerate(test_data):
	t = i*0.15
	imu1 = {0: row[3:6]}
	imu2 = {0: row[9:12]}
	sample = (t,imu1,imu2)

	t0 = time.time()
	classifier.addSample(sample)
	states[i]=[t,classifier.getState()=='stairs',row[3]-row[9]]
	print(time.time()-t0) #operations take order 1e-5 seconds


fig, axs = plt.subplots(2,sharex=True)
axs[1].plot(states[:,0],states[:,1])
axs[0].plot(states[:,0],states[:,2])
plt.show()