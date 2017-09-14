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
	TIMER = 50
	RPWIDTH = 300
	RPGAP = 4
	running = False
	
	FMIN = 200
	FMAX = 4900
	FREQ = FMIN
	STEP = 10          # 10 hz
	GMIN = 0.0		# filter amplitude Gain
	GMAX = 3.0
	Rload = 560.0
	data = [ [], [] ]
	currentTrace = None
	traces = []
	history = []		# Data store	
	sources = ['A1','A2','A3', 'MIC']
	pencol = 2
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 
		try:
			self.p.select_range('A1',4.0)
			self.p.select_range('A2',4.0)	
			self.p.configure_trigger(0, 'A1', 0)
		except:
			pass	
		
		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel('Frequency (Hz)')	
		ax = self.pwin.getAxis('left')
		ax.setLabel('Amplitude Gain')
		self.pwin.disableAutoRange()
		self.pwin.setXRange(self.FMIN, self.FMAX)
		self.pwin.setYRange(self.GMIN, self.GMAX)
		self.pwin.hideButtons()								# Do not show the 'A' button of pg

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignTop)
		right.setSpacing(self.RPGAP)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('Rload ='))
		l.setMaximumWidth(50)
		H.addWidget(l)
		self.LoadRes = utils.lineEdit(60, self.Rload, 6, None)
		H.addWidget(self.LoadRes)
		l = QLabel(text=self.tr('Ohm'))
		l.setMaximumWidth(40)
		H.addWidget(l)
		right.addLayout(H)


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
		 
		b = QPushButton(self.tr("Start"))
		right.addWidget(b)
		b.clicked.connect(self.start)		
		
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
		self.Filename = utils.lineEdit(150, 'filter-data.txt', 20, None)
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
		if err > .5:
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
		NP = 500
		MAXTIME = 200000.  # .2 seconds
		if NP * TG > MAXTIME:
			NP = int(MAXTIME/TG)
		if NP % 2: NP += 1  # make it an even number
		self.msg('Frequency = %5.0f Hz'%fr)

		goodFit = False
		for k in range(3):                  # try 3 times
			try:
				t,v, tt,vv = self.p.capture2(NP, int(TG))	
			except:
				self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
				return 
		
			fa = em.fit_sine(t,v)
			if fa != None:
				if self.verify_fit(v,fa[0]) == False:        #compare trace with the fitted curve
					continue
				fb = em.fit_sine(tt,vv)
				if fb != None:
					if self.verify_fit(vv,fb[0]) == False:     
						continue
					self.data[0].append(fr)
					gain = abs(fb[1][0]) #/fa[1][0])
					self.data[1].append(gain)
					if self.gainMax < gain:
						self.gainMax = gain
						self.peakFreq = fr
					goodFit = True
					break
		
		self.FREQ += self.STEP
		if goodFit == False:
			return

		if self.FREQ > self.FMAX:
			self.running = False
			self.history.append(self.data)
			self.traces.append(self.currentTrace)
			im = self.gainMax/self.Rload * 1000
			self.msg('Completed. Peak voltage = %5.3f\t Peak Current %5.0fmA at %5.0f Hz.'%(self.gainMax,im,self.peakFreq))
			return

		if self.index > 1:			  # Draw the line
			self.currentTrace.setData(self.data[0], self.data[1])
		self.index += 1


	def start(self):
		if self.running == True: return
		
		try:
			self.FMIN = float(self.AWGstart.text())
			self.FMAX = float(self.AWGstop.text())
		except:
			self.msg('Invalid Frequency limis')
			return
		
		self.pwin.setXRange(self.FMIN, self.FMAX)
		self.pwin.setYRange(self.GMIN, self.GMAX)
		try:	
			self.p.select_range('A1',4)
			self.p.select_range('A2',4)
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
			return 
		
		self.running = True
		self.data = [ [], [] ]
		self.FREQ = self.FMIN
		self.currentTrace = self.pwin.plot([0,0],[0,0], pen = self.pencol)
		self.index = 0
		self.pencol += 2
		self.gainMax = 0.0
		self.msg('Started')


	def stop(self):
		if self.running == False: return
		self.running = False
		self.history.append(self.data)
		self.traces.append(self.currentTrace)
		im = self.gainMax/self.Rload * 1000
		self.msg('Stopped. Peak voltage = %5.3f\t Peak Current %5.0fmA at %5.0f Hz.'%(self.gainMax,im,self.peakFreq))

	def clear(self):
		for k in self.traces:
			self.pwin.removeItem(k)
		self.history = []
		self.pencol = 2
		self.msg('Cleared Traces and Data')
		
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
	
