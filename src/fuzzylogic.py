import pygame
import numpy
import random

# Defining my colours
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
LIGHTGRAY = (200, 200, 200)
WHITE = (255, 255, 255)
RED = (150, 0, 0)
GREEN = (100, 200, 100)
DARKGREEN = (0, 100, 0)
BLUE = (0, 0, 150)
CYAN = (50, 220, 220)
YELLOW = (220, 220, 50)
colours = [RED, GREEN, CYAN, BLUE, DARKGREEN, YELLOW, BLACK, GRAY]
output_rate = numpy.zeros(100,int)

# Chemical class
class Chemical:
	def __init__(self, ctype):
		self.ctype = ctype

	def render(self,x,y):
		pygame.draw.circle(screen, colours[self.ctype], (x,y), 5, 0)
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
		pipes.append(self)
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

	def render(self):
		pygame.draw.rect(screen, BLACK, (self.x, self.y, self.length, self.width), 1)
		new_x = self.x + 10*int(self.length/abs(self.length))
		new_y = self.y + 10*int(self.width/abs(self.width))
		index = 0
		while (index < len(self.contents)):
			if (self.contents[index] != 0):
				self.contents[index].render(new_x, new_y)
			index+=1
			if (abs(self.width) < abs(self.length)):
				new_x += 20*int(self.length/abs(self.length))
			else:
				new_y += 20*int(self.width/abs(self.width))
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
		self.total 		= 0
		self.chance		= chance
		self.chemicals 	= numpy.zeros(8,int)
		self.chemifuzzy = [[100,0,0]]*8
		
		self.name 		= name
		self.font_size 	= 28
		self.font 		= pygame.font.SysFont("georgia", self.font_size)
		self.color 		= BLACK
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
				if (self.total > self.thres):
					self.total -= self.thres
					#Actually outputted a chemical
					self.chemicals = temp
					pipe.contents[0] = Chemical(self.ctype)
					return 1
		return 0
	def render(self):
		pygame.draw.rect(screen, GRAY, (self.x, self.y, 60,60),0)
		self.font_size = 28
		screen.blit(self.font.render(self.name, True, self.color), [self.x+20, self.y+12])
		screen.blit(self.font.render(str(self.chance), True, self.color), [self.x-20, self.y-12])
		screen.blit(self.font.render(str(numpy.count_nonzero(output_rate)), True, self.color), [900, 500])
	def adapt(self):
		chemsum = 0
		for chem in self.chemicals:
			chemsum += chem
		self.chance = self.basechance + (min(chemsum,75))
	def report(self, draw_x):
		x = draw_x
		y = 550
		w = 15
		h = 5
		screen.blit(self.font.render(self.name, True, self.color), [x+5, y + 20])
			
		index = 0
		while (index < len(self.chemicals)):
			if (self.creqs[index] == 1):
				height = min(self.chemicals[index]*h,250)
				pygame.draw.rect(screen, colours[index], (x,y-height,w,height),0)
				x+=w
			index+=1
	def fuzzify(self):
		index = 0
		while (index < len(self.chemicals)):
			#Apply Fuzzy Logic Membership Function
			chem = self.chemicals[index]
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
			self.chemifuzzy[index] = [low,med,high]
			index+=1
			

class ChemicalSource:
	def __init__(self, x, y, ctype, pipes, chance):
		self.font_size 	= 12
		self.font 		= pygame.font.SysFont("georgia", self.font_size)
		self.font.set_bold(1)
		
		self.x 			= x
		self.y 			= y
		self.ctype		= ctype
		self.pipes 		= pipes
		self.thres 		= 100
		self.total 		= 0
		self.chance 	= chance
		self.color 		= BLACK
		
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
				if (self.total > self.thres):
					self.total -= self.thres
					pipe.contents[0] = Chemical(self.ctype)
	def render(self):
		screen.blit(self.font.render(str(round(self.chance,2)), True, self.color), [self.x, self.y - 20])
		pygame.draw.rect(screen,colours[self.ctype], (self.x, self.y, 20, 20),0)

class Controller:
	def __init__(self, batchReactors, sources, pipes):
		self.batchReactors 	= batchReactors.copy()
		self.nBatchReacts	= len(self.batchReactors)
		self.sources		= sources.copy()
		self.pipes			= pipes.copy()
		self.nSources		= len(self.sources)
		self.input			= numpy.zeros((1, self.nBatchReacts * 8 * 3))
		self.controlMatrix  = numpy.zeros((self.nBatchReacts * 8 * 3, self.nSources))
		self.output			= numpy.zeros((1, self.nSources))
		
		self.font_size		= 28
		self.font			= pygame.font.SysFont("georgia", self.font_size)
		self.color			= BLACK
		
	def updateControls(self, ruleComps):
		for c in ruleComps:
			# format for c: [batch Reactor n., chemical n., fuzzy value n., source n., value]
			if (c[0] < 0 or c[0] > self.nBatchReacts):
				return False
			if (c[1] < 0 or c[1] > 8):
				return False
			if (c[2] < 0 or c[2] > 3):
				return False
			if (c[3] < 0 or c[3] > self.nSources):
				return False
			self.controlMatrix[24*c[0] + 3*c[1] + c[2], c[3]] = c[4]
		return True
	
	def getInputs(self):
		i = 0
		for batchRect in self.batchReactors:
			batchRect.fuzzify()
			for fuzzy in batchRect.chemifuzzy:
					for val in fuzzy:
						self.input[0,i] = val
						i += 1
		return True
		
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
				screen.blit(self.font.render("Test", True, self.color), [900, 500])

	
# Initialise pygame module
pygame.init()
# Create game window
size = [1000,600]
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Fuzzy Logic")
# Initialise pygame clock
clock = pygame.time.Clock()

# Build the chemical process plant
pipes = []
batchConverters = []
sources = []

link_0 = Pipe(840,420,160,20,None)
batchConverters.append(BatchConverter(780,400,4,[0,0,0,0,0,1,1,0],[link_0],"A",70))
link_1 = Pipe(680,420,100,20,batchConverters[len(batchConverters)-1])
link_2 = Pipe(800,260,20,140,batchConverters[len(batchConverters)-1])

batchConverters.append(BatchConverter(620,400,5,[1,0,0,0,0,0,0,1],[link_1],"B",70))
Pipe(420,420,200,20,batchConverters[len(batchConverters)-1])
sources.append(ChemicalSource(400,420,0,[pipes[len(pipes)-1]],20))
link_3 = Pipe(640,80,20,320,batchConverters[len(batchConverters)-1])

batchConverters.append(BatchConverter(780,200,6,[1,1,1,0,0,0,0,0],[link_2],"C",70))
Pipe(800,100,20,100,batchConverters[len(batchConverters)-1])
sources.append(ChemicalSource(800,80,0,[pipes[len(pipes)-1]],20))
Pipe(500,220,280,20,batchConverters[len(batchConverters)-1])
sources.append(ChemicalSource(480,220,1,[pipes[len(pipes)-1]],40))
Pipe(940,220,-100,20,batchConverters[len(batchConverters)-1])
sources.append(ChemicalSource(940,220,2,[pipes[len(pipes)-1]],20))

batchConverters.append(BatchConverter(620,20,7,[1,1,0,0,0,0,0,0],[link_3],"D",70))
Pipe(420,40,200,20,batchConverters[len(batchConverters)-1])
sources.append(ChemicalSource(400,40,0,[pipes[len(pipes)-1]],20))
Pipe(880,40,-200,20,batchConverters[len(batchConverters)-1])
sources.append(ChemicalSource(880,40,1,[pipes[len(pipes)-1]],40))

#	batchConverters and sourcelayout is as follows:
#	batchConverters = [ A = 0	source = [	B0 = 0 chemical = 0
#						B = 1				C0 = 1 chemical = 0
#						C = 2				C1 = 2 chemical = 1
#						D = 3				C2 = 3 chemical = 2
#					  ]						D0 = 4 chemical = 0
#											D1 = 5 chemical = 1
#										 ]

controller = Controller(batchConverters, sources, pipes)
controller.updateControls([  
#							[BaR, Chm, Fuz, Src, Val], 
							[  1,   0,   0,   0,   2  ],
							[  1,   0,   1,   0,   1  ],
							[  2,   0,   0,   1,   1  ],
							[  2,   0,   1,   1,   0.75],
							[  0,   6,   2,   1,   -1 ],
							[  2,   1,   0,   2,   1  ],
							[  2,   1,   1,   2,   0.75],
							[  0,   6,   2,   2,   -1 ],
							[  2,   2,   0,   3,   1  ],
							[  2,   2,   1,   3,   0.75],
							[  0,   6,   2,   3,   -1 ],
							[  3,   0,   0,   4,   1  ],
							[  3,   0,   1,   4,   0.75],
							[  1,   7,   2,   4,   -1  ],
							[  3,   1,   0,   5,   1   ],
							[  3,   1,   1,   5,   0.75],
							[  1,   7,   2,   5,   -1  ],
						  ])

controller.step()

# Begin game loop
exit_flag = 0
auto = False
last_time = pygame.time.get_ticks()
while (exit_flag == 0):
	# Deal with all user events
	for event in pygame.event.get():
		# Check for key presses
		if event.type == pygame.KEYDOWN:
			# User hit the Q key -> EXIT
			if event.key == pygame.K_q:
				exit_flag = 1
			# User hit the S key -> START/STOP Auto flow
			if event.key == pygame.K_s:
				auto = not auto
			# User hit SPACE -> Force flow
			if event.key == pygame.K_SPACE:
				if not auto:
					controller.step()
						
	# Automatically cycle through process every 0.5s
	if auto:
		new_time = pygame.time.get_ticks()
		if (new_time - last_time > 100):
			controller.step()
				
			last_time = new_time
			
	# Wash with clean background
	screen.fill(WHITE)
	# Draw UI
	pygame.draw.rect(screen, LIGHTGRAY, (0, 0, 4*size[0]/10, size[1]), 0)

	#Draw simulation elements
	draw_x = 50
	for bc in batchConverters:
		bc.render()
		bc.report(draw_x)
		draw_x += 80
	for pipe in pipes:
		pipe.render()
	for source in sources:
		source.render()
	


	# Update screen with new contents
	pygame.display.flip()
	# Limit fps
	# clock.tick(10)

# We're out of the game loop so shut things down
pygame.quit()
#quit()

