# *************************\  FUZZY LOGIC & CONTROLLER /*************************
import numpy
import pygame
from colour import Color 
output_rate = numpy.zeros(100,int)

class Controller:
	def __init__(self, batchReactors, sources, pipes):
		self.batchReactors 	= batchReactors.copy()
		self.nBatchReacts	= len(self.batchReactors)
		self.sources		= sources.copy()
		self.pipes			= pipes.copy()
		self.nSources		= len(self.sources)
		self.input			= numpy.zeros((1, 3+(self.nBatchReacts * 8 * 3)))
		self.controlMatrix  = numpy.zeros((3+(self.nBatchReacts * 8 * 3), self.nSources))
		self.output			= numpy.zeros((1, self.nSources))
		
		self.requiredOut	= 0
		self.reqOutifuzzy 	= []
		self.updateRequiredOut(50)
		
		self.steps 			= 0
		
		self.font_size		= 14
		self.font			= pygame.font.SysFont("georgia", self.font_size)
		self.color			= Color.BLACK
		self.controlName	= "None"
	
	# for inputing rules into the control matrix
	def updateControls(self, ruleComps):
		for c in ruleComps:
			# format for c: [batch Reactor n., chemical n., fuzzy value n., source n., value]
			
			if (c[0] == self.nBatchReacts):
				if (c[1] != 0):
					print("Warning: output only has one chemical\n")
					return False
				if (c[2] < 0 or c[2] > 3):
					print("Warning: wrong value for fuzzy catagory\n")
					return False
				if (c[3] < 0 or c[3] > self.nSources):
					print("Warning: source number out of bounds\n")
					return False
				self.controlMatrix[24*c[0] + 3*c[1] + c[2], c[3]] = c[4]
			else:
				if (c[0] < 0 or c[0] > self.nBatchReacts):
					print("Warning: reactor number out of bounds\n")
					return False
				if (c[1] < 0 or c[1] > 8):
					print("Warning: Chemical number out of bounds\n")
					return False
				if (c[2] < 0 or c[2] > 3):
					print("Warning: fuzzy catagory out of bounds\n")
					return False
				if (c[3] < 0 or c[3] > self.nSources):
					print("Warning: source number out of bounds\n")
					return False
				self.controlMatrix[24*c[0] + 3*c[1] + c[2], c[3]] = c[4]
		return True
	
	def updateRequiredOut(self, newValue):
		self.requiredOut = newValue
		
		if (self.requiredOut < 20):
			low = 100 - self.requiredOut*5
			med = 100 - low
			high = 0
		elif (self.requiredOut < 40):
			low = 0
			med = 100
			high = 0
		elif (self.requiredOut < 60):
			low = 0
			med = 300 - self.requiredOut*5
			high = 100 - med
		else:
			low = 0
			med = 0
			high = 100
		self.reqOutifuzzy = [low,med,high]
	
	#Get the fuzzify values 
	def getInputs(self):
		i = 0
		for batchRect in self.batchReactors:
			batchRect.fuzzify()
			for fuzzy in batchRect.chemifuzzy:
					for val in fuzzy:
						self.input[0,i] = val
						i += 1
		for val in self.reqOutifuzzy:
			self.input[0,i] = val
			i += 1
		
		return True
	
	#Uses fuzzy values 
	def controlSource(self):
		self.getInputs()
		numpy.matmul(self.input, self.controlMatrix, self.output)

		i = 0
		for source in self.sources:
			if (self.output[0 ,i] < 0):
				self.output[0, i] = 0
			
			source.chance = self.output[0, i]%101
			i += 1
		
			
		return True
		
	def step(self):
		self.steps += 1
		global output_rate
		
		for pipe in self.pipes:
			pipe.flow()
		for source in self.sources:
			self.controlSource()
			source.generate()
		for batch in self.batchReactors:
			batch.adapt()
			gen = batch.generate()
			if (batch.name == "A"):
				output_rate = numpy.append(output_rate,[gen])
				output_rate = output_rate[1:]
	
	def resetSimulation(self):
		self.steps = 0
		for pipe in self.pipes:
			pipe.clearPipe()
		for source in self.sources:
			source.thres = 100
			source.total = 0			
		for batch in self.batchReactors:
			batch.thres = 100
			batch.total = 0
			batch.chemicals.fill(0)
		
def get_output_rate():
    return output_rate