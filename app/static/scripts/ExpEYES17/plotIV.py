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
	TIMER = 50
	RPWIDTH = 300
	RPGAP = 4
	running = False
	PV1min = -5.0
	PV1max = 5.0
	PV1val = 2.
	
	VLLIM = -5  # maximum limits
	VULIM = 5
	ILLIM = -5  # maximum limits
	IULIM =  5
	
	VMIN = -5.0
	VMAX =  5.0
	VSET = VMIN
	STEP = 0.050           # 50 mV
	Res = 1000
	IMIN = 5
	IMAX = 5
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
		ax.setLabel('Current through R (mA)')	
		ax = self.pwin.getAxis('left')
		ax.setLabel('Voltage across R(Volts)')
		self.pwin.disableAutoRange()
		self.IMIN = self.VMIN / self.Res
		self.IMAX = self.VMAX / self.Res
		self.pwin.setXRange(self.IMIN, self.IMAX)
		self.pwin.setYRange(self.VMIN, self.VMAX)
		self.pwin.hideButtons()								# Do not show the 'A' button of pg

		right = QVBoxLayout()							# right side vertical layout
		right.setAlignment(Qt.AlignTop)
		right.setSpacing(self.RPGAP)
					
		H = QHBoxLayout()
		l = QLabel(self.tr("R from A1 to Ground"))
		l.setMaximumWidth(160)
		H.addWidget(l)
		self.Rval = utils.lineEdit(50, self.Res, 10, None)
		H.addWidget(self.Rval)
		l = QLabel(self.tr("Ohm"))
		l.setMaximumWidth(20)
		H.addWidget(l)
		right.addLayout(H)

		
		H = QHBoxLayout()
		l = QLabel(self.tr("Sweep PV1 from"))
		l.setMaximumWidth(120)
		H.addWidget(l)
		self.PVmin = utils.lineEdit(40, self.VMIN, 10, None)
		H.addWidget(self.PVmin)
		l = QLabel(self.tr("to"))
		l.setMaximumWidth(20)
		H.addWidget(l)
		self.PVmax = utils.lineEdit(40, self.VMAX, 10, None)
		H.addWidget(self.PVmax)
		l = QLabel(self.tr("V"))
		l.setMaximumWidth(15)
		H.addWidget(l)
		right.addLayout(H)
		
		
		H = QHBoxLayout()		 
		b = QPushButton(self.tr("Start"))
		right.addWidget(b)
		b.clicked.connect(self.start)		
		
		b = QPushButton(self.tr("Stop"))
		right.addWidget(b)
		b.clicked.connect(self.stop)		
		
		b = QPushButton(self.tr("Analyze last Trace"))
		right.addWidget(b)
		b.clicked.connect(self.fit_curve)		

		b = QPushButton(self.tr("Clear Traces"))
		right.addWidget(b)
		b.clicked.connect(self.clear)		

		H = QHBoxLayout()
		self.SaveButton = QPushButton(self.tr("Save Data to"))
		self.SaveButton.setMaximumWidth(90)
		self.SaveButton.clicked.connect(self.save_data)		
		H.addWidget(self.SaveButton)
		self.Filename = utils.lineEdit(150, 'iv.txt', 20, None)
		H.addWidget(self.Filename)
		right.addLayout(H)

		self.Manual = QLabel(self.tr("Change Voltage"))
		right.addWidget(self.Manual)
		#l.setMaximumWidth(15)

		self.PV1slider = utils.slider(0, 30, 0, 250, self.pv1_slider)
		right.addWidget(self.PV1slider)

		H = QHBoxLayout()
		self.Voltage = QLabel(self.tr('Voltage = %5.3f'%self.PV1min))
		H.addWidget(self.Voltage)
		right.addLayout(H)

		H = QHBoxLayout()
		self.Current = QLabel(self.tr("Current = 0 mA"))
		H.addWidget(self.Current)
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
		
		
	def pv1_slider(self, pos):
		res = float(self.Rval.text())		# Reference register
		sval = float(pos)
		val = self.PV1min + pos*(self.PV1max-self.PV1min)/30
		self.p.set_pv1(val)
		a1 = self.p.get_voltage('A1')
		volt = val- a1
		self.Voltage.setText('Voltage = %5.3f V'%volt)
		i = a1/res *1000
		self.Current.setText('Current = %5.3f mA'%i)
	
	
	def fit_curve(self):
		if self.running == True or self.data[0]==[]:
			return
		x = self.data[0]
		data = self.data[1]
		xbar = np.mean(x)
		ybar = np.mean(data)
		b = np.sum(data*(x-xbar)) / np.sum(x*(x-xbar))
		a = ybar - xbar * b
		self.msg('Slope of the Line (dV/dI) = %5.0f'%(b*1000))
	
				
	def update(self):
		if self.running == False:
			return
		try:
			vs = self.p.set_pv1(self.VSET)	
			time.sleep(0.001)	
			va = self.p.get_voltage('A1')		# voltage across the diode
		except:
			self.msg('<font color="red">Communication Error. Try Reconnect from the Device menu')		
			return 
		
		i = va/self.Res * 1000 		   # in mA
		vr = vs-va
		if i == i and vr == vr and abs(vr) > 0.04:   # Reject NaN and very small values
			self.data[0].append(i)
			self.data[1].append(vs-va)
		
		self.VSET += self.STEP
		if self.VSET > self.VMAX:
			self.running = False
			self.history.append(self.data)
			self.traces.append(self.currentTrace)
			self.fit_curve()
			self.manual()
			return
		if self.index > 1:			  # Draw the line
			self.currentTrace.setData(self.data[0], self.data[1])
		self.index += 1


	def manual(self):
		if self.running == True:
			self.PV1slider.hide()
			self.Voltage.hide()
			self.Current.hide()
			self.Manual.hide()
		else:
			self.PV1slider.show()
			self.Voltage.show()
			self.Current.show()	
			self.Manual.show()

	def start(self):
		if self.running == True: return
		try:
			self.Res = float(self.Rval.text())
			self.VMIN = float(self.PVmin.text())
			self.VMAX = float(self.PVmax.text())
		except:
			self.msg('Err')
			return
		
		self.IMIN = self.VMIN / self.Res
		self.IMAX = self.VMAX / self.Res
		self.pwin.setXRange(self.ILLIM, self.IULIM)
		self.pwin.setYRange(self.VLLIM, self.VULIM)
		self.running = True
		self.data = [ [], [] ]
		self.VSET = self.VMIN
		self.currentTrace = self.pwin.plot([0,0],[0,0], pen = self.pencol)
		self.index = 0
		self.pencol += 2
		self.msg('Started')
		self.manual()

	def stop(self):
		if self.running == False: return
		self.PV1slider.show()
		self.Voltage.show()
		self.Current.show()
		self.running = False
		self.history.append(self.data)
		self.traces.append(self.currentTrace)
		self.msg('User Stopped')
		self.manual()
		
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
	
