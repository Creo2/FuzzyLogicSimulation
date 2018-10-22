import pygame
import sys
import numpy
from colour import Color,get_colors
from controller import get_output_rate
import random
# dont like this :C 
colours = get_colors()

# Chemical class
class Chemical:
	def __init__(self, ctype):
		self.ctype = ctype

	def render(self,x,y,screen):
		pygame.draw.circle(screen, colours[self.ctype].value, (x,y), 5, 0)
# Pipe class - contain the chemicals and transfer to batch
class Pipe:
	def __init__(self, x, y, length, width, batch_converter):
		self.x = x
		self.y = y
		self.length = length
		self.width = width
		self.contents = [0]*int(max(abs(length/20),abs(width/20)))
		self.output = batch_converter
		self.flowing = 1
	def flow(self):
		if (self.flowing == 0):
			return
		index = len(self.contents) - 1
		if (self.contents[index] != 0):
			if (self.output != None):
				self.output.add(self.contents[index])                        
		while (index > 0):
			self.contents[index] = self.contents[index-1]
			index-=1
		self.contents[0] = 0

	def render(self,screen):
		pygame.draw.rect(screen, Color.BLACK.value, (self.x, self.y, self.length, self.width), 1)
		new_x = self.x + 10*int(self.length/abs(self.length))
		new_y = self.y + 10*int(self.width/abs(self.width))
		index = 0
		while (index < len(self.contents)):
			if (self.contents[index] != 0):
				self.contents[index].render(new_x, new_y,screen)
			index+=1
			if (abs(self.width) < abs(self.length)):
				new_x += 20*int(self.length/abs(self.length))
			else:
				new_y += 20*int(self.width/abs(self.width))
	def clearPipe(self):
		index = len(self.contents) - 1                       
		while (index > -1):
			self.contents[index] = 0
			index-=1
			
			
# Batch Converter class, track how many chemicals are inside and generate
# new chemicals dependant on the prerequisites
class BatchConverter:
	def __init__(self, x, y, ctype, creqs, pipes, name, chance):
		self.x 			= x
		self.y 			= y
		self.ctype 		= ctype
		self.creqs 		= creqs
		self.pipes 		= pipes
		self.basechance = 25
		self.thres 		= 100
		self.total 		= 0.0
		self.chance		= chance
		self.reactRate  = 1.0
		self.chemicals 	= numpy.zeros(8,int)
		self.chemifuzzy = [[100,0,0]]*8
		self.chemSum	= 0	
		
		self.name 		= name
		self.font_size 	= 28
		self.font 		= pygame.font.SysFont("georgia", self.font_size)
		self.color 		= Color.BLACK
		self.font.set_bold(1)
		
		
	def add(self, chemical):
		self.chemicals[chemical.ctype] += 1
	def generate(self):
		if (self.pipes == None):
			return 0
		temp = numpy.subtract(self.chemicals,self.creqs)
		for index in temp:
			if (index < 0):
				return 0
		for pipe in self.pipes:
			if (pipe.contents[0] == 0):
				self.total += self.chance
				if (self.total >= self.thres):
					self.total %= self.thres
					#Actually outputted a chemical
					self.chemicals = temp
					pipe.contents[0] = Chemical(self.ctype)
					return 1
		return 0
	def render(self,screen):
		pygame.draw.rect(screen, Color.GRAY.value, (self.x, self.y, 60,60),0)
		liqLevel = 55*(self.chemSum/100)
		pygame.draw.rect(screen, Color.BLUE.value, (self.x+45, self.y+55-liqLevel, 10, liqLevel),0)
		self.font_size = 28
		screen.blit(self.font.render(self.name, True, self.color.value), [self.x+20, self.y+12])
		screen.blit(self.font.render(str(self.chance), True, self.color.value), [self.x-20, self.y-12])
		screen.blit(self.font.render(str(numpy.count_nonzero(get_output_rate())), True, self.color.value), [900, 500])
	def adapt(self):
		self.chemSum = 0
		for chem in self.chemicals:
			self.chemSum += chem
		self.chance = self.basechance + (min(round(self.chemSum*self.reactRate,1),75))
	def report(self, draw_x, screen):
		x = draw_x
		y = 550
		w = 15
		h = 5
		screen.blit(self.font.render(self.name, True, self.color.value), [x+5, y + 20])
			
		index = 0
		while (index < len(self.chemicals)):
			if (self.creqs[index] == 1):
				height = min(self.chemicals[index]*h,250)
				pygame.draw.rect(screen, colours[index].value, (x,y-height,w,height),0)
				x+=w
			index+=1
	def fuzzify(self, membership_f):
		index = 0
		while (index < len(self.chemicals)):
			#Apply the correct Fuzzy Logic Membership Function
			chem = self.chemicals[index]
			if (membership_f == 0):
				#Trapezoidal: 0 = [100,0,0] 10 = [0,100,0] 20 = [0,100,0], 30 = [0,0,100] with linear shifts in regions
				if (chem < 10):
					low = 100 - chem*10
					med = 100 - low
					high = 0
				elif (chem < 20):
					low = 0
					med = 100
					high = 0
				elif (chem < 30):
					low = 0
					med = 300 - chem*10
					high = 100 - med
				else:
					low = 0
					med = 0
					high = 100
			if (membership_f == 1):
				#Uniform: [100,0,0] from 0->15, [0,100,0] from 15->30 and [0,0,100] from 30+
				if (chem < 15):
					low = 100
					med = 0
					high = 0
				elif (chem < 30):
					low = 0
					med = 100
					high = 0
				else :
					low = 0
					med = 0
					high = 100
			if (membership_f == 2):
				#Gaussian Approximation
				#Negative Quadratics, shifted to suit function.
				low = max(100 - chem*chem,0)
				med = max(100 - (chem-15)*(chem-15),0)
				high = max(100 - (chem-30)*(chem-30),0)
				if (chem >= 30):
					high = 100
			
			self.chemifuzzy[index] = [low,med,high]
			index+=1
			

class ChemicalSource:
	def __init__(self, x, y, ctype, pipes, chance, name=""):
		self.font_size 	= 12
		self.font 		= pygame.font.SysFont("georgia", self.font_size)
		self.font.set_bold(1)
		
		self.name		= name 
		
		self.x 			= x
		self.y 			= y
		self.ctype		= ctype
		self.pipes 		= pipes
		self.thres 		= 100
		self.total 		= 0
		self.chance 	= chance
		self.color 		= Color.BLACK
		
	def adapt(self):
		nb = self.pipes[0].output
		nbc = nb.chemifuzzy[self.ctype]
		nnb = nb.pipes[0].output
		nnbc = nnb.chemifuzzy[nb.ctype]
		self.chance = (1/100)*(100-nbc[2])*(nbc[0] + 0.5*nbc[1])*(1/100)*(100-nnbc[2])*(nnbc[0]+0.5*nnbc[1])*(1/100)
	def generate(self):
		for pipe in self.pipes:
			if (pipe.contents[0] == 0):
				self.total += self.chance*random.uniform(0.8, 1.2)
				print(self.total)
				if (self.total > self.thres):
					self.total %= (self.thres)
					pipe.contents[0] = Chemical(self.ctype)
					
	def render(self,screen):
		screen.blit(self.font.render(self.name + "=" + str(round(self.chance,2)),
					True, self.color.value), [self.x, self.y - 20])
		pygame.draw.rect(screen,colours[self.ctype].value, (self.x, self.y, 20, 20),0)

		
	