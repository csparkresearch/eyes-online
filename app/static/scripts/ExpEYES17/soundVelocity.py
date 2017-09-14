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
	AWGmin = 1
	AWGmax = 5000
	AWGval = 3500

	tbvals = [0.100, 0.200, 0.500]	# allowed mS/div values
	NP = 500			# Number of samples
	TG = 1				# Number of channels
	MINDEL = 1			# minimum time between samples, in usecs
	MAXDEL = 1000
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

	NP = 500			# Number of samples
	TG = 1				# Number of channels
	
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
		self.SaveButton = QPushButton(self.tr("Save Data to"))
		self.SaveButton.setMaximumWidth(90)
		self.SaveButton.clicked.connect(self.save_data)		
		H.addWidget(self.SaveButton)
		self.Filename = utils.lineEdit(150, 'sound-velocity.txt', 20, None )
		H.addWidget(self.Filename)
		right.addLayout(H)

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
		l = QLabel(text=self.tr('Timebase'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		self.TBslider = utils.slider(0, len(self.tbvals)-1, self.TBval, 150, self.set_timebase)
		H.addWidget(self.TBslider)
		l = QLabel(text=self.tr('mS/div'))
		l.setMaximumWidth(60)
		H.addWidget(l)
		right.addLayout(H)

		self.enable = QCheckBox('Enable Measurements')
		right.addWidget(self.enable)
		self.enable.stateChanged.connect(self.control)

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
	
	def control(self):
		try:	
			if self.enable.isChecked() == False:
				self.p.set_sine(0)
			else:
				self.p.set_sine(self.AWGval)
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
			return
			
	def update(self):
		if self.enable.isChecked() == False:
			return
		try:
			tvs = self.p.capture4(self.NP, self.TG)
			self.timeData[0] = tvs[0]
			self.voltData[0] = tvs[1]
			self.timeData[1] = tvs[6]   # MIC channel
			self.voltData[1] = -tvs[7]			
			for ch in range(self.MAXCHAN):
				self.traceWidget[ch].setData(self.timeData[ch], self.voltData[ch])		
			self.measured = True
			
			fa = em.fit_sine(self.timeData[0], self.voltData[0])
			if fa != None:	
				fb = em.fit_sine(self.timeData[1], self.voltData[1])
				pa = fa[1][2] * 180/em.pi
				pb = fb[1][2] * 180/em.pi
				pdiff = pa-pb
				if fb[1][0] < 0: pdiff = 180 - pdiff
				self.Res.setText('Phase Shift = %5.1f deg'%(pdiff))
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')			
	
	def save_data(self):
		if self.measured == False: 
			return
		fn = self.Filename.text()
		dat = []
		for ch in range(2):
				dat.append( [self.timeData[ch], self.voltData[ch] ])
		self.p.save(dat,fn)
		self.msg('Traces saved to %s'%fn)
			
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

	def set_wave(self):
		try:	
			res = self.p.set_sine(self.AWGval)
			self.msg('AWG set to %6.2f Hz'%res)
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
			return

	def awg_text(self, text):
		val = float(text)
		if self.AWGmin <= val <= self.AWGmax:
			self.AWGval = val
			self.AWGslider.setValue(self.AWGval)
			self.set_wave()

	def awg_slider(self, val):
		if self.AWGmin <= val <= self.AWGmax:
			self.AWGval = val
			self.AWGtext.setText(str(val))
			self.set_wave()
		
	def msg(self, m):
		self.msgwin.setText(self.tr(m))
		

if __name__ == '__main__':
	import eyes17.eyes
	dev = eyes17.eyes.open()
	app = QApplication(sys.argv)
	mw = Expt(dev)
	mw.show()
	sys.exit(app.exec_())
	
