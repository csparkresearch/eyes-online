import sys, time, utils, math, importlib, os, platform

if utils.PQT5 == True:
	from PyQt5.QtWidgets import QMainWindow, QApplication, QCheckBox, QStatusBar, QLabel,QDesktopWidget
	from PyQt5.QtGui import QPalette, QColor
	from PyQt5.QtWebKitWidgets import QWebView
	from PyQt5.QtCore import QUrl, QSize
else:
	from PyQt4.QtCore import Qt, QTimer, QUrl, QSize
	from PyQt4.QtGui import QPalette, QColor, QFont, QMainWindow, QApplication, QCheckBox,\
	QStatusBar, QLabel,QDesktopWidget
	from PyQt4.QtWebKit import QWebView,QWebSettings
	
import pyqtgraph as pg

pf = platform.platform()
print (pf)	
if 'Windows' in pf:
	import diodeIV, editor, filterCircuit, induction, MPU6050, npnCEout, pendulumVelocity
	import plotIV, pnpCEout, pt100, RCsteadystate, RCtransient, RLCsteadystate, RLCtransient
	import RLtransient, rodPendulum, scope, soundBeats, soundFreqResp, soundVelocity
	import sr04dist, utils

schoolExpts = [ 
["Resistance measurement", 'res-measure'],
["Resistors in Series", 'res-series'],
["Resistors in Parallel", 'res-parallel'],
["Capacitance measurement", 'cap-measure'],
["Capacitors in Series", 'cap-series'],
["Capacitors in Parallel", 'cap-parallel'],
["Resistance by Ohm's law", 'res-compare'],
['Direct and Alternating Currents', 'ac-dc'],
['Separating AC and DC', 'acdc-separating'],
['Conducting Human body', 'conducting-human'],
['Resistance of Human body', 'res-body'],
['Lemon Cell', 'lemon-cell'],
['Simple AC generator', 'ac-generator'],
['Transformer', 'transformer'],
['Resistance of Water', 'res-water'],
['Sound Generator', 'sound-generator'],
['Light Dependent Resistor', 'ldr'],
['Capturing Sound', 'sound-capture'],
['Stroboscope', 'stroboscope'],
['Driven Pendulum resonance','driven-pendulum']
]


testEquipment = [ 
['Oscilloscope','scope'],
['Monitor and Control', 'mon-con']
]

electronicsExpts = [ 
['Diode IV Char.','diodeIV'],
['NPN Output Char.','npnCEout'],
['PNP Output Char.','pnpCEout'],
#['AM and FM', 'amfm']
]

electronicsExptsScope = [ 
['Oscilloscope','scope'],
['Halfwave Rectifier','halfwave'],
['Fullwave Rectifier','fullwave'],
['Diode Clipping','clipping'],
['Diode Clamping','clamping'],
['IC555 Multivibrator','osc555'],
['Inverting Amplifier','opamp-inv'],
['Non-Inverting Amplifier','opamp-noninv'],
['Integrator using Op-Amp','opamp-int'],
['Logic Gates','logic-gates'],
['Clock Divider Circuit','clock-divider']
]

electricalExpts = [ 
['Plot I-V Curve','plotIV'],
#['RC Steady state response','RCsteadystate'],
['RLC Steady state response','RLCsteadystate'],
['RC Transient response','RCtransient'],
['RL Transient response','RLtransient'],
['RLC transient response','RLCtransient'],
['Frequency Response of Filter Circuit','filterCircuit'],
['Electromagnetic Induction','induction']
]

soundExpts = [
['Frequency Response of Piezo Buzzer','soundFreqResp'],
['Velocity of Sound' , 'soundVelocity'],
['Sound beats' , 'soundBeats']
]

mechanicsExpts = [
['Rod Pendulum with Light barrier' , 'rodPendulum'],
['Pendulum Wavefrorm','pendulumVelocity'],
['Distance by HY-SRF04 Echo module', 'sr04dist']
]

otherExpts = [ 
['Temperatue, PT100 Sensor', 'pt100'],
#['Data Logger', 'logger']
]

modulesI2C = [ 
['MPU-6050 Acccn, Velocity and Temp', 'MPU6050'],
]

pythonCodes = [ 
['Read Inputs',  'readInputs'],
['Capture Single Input', 'capture1'],
['Capture Two Inputs', 'capture2'],
['Capture Four Inputs', 'capture4'],
['Set DC Voltages', 'setVoltages'],
['Triangular Waveform', 'triangularWave'],
['Arbitrary Wavefrom', 'waveforms'],
['Charging of Capacitor', 'chargingCap'],
#['Play music on WG', 'music']
]


#---------------------------------------------------------------------
class helpWin(QWebView):
	def __init__(self, name = ''):
		QWebView.__init__(self)
		fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'html', name[1]+'.html')
		self.load(QUrl.fromLocalFile(fn))
		self.setWindowTitle('Help: '+name[0])
		self.setMaximumSize(QSize(500, 1200))
		self.show()
		screen = QDesktopWidget().screenGeometry()
		self.move(screen.width()-self.width()-20, screen.height()-self.height()-60)


class MainWindow(QMainWindow):
	WIDTH = 900
	HEIGHT = 550
	expWidget = None
	expName = ''
	hlpName = ''
	hwin = None
	
	def closeEvent(self, e):
		if self.hwin != None:
			self.hwin.close()

	def __init__(self):
		QMainWindow.__init__(self)
		self.makeMenu()
		self.setMinimumSize(self.WIDTH, self.HEIGHT)
		self._x = 100
		self._y = 10
		palette = QPalette()								# background color
		palette.setColor(QPalette.Background, QColor("#88bbcc")) #("#99ccff"))
		self.setPalette(palette)	

		self.helpCB = QCheckBox('Show PopUp Help Window')
		self.helpCB.stateChanged.connect(self.showHelp)

		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)
		self.statusBar.addWidget(self.helpCB)
		
		self.callExpt(testEquipment[0])					# Start the scope by default
		self.screen = QDesktopWidget().screenGeometry()
		self.show()
		self.move(20, 20)


	def showHelp(self):
		if self.helpCB.isChecked() == True:
			if self.hwin == None: 
				self.hwin = helpWin((self.title,self.hlpName))
			self.hwin.show()
		else:
			if self.hwin != None: self.hwin.hide()
	
	
	def scope_help(self,e):
		self.hlpName = e[1]
		if self.expName != 'scope':
			explib = importlib.import_module('scope')
			try:
				if self.expWidget != None:
					self.expWidget.timer.stop()     # Stop the timer loop of current widget			
				self.hwin = None
				self.expWidget= None 			    # Let python delete it
				w = explib.Expt(p) 
				self.setWindowTitle(e[0])
				self.setCentralWidget(w)
				self.expWidget = w
				self.expName = 'scope'
			except:
				self.expName = ''
				self.setWindowTitle('Failed to load scope')
		self.hwin = None
		self.title = e[0]
		self.showHelp()
	

	def callExpt(self, e):
		explib = importlib.import_module(e[1])
		try:
			if self.expWidget != None:
				self.expWidget.timer.stop()     # Stop the timer loop of current widget			
			self.hwin = None
			self.expWidget= None 			    # Let python delete it
			w = explib.Expt(p) 
			self.setWindowTitle(e[0])
			self.setCentralWidget(w)
			self.expWidget = w
			self.expName = e[1]
			self.hlpName = e[1]
			self.title = e[0]
			self.showHelp()
		except:
			self.expName = ''
			self.setWindowTitle('Failed to load %s'%e[0])

	def runCode(self, e):
		if self.expName != 'editor':
			self.callExpt( ('Python Coding', 'editor'))
		self.expWidget.mycode = e[1]
		self.expWidget.update()
	
		
	def makeMenu(self):
		bar = self.menuBar()

		mb = bar.addMenu("Device")
		mb.addAction('Reconnect', self.reconnect)

		em = bar.addMenu("School Expts")
		for e in schoolExpts:
			em.addAction(e[0],  lambda item=e: self.scope_help(item))	

		em = bar.addMenu("Electronics")
		for e in electronicsExptsScope:
			em.addAction(e[0],  lambda item=e: self.scope_help(item))	
			
		for e in electronicsExpts:
			em.addAction(e[0],  lambda item=e: self.callExpt(item))	
		
		em = bar.addMenu("Electrical")
		for e in electricalExpts:
			em.addAction(e[0],  lambda item=e: self.callExpt(item))	

		em = bar.addMenu("Sound")
		for e in soundExpts:
			em.addAction(e[0],  lambda item=e: self.callExpt(item))	

		em = bar.addMenu("Mechanics")
		for e in mechanicsExpts:
			em.addAction(e[0],  lambda item=e: self.callExpt(item))	

		em = bar.addMenu("Other Expts")
		for e in otherExpts:
			em.addAction(e[0],  lambda item=e: self.callExpt(item))	

		em = bar.addMenu("I2C Modules")
		for e in modulesI2C:
			em.addAction(e[0],  lambda item=e: self.callExpt(item))	

		em = bar.addMenu("PythonCode")
		for e in pythonCodes:
			em.addAction(e[0],  lambda item=e: self.runCode(item))	


	def reconnect(self):
		global p
		try:
			p.H.disconnect()
		except:
			pass
		p=eyes.open()
		if p != None: 
			p.select_range('A1',4)
		self.expWidget.p = p
		self.expWidget.msg('')

		
# Program starts here
import eyes17.eyes as eyes
p = eyes.open()
if p != None: 
	p.set_sine(1000)
	p.set_sqr1(-1)
	p.set_pv1(0)
	p.set_pv2(0)
	p.set_state(OD1=0)

app = QApplication(sys.argv)
mw = MainWindow()
sys.exit(app.exec_())
