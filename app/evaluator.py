from __future__ import print_function

import sys,inspect,re

import numpy as np
from flask import json
from collections import OrderedDict


class Evaluator:
	'''
	`Compile` python scripts into a JSON array for frontends to render into applications
	'''
	def __init__(self,functionList):		
		self.generatedApp=[]
		self.hasPlot=False
		self.itemList=[]
		
		self.evalGlobals={}
		self.functionList = functionList
		self.evalGlobals = functionList.copy()
		self.evalGlobals['print_']=self.fancyPrint
		self.evalGlobals['print']=self.print
		self.evalGlobals['button']=self.button
		self.evalGlobals['label']=self.label
		self.evalGlobals['plot']=self.plot
		self.evalGlobals['show']=self.show
		
		self.evalGlobals['importer']=self.importer

	def toUnique(self,identifier,suffix=0):
		newId = identifier+str(suffix) if suffix else identifier
		if newId in self.itemList:
			return self.toUnique(identifier,suffix+1)
		return newId
		
	def print(self,*args):
		'''
		For now, the print function is being overloaded in order to capture the console output.
		Future plans will store each line of execution as a json object. This approach will increase flexibility,
		and outputs more than just text, such as images and widgets can be created.
		'''
		name=self.toUnique("print")
		self.generatedApp.append({"type":"text","name":name,"value":[str(a) for a in args]})
		self.itemList.append(name)
		return name
	

	def fancyPrint(self,txt,name="print"):
		name=self.toUnique(name)
		self.generatedApp.append({"type":"span","name":name,"class":"row well","value":str(txt)})
		self.itemList.append(name)
		return name

	#####################  WIDGETS  #####################################
	def label(self,txt,name="print",html_class=""):
		name=self.toUnique(name)
		self.generatedApp.append({"type":"label","name":name,"class":html_class,"value":str(txt)})
		self.itemList.append(name)
		return name

	def button(self,label,endpoint,displayType="display_number",**kwargs):
		name = kwargs.get("name","button-id")
		name=self.toUnique(name)
		self.itemList.append(name)
		
		targetName = kwargs.get('target',name+'-label')
		if 'target' not in kwargs:  #If a target was not specified, make up a name
			targetName = self.toUnique(name+'-label')

		successOpts={"datapoint":'result',"type":displayType,"target":targetName}
		if displayType=='update-plot': # specify the stacking of data
			successOpts['stacking']=kwargs.get('stacking','xy')
		self.generatedApp.append({"type":"button", "name":name,"label":label,"fetched_value":"","action":{"type":"POST","endpoint":endpoint,"success":successOpts}})
		if 'target' not in kwargs:  #If a target was not specified, make a label.
			if displayType in ["display_number","display"]:
				self.label('',targetName)
		return name
	
	#####################  PLOTS  #####################################
	def plot(self,*args,**kwargs):
		name = kwargs.get('name',self.toUnique('myPlot'))
		style =	{
							'axes'  : {
								'xaxis': {
									'tickInterval'    : 1,
									'rendererOptions' : {
										'minorTicks'    : 4
										}
								}
							},
							'highlighter': {
								'show'      : True,
								'showLabel' : True,

								'tooltipAxes'     : 'xy',
								'sizeAdjust'      : 9.5,
								'tooltipLocation' : 'ne'
							},
							'legend': {
								'show'            : True,
								'location'        : 'e',
								'rendererOptions' : {
									'numberColumns' : 1
								}
							},
							'cursor': {
								'show'        : True,
								'zoom'        : True,
								'showTooltip' : False
							}

						}

		style.update(kwargs)

		if len(args)==2:
			self.generatedApp.append({"type":"plot","name":name,"data":[np.array([args[0],args[1]]).T.tolist()], "style":style}) 
		elif len(args)==1:
			self.generatedApp.append({"type":"plot","name":name,"data":[np.array([range(len(args[0])),args[0]]).T.tolist()], "style":style}) 
			style.update({'series':[{
											'label'					: name,
											'lineWidth'     : 2,
											#'markerOptions' : { 'style':'diamond' }
											}
									]})
		self.itemList.append(name)
		return name

	def show(self):
		pass

	#####################  * import LIBRARIES  #####################################
	def importer(self,*args):
		print(args)
	#####################  EVALUATION  #####################################
	def runCode(self,code):
		self.generatedApp=[]
		self.itemList=[]
		code = re.sub(r"(from)\s(.+)\s(import)\s(.+)\n", r"importer('\2','\4')\n", code)
		submitted = compile(code.encode(), '<string>', mode='exec')
		self.exec_scope = self.evalGlobals.copy()
		try:
			exec(submitted, self.exec_scope)
		except Exception as e:
			print(str(e))
			
		return self.getApp()

	def getApp(self):
		return self.generatedApp



		
