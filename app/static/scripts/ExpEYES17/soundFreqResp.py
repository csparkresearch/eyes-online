import sys, time, utils, math

if utils.PQT5 == True:
	from PyQt5.QtCore import Qt, QTimer
	from PyQt5.QtWidgets import QApplication,QWidget, QLabel, QHBoxLayout,\
	QCheckBox, QVBoxLayout, QPushButton 
	from PyQt5.QtGui import QPalette, QColor
else:
	from PyQt4.QtCore import Qt, QTimer
	from PyQt4.QtGui import QPalette, QColor, QApplication, QWidget,\
	QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QCheckBox
	
import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em


class Expt(QWidget):
	MINTIMER = 85
	TIMER = MINTIMER
	RPWIDTH = 300
	RPGAP = 4
	running = False
	AWGmin = 1
	AWGmax = 5000
	AWGval = 1000
	
	FMIN = 1000
	FMAX = 4000
	FREQ = FMIN
	STEP = 20         
	VMIN = 0		# filter amplitude Gain
	VMAX = 4.0
	data = [ [], [] ]
	currentTrace = None
	traces = []
	history = []		# Data store	
	sources = ['A1','A2','A3', 'MIC']
	pencol = 2
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device								# connection to the device hardware 
		try:
			self.p.configure_trigger(0, 'A1', 0)
			self.p.select_range('A1',4.0)
		except:
			pass
			
		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel('Frequency (Hz)')	
		ax = self.pwin.getAxis('left')
		ax.setLabel('Amplitude (V)')
		self.pwin.disableAutoRange()
		self.pwin.setXRange(self.FMIN, self.FMAX)
		self.pwin.setYRange(self.VMIN, self.VMAX)
		self.pwin.hideButtons()								# Do not show the 'A' button of pg

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignTop)
		right.setSpacing(self.RPGAP)
		 
		H = QHBoxLayout()
		l = QLabel(text=self.tr('From'))
		l.setMaximumWidth(35)
		H.addWidget(l)
		self.AWGstart = utils.lineEdit(60, self.FMIN, 6, None)
		H.addWidget(self.AWGstart)
		l = QLabel(text=self.tr('to'))
		l.setMaximumWidth(20)
		H.addWidget(l)
		self.AWGstop = utils.lineEdit(60, self.FMAX, 6, None)
		H.addWidget(self.AWGstop)
		l = QLabel(text=self.tr('Hz'))
		l.setMaximumWidth(20)
		H.addWidget(l)
		right.addLayout(H)
		 
		H = QHBoxLayout()
		l = QLabel(text=self.tr('in'))
		l.setMaximumWidth(20)
		H.addWidget(l)
		self.totalTimeW = utils.lineEdit(60, 20, 6, None)
		H.addWidget(self.totalTimeW)
		l = QLabel(text=self.tr('seconds'))
		l.setMaximumWidth(20)
		H.addWidget(l)
		right.addLayout(H)

		b = QPushButton(self.tr("Start"))
		right.addWidget(b)
		b.clicked.connect(self.start)		
		
		H = QHBoxLayout()
		self.updateLabel = QLabel(text=self.tr(''))
		self.updateLabel.setMaximumWidth(200)
		H.addWidget(self.updateLabel)
		right.addLayout(H)

		b = QPushButton(self.tr("Stop"))
		right.addWidget(b)
		b.clicked.connect(self.stop)		
		
		b = QPushButton(self.tr("Clear Traces"))
		right.addWidget(b)
		b.clicked.connect(self.clear)		

		H = QHBoxLayout()
		self.SaveButton = QPushButton(self.tr("Save Data to"))
		self.SaveButton.setMaximumWidth(90)
		self.SaveButton.clicked.connect(self.save_data)		
		H.addWidget(self.SaveButton)
		self.Filename = utils.lineEdit(150, 'Piezo-freq-resp.txt', 20, None)
		H.addWidget(self.Filename)
		right.addLayout(H)

		#------------------------end of right panel ----------------
		
		top = QHBoxLayout()
		top.addWidget(self.pwin)
		top.addLayout(right)
		
		full = QVBoxLayout()
		full.addLayout(top)
		self.msgwin = QLabel(text=self.tr(''))
		full.addWidget(self.msgwin)
				
		self.setLayout(full)
		
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(self.TIMER)
		

		#----------------------------- end of init ---------------
		

	def verify_fit(self,y,y1):
		sum = 0.0
		for k in range(len(y)):
			sum += abs((y[k] - y1[k])/y[k])
		err = sum/len(y)
		if err/sum > 0.01:
			return False
		else:
			return True
				
	def update(self):
		if self.running == False:
			return
						
		try:	
			fr=self.p.set_sine(self.FREQ)
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
			return
		time.sleep(0.02)	
		TG = 1.e6/self.FREQ/50   # 50 points per wave
		TG = int(TG)//2 * 2
		if TG > 500:
			TG = 500
		elif TG < 2:
			TG = 2
		NP = 500
		MAXTIME = 200000.  # .2 seconds
		if NP * TG > MAXTIME:
			NP = int(MAXTIME/TG)
		if NP % 2: NP += 1  # make it an even number
		
		goodFit = False
		for k in range(3):                  # try 3 times
			try:
				t,v   = self.p.capture1('MIC', NP, TG)	
			except:
				print 'Err'
				self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')
				return		
			fa = em.fit_sine(t,v)
			if fa != None:
				if self.verify_fit(v,fa[0]) == False:        #compare trace with the fitted curve
					continue
				self.updateLabel.setText('Frequency = %5.0f Hz V = %5.3f'%(fr,abs(fa[1][0])))
				self.data[0].append(fr)
				self.data[1].append(abs(fa[1][0]))
				goodFit = True
				break
		
		self.FREQ += self.STEP
		if goodFit == False:
			return

		if self.FREQ > self.FMAX:
			self.running = False
			elapsed = time.time() - self.startTime
			
			self.history.append(self.data)
			self.traces.append(self.currentTrace)
			try:
				self.p.set_sine(0)
				self.msg('Completed in %5.1f Seconds'%elapsed)
			except:
				self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
			return

		if self.index > 1:			  # Draw the line
			self.currentTrace.setData(self.data[0], self.data[1])
		self.index += 1


	def start(self):
		if self.running == True: return
		try:
			self.p.select_range('A1',4)
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
			return
		try:
			self.FMIN = float(self.AWGstart.text())
			self.FMAX = float(self.AWGstop.text())
		except:
			self.msg('Invalid Frequency limis')
			return
			
		try:
			self.totalTime = float(self.totalTimeW.text())
		except:
			self.msg('Invalid Time interval')
			return

		nstep = (self.FMAX - self.FMIN)/self.STEP
		tgap = self.totalTime*1000/nstep
		mt = nstep * self.MINTIMER /1000 + 1
		print tgap, mt
		
		if tgap > self.MINTIMER:
			self.TIMER = tgap	
			self.timer.stop()
			self.timer.start(self.TIMER)
		else:
			self.msg('Increase time interval to %4.0f, or Reduce frequency span'%mt)
			return
			
		self.pwin.setXRange(self.FMIN, self.FMAX)
		self.pwin.setYRange(self.VMIN, self.VMAX)
		self.running = True
		self.data = [ [], [] ]
		self.FREQ = self.FMIN
		self.currentTrace = self.pwin.plot([0,0],[0,0], pen = self.pencol)
		self.index = 0
		self.pencol += 2
		self.msg('From %5.0f to %5.0f Hz. %5.0f mS at each step'%(self.FMIN, self.FMAX,tgap))

		self.startTime = time.time()


	def stop(self):
		if self.running == False: return
		self.running = False
		self.history.append(self.data)
		self.traces.append(self.currentTrace)
		self.msg('User Stopped')
		try:
			self.p.set_sine(0)
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		

	def clear(self):
		for k in self.traces:
			self.pwin.removeItem(k)
		self.history = []
		self.pencol = 2
		self.msg('Cleared Completed Traces and Data')
		
	def save_data(self):
		if self.history == []:
			self.msg('No Traces available for saving')
			return
		fn = self.Filename.text()
		self.p.save(self.history, fn)
		self.msg('Traces saved to %s'%fn)
		
	def msg(self, m):
		self.msgwin.setText(self.tr(m))
		

if __name__ == '__main__':
	import eyes17.eyes
	dev = eyes17.eyes.open()
	app = QApplication(sys.argv)
	mw = Expt(dev)
	mw.show()
	sys.exit(app.exec_())
	
