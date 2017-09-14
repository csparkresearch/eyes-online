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
	AWGmin = 100
	AWGmax = 5000
	AWGval = 3500
	SQ1min = 100
	SQ1max = 5000
	SQ1val = 3600
	

	tbvals = [0.100, 0.200, 0.500, 1.0, 2.0, 5.0, 10.0, 20.0]	# allowed mS/div values
	NP = 4000			# Number of samples
	TG = 2				# Number of channels
	MINDEL = 1			# minimum time between samples, in usecs
	MAXDEL = 50
	delay = MINDEL		# Time interval between samples
	TBval = 1			# timebase list index
	
	TMAX = 1
	VMIN = -5
	VMAX = 5
	MAXCHAN = 2
	timeData    = [None]*MAXCHAN
	voltData    = [None]*MAXCHAN
	voltDataFit = [None]*MAXCHAN
	traceWidget = [None]*MAXCHAN
	traceWidget = [None]*MAXCHAN
	#history = []		# Data store	
	measured = False
	sources = ['A1','A2','A3', 'MIC']
	chanpens = ['y','g','w','m']     #pqtgraph pen colors

	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 

		try:
			self.p.configure_trigger(0, 'A1', 0)
			self.p.select_range('A1',4.0)
			self.p.set_sine(0)
		except:
			pass	
		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel('Time (mS)')	
		ax = self.pwin.getAxis('left')
		ax.setLabel('Voltage')
		self.pwin.disableAutoRange()
		self.pwin.setXRange(0, self.TMAX)
		self.pwin.setYRange(self.VMIN, self.VMAX)
		self.pwin.hideButtons()								# Do not show the 'A' button of pg

		for ch in range(self.MAXCHAN):							# initialize the pg trace widgets
			self.traceWidget[ch] = self.pwin.plot([0,0],[0,0], pen = self.chanpens[ch])

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignTop)
		right.setSpacing(self.RPGAP)				


		H = QHBoxLayout()
		l = QLabel(text=self.tr('WG'))
		l.setMaximumWidth(25)
		H.addWidget(l)
		self.AWGslider = utils.slider(self.AWGmin, self.AWGmax, self.AWGval,100,self.awg_slider)
		H.addWidget(self.AWGslider)
		self.AWGtext = utils.lineEdit(100, self.AWGval, 6, self.awg_text)
		H.addWidget(self.AWGtext)
		l = QLabel(text=self.tr('Hz'))
		l.setMaximumWidth(20)
		H.addWidget(l)
		right.addLayout(H)
		
		H = QHBoxLayout()
		l = QLabel(text=self.tr('SQ1'))
		l.setMaximumWidth(25)
		H.addWidget(l)
		self.SQ1slider = utils.slider(self.SQ1min, self.SQ1max, self.SQ1val,100,self.sq1_slider)
		H.addWidget(self.SQ1slider)
		self.SQ1text = utils.lineEdit(100, self.SQ1val, 6, self.sq1_text)
		H.addWidget(self.SQ1text)
		l = QLabel(text=self.tr('Hz'))
		l.setMaximumWidth(20)
		H.addWidget(l)
		right.addLayout(H)	

		l = QLabel(text=self.tr('Change of Freqency effected\nonly after Enable/Disable controls.\n\
shows the actual frequency set.\n'))
		right.addWidget(l)	

		self.AWG = QCheckBox('Enable WG')
		right.addWidget(self.AWG)
		self.AWG.stateChanged.connect(self.control)

		self.SQ1 = QCheckBox('Enable SQ1')
		right.addWidget(self.SQ1)
		self.SQ1.stateChanged.connect(self.control)

		self.enable = QCheckBox('Enable Measurements')
		right.addWidget(self.enable)
		self.enable.stateChanged.connect(self.control)

		H = QHBoxLayout()
		l = QLabel(text=self.tr('Timebase'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		self.TBslider = utils.slider(0, len(self.tbvals)-1, self.TBval, 150, self.set_timebase)
		H.addWidget(self.TBslider)
		l = QLabel(text=self.tr('mS/div'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		right.addLayout(H)

		H = QHBoxLayout()
		self.SaveButton = QPushButton(self.tr("Save Data to"))
		self.SaveButton.setMaximumWidth(90)
		self.SaveButton.clicked.connect(self.save_data)		
		H.addWidget(self.SaveButton)
		self.Filename = utils.lineEdit(150, 'sound-beats.txt', 20, None)
		H.addWidget(self.Filename)
		right.addLayout(H)

		self.FFT = QPushButton(self.tr("Frequency Spectrum"))
		right.addWidget(self.FFT)
		self.FFT.clicked.connect(self.show_fft)		


		H = QHBoxLayout()
		self.Res = QLabel(text=self.tr(''))
		#Res.setMaximumWidth(60)
		H.addWidget(self.Res)
		right.addLayout(H)
		
		#------------------------end of right panel ----------------
		
		top = QHBoxLayout()
		top.addWidget(self.pwin)
		top.addLayout(right)
		
		full = QVBoxLayout()
		full.addLayout(top)
		self.msgwin = QLabel(text=self.tr('messages'))
		full.addWidget(self.msgwin)
				
		self.setLayout(full)
		
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(self.TIMER)
		

		#----------------------------- end of init ---------------
	
	def show_fft(self):
		self.popwin = pg.PlotWidget()				# pyqtgraph window
		self.popwin.showGrid(x=True, y=True)						# with grid
		self.popwin.setWindowTitle('Frequency Spectrum')
		try:
			xa,ya = em.fft(self.voltData[0], self.timeData[0][1]-self.timeData[0][0])
			self.popwin.plot(xa*1000,ya, pen = 'w')					
		except:
			self.msg('FFT err')
		self.popwin.show()

	def control(self):
		try:
			if self.enable.isChecked() == False:
				self.p.set_sine(0)
				self.p.set_sqr1(0)
			else:
				if self.AWG.isChecked() == True:
					fr = self.p.set_sine(self.AWGval)
					self.AWGtext.setText('%5.2f'%fr)
				else:
					self.p.set_sine(0)				
				if self.SQ1.isChecked() == True:
					fr = self.p.set_sqr1(self.SQ1val)
					self.SQ1text.setText('%5.2f'%fr)
				else:
					self.p.set_sqr1(0)
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
				
	def update(self):
		if self.enable.isChecked() == False:
			return
		try:
			self.timeData[0], self.voltData[0] = self.p.capture1('MIC', self.NP, self.TG)
			self.traceWidget[0].setData(self.timeData[0], self.voltData[0])	
			self.measured = True 	
		except:
			self.msg('<font color="red">Capture or fit Error, Try reconnect')		

	def save_data(self):
		if self.measured == False: 
			return
		fn = self.Filename.text()
		dat = []
		for ch in range(1):
				dat.append( [self.timeData[ch], self.voltData[ch] ])
		self.p.save(dat,fn)
		self.msg('Trace saved to %s'%fn)
			
	def set_timebase(self, tb):
		self.TBval = tb
		self.pwin.setXRange(0, self.tbvals[self.TBval]*10)
		msperdiv = self.tbvals[int(tb)]				#millisecs / division
		totalusec = msperdiv * 1000 * 10.0  	# total 10 divisions
		self.TG = int(totalusec/self.NP)
		if self.TG < self.MINDEL:
			self.TG = self.MINDEL
		elif self.TG > self.MAXDEL:
			self.TG = self.MAXDEL

	def sq1_text(self, text):
		try:
			val = float(text)
		except:
			return
		if self.SQ1min <= val <= self.SQ1max:
			self.SQ1val = val
			self.SQ1slider.setValue(self.SQ1val)

	def sq1_slider(self, val):
		if self.SQ1min <= val <= self.SQ1max:
			self.SQ1val = val
			self.SQ1text.setText(str(val))

	def set_wave(self):
		try:
			res = self.p.set_sine(self.AWGval)
			self.msg('AWG set to %6.2f Hz'%res)
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		

	def awg_text(self, text):
		val = float(text)
		if self.AWGmin <= val <= self.AWGmax:
			self.AWGval = val
			self.AWGslider.setValue(self.AWGval)

	def awg_slider(self, val):
		if self.AWGmin <= val <= self.AWGmax:
			self.AWGval = val
			self.AWGtext.setText(str(val))
		
	def msg(self, m):
		self.msgwin.setText(self.tr(m))
		

if __name__ == '__main__':
	import eyes17.eyes
	dev = eyes17.eyes.open()
	app = QApplication(sys.argv)
	mw = Expt(dev)
	mw.show()
	sys.exit(app.exec_())
	
