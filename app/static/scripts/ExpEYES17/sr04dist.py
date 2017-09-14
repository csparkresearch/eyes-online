import sys, time, utils, math

if utils.PQT5 == True:
	from PyQt5.QtCore import Qt, QTimer
	from PyQt5.QtWidgets import QApplication,QWidget, QLabel, QHBoxLayout, QVBoxLayout,\
	QCheckBox, QPushButton 
	from PyQt5.QtGui import QPalette, QColor
else:
	from PyQt4.QtCore import Qt, QTimer
	from PyQt4.QtGui import QPalette, QColor, QApplication, QWidget,\
	QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QCheckBox
	
import pyqtgraph as pg
import numpy as np
import eyes17.eyemath17 as em


class Expt(QWidget):
	TIMER = 20
	RPWIDTH = 300
	RPGAP = 4
	running = False
	
	TMIN = 0
	TMAX = 5
	DMIN = 0
	DMAX = 80
	DLIMIT = 80
	guessTP = 1.0     #time period guess
	data = [ [], [] ]
	currentTrace = None
	traces = []
	history = []		# Data store	
	sources = ['A1','A2','A3', 'MIC']
	pencol = 2
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 
		
		self.pwin = pg.PlotWidget()							# pyqtgraph window
		self.pwin.showGrid(x=True, y=True)					# with grid
		ax = self.pwin.getAxis('bottom')
		ax.setLabel('Time (Sec)')	
		ax = self.pwin.getAxis('left')
		ax.setLabel('Distance(cm)')
		self.pwin.disableAutoRange()
		self.pwin.setXRange(self.TMIN, self.TMAX)
		self.pwin.setYRange(self.DMIN, self.DMAX)
		self.pwin.hideButtons()								# Do not show the 'A' button of pg

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignTop)
		right.setSpacing(self.RPGAP)
					
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Y-axis from 0 to'))
		l.setMaximumWidth(100)
		H.addWidget(l)
		self.DMAXtext = utils.lineEdit(40, self.DMAX, 6, None)
		H.addWidget(self.DMAXtext)
		l = QLabel(text=self.tr('cm'))
		l.setMaximumWidth(50)
		H.addWidget(l)
		right.addLayout(H)

		
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Measure during'))
		l.setMaximumWidth(100)
		H.addWidget(l)
		self.TMAXtext = utils.lineEdit(40, self.TMAX, 6, None)
		H.addWidget(self.TMAXtext)
		l = QLabel(text=self.tr('Secs'))
		l.setMaximumWidth(50)
		H.addWidget(l)
		right.addLayout(H)
		
		b = QPushButton(self.tr("Start"))
		right.addWidget(b)
		b.clicked.connect(self.start)		
		
		b = QPushButton(self.tr("Stop"))
		right.addWidget(b)
		b.clicked.connect(self.stop)		
		
		b = QPushButton(self.tr("Fit Curve using Sine"))
		b.clicked.connect(self.fit_curve)		
		right.addWidget(b)
		
		b = QPushButton(self.tr("Clear Traces"))
		right.addWidget(b)
		b.clicked.connect(self.clear)		

		H = QHBoxLayout()
		self.SaveButton = QPushButton(self.tr("Save to"))
		self.SaveButton.setMaximumWidth(90)
		self.SaveButton.clicked.connect(self.save_data)		
		H.addWidget(self.SaveButton)
		self.Filename = utils.lineEdit(150, 'sr04-data.txt', 20, None)
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

	
	def fit_curve(self):
		if self.history != []:
			x = self.history[-1][0]
			y = self.history[-1][1]
			if len(x) % 2 != 0:
				x = x[:-1]
				y = y[:-1]
			fa = em.fit_dsine(np.array(x), np.array(y), 1000)# ./self.guessTP)  #Need to fix eyemath, expects kHz
		else:
			self.msg('No data to analyze.')
			return
			
		if fa != None:
			pa = fa[1]
			self.msg('Sine Fit Result: Frequency = %5.2f Hz'%(pa[1]))
			self.traces.append(self.pwin.plot(x, fa[0], pen = 'w'))
		else:
			self.msg('Failed to fit the curve')
		
				
	def update(self):
		if self.running == False:
			return
			
		try:
			t,D = self.p.sr04_distance_time()  # SR04 measurement
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
			return
			
		if len(self.data[0]) == 0:
			self.start_time = t
			elapsed = 0
		else:
			elapsed = t - self.start_time

		self.data[0].append(elapsed)
		self.data[1].append(D)
		if elapsed > self.TMAX:
			self.running = False
			self.history.append(self.data)
			self.traces.append(self.currentTrace)
			self.msg('Time vs Distance plot completed')
			return
		if self.index > 1:			  # Draw the line
			self.currentTrace.setData(self.data[0], self.data[1])
		self.index += 1


	def start(self):
		if self.running == True: return
		if self.p == None:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
			return
		try:
			self.TMAX = float(self.TMAXtext.text())
		except:
			self.msg('Invalid Duration')
			return
		try:
			val = float(self.DMAXtext.text())
			if 5 < val <= self.DLIMIT:
				self.DMAX = val
			else:
				self.msg('Set maximum distance between 5cm and %d cm'%self.DLIMIT)	
				return			
		except:
			self.msg('Invalid Maximum Distance')
			return

		self.pwin.setXRange(self.TMIN, self.TMAX)
		self.pwin.setYRange(self.DMIN, self.DMAX)
		self.running = True
		self.data = [ [], [] ]
		self.currentTrace = self.pwin.plot([0,0],[0,0], pen = self.pencol)
		self.index = 0
		self.pencol += 2
		self.msg('Started Measurements')

	def stop(self):
		if self.running == False: return
		self.running = False
		self.history.append(self.data)
		self.traces.append(self.currentTrace)
		self.msg('User Stopped')

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
	
