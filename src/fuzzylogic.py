import sys
import pygame
import numpy
import random
from colour import get_colors,Color
# Defining my colours


output_rate = numpy.zeros(100,int)
colours = get_colors()
# *************************\ NONE FUZZY LOGIC RELATED FUNCTIONS /*************************
class Button():
    def __init__(self, txt, location, action, input, size=(80, 30), font_name="georgia", font_size=16):
        self.color 	= Color.WHITE  # the static (normal) color
        self.bg 	= Color.WHITE  # actual background color, can change on mouseover
        self.fg 	= Color.BLACK  # text color
        self.size 	= size
        self.font = pygame.font.SysFont(font_name, font_size)
        self.txt = txt
        self.txt_surf = self.font.render(self.txt, 1, self.fg.value)
        self.txt_rect = self.txt_surf.get_rect(center=[s//2 for s in self.size])
		
        self.surface = pygame.surface.Surface(size)
        self.rect = self.surface.get_rect(center=location)
		
        self.call_back_ = action
        self.input = input
		
		
    def draw(self):
        self.mouseover()

        self.surface.fill(self.bg.value)
        self.surface.blit(self.txt_surf, self.txt_rect)
        screen.blit(self.surface, self.rect)

    def mouseover(self):
        self.bg = self.color
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.bg = Color.GRAY  # mouseover color

    def call_back(self):
        self.call_back_(self.input)
		
def mousebuttondown(buttons, controller):
	pos = pygame.mouse.get_pos()
	for button in buttons:
		if button.rect.collidepoint(pos):
			button.call_back()


# Chemical class
class Chemical:
	def __init__(self, ctype):
		self.ctype = ctype

	def render(self,x,y):
		pygame.draw.circle(screen, self.ctype, (x,y), 5, 0)
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
		pygame.draw.rect(screen, Color.BLACK.value, (self.x, self.y, self.length, self.width), 1)
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
					self.total %= (self.thres + 1)
					#Actually outputted a chemical
					self.chemicals = temp
					pipe.contents[0] = Chemical(self.ctype)
					return 1
		return 0
	def render(self):
		pygame.draw.rect(screen, Color.GRAY.value, (self.x, self.y, 60,60),0)
		liqLevel = 55*(self.chemSum/100)
		pygame.draw.rect(screen, Color.BLUE.value, (self.x+45, self.y+55-liqLevel, 10, liqLevel),0)
		self.font_size = 28
		screen.blit(self.font.render(self.name, True, self.color.value), [self.x+20, self.y+12])
		screen.blit(self.font.render(str(self.chance), True, self.color.value), [self.x-20, self.y-12])
		screen.blit(self.font.render(str(numpy.count_nonzero(output_rate)), True, self.color.value), [900, 500])
	def adapt(self):
		self.chemSum = 0
		for chem in self.chemicals:
			self.chemSum += chem
		self.chance = self.basechance + (min(self.chemSum*self.reactRate,75))
	def report(self, draw_x):
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
				if (self.total > self.thres):
					self.total %= (self.thres + 1)
					pipe.contents[0] = Chemical(self.ctype)
					
	def render(self):
		screen.blit(self.font.render(self.name + "=" + str(round(self.chance,2)),
					True, self.color.value), [self.x, self.y - 20])
		pygame.draw.rect(screen,colours[self.ctype].value, (self.x, self.y, 20, 20),0)

		
# *************************\  FUZZY LOGIC & CONTROLLER /*************************
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
			
class Logger:
	def __init__(self,  name, controller):
		self.controller		= controller
		self.name			= name
		self.file			= open(name + ".csv","w+")
		
		self.file.write("steps,")
		for batchReactor in self.controller.batchReactors:
			for i in range(0, 8):
				self.file.write(batchReactor.name + "chem%d," % i)
			self.file.write(batchReactor.name + "reactRate,")
		for source in self.controller.sources:
			self.file.write(source.name + "thres,")
			self.file.write(source.name + "chance,")
		
		self.file.write("zeros\n")
	
	def writeToFile(self):
		self.file.write("%d," % controller.steps)
		
		for batchReactor in self.controller.batchReactors:
			for i in range(0, 8):
				self.file.write("%d," % batchReactor.chemicals[i])
			self.file.write("%d," % batchReactor.chance)
		for source in self.controller.sources:
			self.file.write("%d," % source.thres)
			self.file.write("%d," % source.chance)
		
		self.file.write("0\n")
		
	def closeFile(self):
		self.file.close()
		
		
def setupRuleSet1(controller):
	controller.controlName = "Rule Set 1"
	controller.controlMatrix.fill(0)
	#	batchReactors and sourcelayout is as follows:
	#	batchReactors = [ A = 0	source = [	B0 = 0 chemical = 0
	#						B = 1				C0 = 1 chemical = 0
	#						C = 2				C1 = 2 chemical = 1
	#						D = 3				C2 = 3 chemical = 2
	#					  ]						D0 = 4 chemical = 0
	#											D1 = 5 chemical = 1
	#										 ]

	
	controller.updateControls([  
	#							[BaR, Chm, Fuz, Src, Val], 
								[  1,   0,   0,   0,   2  ],
								
								[  2,   0,   0,   1,   1  ],
								
								[  2,   1,   0,   2,   1  ],
								
								[  2,   2,   0,   3,   1  ],
								
								[  3,   0,   0,   4,   1  ],
								
								[  3,   1,   0,   5,   1  ],
							  ])

def setupRuleSet2(controller):
	controller.controlName = "Rule Set 2"
	controller.controlMatrix.fill(0)
	#	batchReactors and sourcelayout is as follows:
	#	batchReactors = [ A = 0	source = [	B0 = 0 chemical = 0
	#						B = 1				C0 = 1 chemical = 0
	#						C = 2				C1 = 2 chemical = 1
	#						D = 3				C2 = 3 chemical = 2
	#					  ]						D0 = 4 chemical = 0
	#											D1 = 5 chemical = 1
	#										 ]

	
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
							  
def setupRuleSet3(controller):
	controller.controlName = "Rule Set 3"
	controller.controlMatrix.fill(0)
	#	batchReactors and sourcelayout is as follows:
	#	batchReactors = [ A = 0	source = [	B0 = 0 chemical = 0
	#						B = 1				C0 = 1 chemical = 0
	#						C = 2				C1 = 2 chemical = 1
	#						D = 3				C2 = 3 chemical = 2
	#					  ]						D0 = 4 chemical = 0
	#											D1 = 5 chemical = 1
	#										 ]

	
	controller.updateControls([  
	#							[BaR, Chm, Fuz, Src, Val], 
								[  1,   0,   0,   0,   2  ],
								[  1,   0,   1,   0,   -0.5],
								[  1,   0,   2,   0,   -2  ],
								[  1,   7,   1,   0,   1   ],
								[  1,   7,   2,   0,   1.5 ],
																
								[  2,   0,   0,   1,   1   ],
								[  2,   0,   1,   1,   0.75],
								[  0,   6,   2,   1,   -1  ],
								
								[  2,   1,   0,   2,   1   ],
								[  2,   1,   1,   2,   0.75],
								[  0,   6,   2,   2,   -1  ],
								
								[  2,   2,   0,   3,   1   ],
								[  2,   2,   1,   3,   0.75],
								[  0,   6,   2,   3,   -1  ],
								
								[  3,   0,   0,   4,   1   ],
								[  3,   0,   2,   4,   -2   ],
								[  1,   7,   1,   4,   -0.5],
								[  1,   7,   2,   4,   -2  ],
								[  1,   0,   1,   4,   1   ],
								[  1,   0,   2,   4,   1.5 ],
								
								[  3,   1,   0,   5,   1    ],
								[  3,   1,   2,   5,   -2   ],
								[  1,   7,   1,   5,   -0.5],
								[  1,   7,   2,   5,   -2   ],
								[  1,   0,   1,   5,   1    ],
								[  1,   0,   2,   5,   1.5  ],
							  ])					  
	
	
	
def increaseThres(source):
	if (source.thres < 299):
		source.thres += 10
	
def decreaseThres(source):
	if (source.thres > 1):
		source.thres -= 10

def increaseRR(batchReactor):
	if (batchReactor.reactRate < 2.99):
		batchReactor.reactRate += 0.1

def decreaseRR(batchReactor):
	if (batchReactor.reactRate > 0.01):
		batchReactor.reactRate -= 0.1

def resetSimulation(controller):
	controller.resetSimulation()

def increateDemand(controller):
	newVal = controller.requiredOut + 1
	if (newVal < 76): 
		controller.updateRequiredOut(newVal)

def decreateDemand(controller):
	newVal = controller.requiredOut - 1
	if (newVal > -1): 
		controller.updateRequiredOut(newVal)
	
# Check inputs to see if log should be enabled
enableLog = False
logName	  = ""
if len(sys.argv) == 2:
	enableLog = True
	logName = sys.argv[1]
		
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
batchReactors = []
sources = []

link_0 = Pipe(840,420,160,20,None)
batchReactors.append(BatchConverter(780,400,4,[0,0,0,0,0,1,1,0],[link_0],"A",70))
link_1 = Pipe(680,420,100,20,batchReactors[len(batchReactors)-1])
link_2 = Pipe(800,260,20,140,batchReactors[len(batchReactors)-1])

batchReactors.append(BatchConverter(620,400,5,[1,0,0,0,0,0,0,1],[link_1],"B",70))
Pipe(420,420,200,20,batchReactors[len(batchReactors)-1])
sources.append(ChemicalSource(400,420,0,[pipes[len(pipes)-1]],20, "B1"))
link_3 = Pipe(640,80,20,320,batchReactors[len(batchReactors)-1])

batchReactors.append(BatchConverter(780,200,6,[1,1,1,0,0,0,0,0],[link_2],"C",70))
Pipe(800,100,20,100,batchReactors[len(batchReactors)-1])
sources.append(ChemicalSource(800,80,0,[pipes[len(pipes)-1]],20,  "C1"))
Pipe(500,220,280,20,batchReactors[len(batchReactors)-1])
sources.append(ChemicalSource(480,220,1,[pipes[len(pipes)-1]],40, "C2"))
Pipe(940,220,-100,20,batchReactors[len(batchReactors)-1])
sources.append(ChemicalSource(940,220,2,[pipes[len(pipes)-1]],20, "C3"))

batchReactors.append(BatchConverter(620,20,7,[1,1,0,0,0,0,0,0],[link_3],"D",70))
Pipe(420,40,200,20,batchReactors[len(batchReactors)-1])
sources.append(ChemicalSource(400,40,0,[pipes[len(pipes)-1]],20, "D1"))
Pipe(880,40,-200,20,batchReactors[len(batchReactors)-1])
sources.append(ChemicalSource(880,40,1,[pipes[len(pipes)-1]],40, "D2"))

controller = Controller(batchReactors, sources, pipes)
if enableLog:
	logger = Logger(logName, controller)

controller.updateControls([  
#							[BaR, Chm, Fuz, Src, Val], 
							[  4,   0,   1,   0,   0.5  ],
							[  4,   0,   2,   0,   0.75 ],
							
							[  4,   0,   1,   1,   0.5  ],
							[  4,   0,   2,   1,   0.75 ],
							
							[  4,   0,   1,   2,   0.5  ],
							[  4,   0,   2,   2,   1    ],
							
							[  4,   0,   1,   3,   0.5  ],
							[  4,   0,   2,   3,   1    ],
							
							[  4,   0,   1,   4,   0.5  ],
							[  4,   0,   2,   4,   1    ],
							
							[  4,   0,   1,   5,   0.5  ],
							[  4,   0,   2,   5,   1    ],
						  ])	

# Add controller buttons
buttons = []
buttons.append(Button("Rule set 1", ( 90, 50), setupRuleSet1, controller))
buttons.append(Button("Rule set 2", (190, 50), setupRuleSet2, controller))
buttons.append(Button("Rule set 3", (290, 50), setupRuleSet3, controller))

y = 126+(3.25*size[1]/10)
buttons.append(Button("+", (120, y), increateDemand, controller, (20, 20)))
buttons.append(Button("-", (160, y), decreateDemand, controller, (20, 20)))

y = 150
for source in sources:
	buttons.append(Button("+", (120, y), increaseThres, source, (20, 20)))
	buttons.append(Button("-", (160, y), decreaseThres, source, (20, 20)))
	y += 25

y = 150
x = 140+(1.6*size[0]/10)

for reactors in batchReactors:
	buttons.append(Button("+", (x,    y), increaseRR, reactors, (20, 20)))
	buttons.append(Button("-", (x+40, y), decreaseRR, reactors, (20, 20)))
	y += 40


resetButton = Button("Reset Simulation", (500, 550), resetSimulation, controller, (130, 30))
resetButton.color = Color.RED
buttons.append(resetButton)

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
					if enableLog:
						logger.writeToFile()
					
		if event.type == pygame.MOUSEBUTTONUP:
			mousebuttondown(buttons, controller)
			
		if event.type == pygame.QUIT:
			exit_flag = 1
				
						
	# Automatically cycle through process every 0.5s
	if auto:
		new_time = pygame.time.get_ticks()
		if (new_time - last_time > 100):
			controller.step()
			if enableLog:
				logger.writeToFile()
			last_time = new_time
			
	# Wash with clean background
	screen.fill(Color.WHITE.value)
	# Draw UI
	pygame.draw.rect(screen, Color.LIGHTGRAY.value, (0, 0, 4*size[0]/10, size[1]), 0)
	pygame.draw.rect(screen, Color.MEDGRAY.value, (25, 100, 1.6*size[0]/10, 3.25*size[1]/10), 0)
	pygame.draw.rect(screen, Color.MEDGRAY.value, (50+(1.6*size[0]/10), 100, 1.6*size[0]/10, 3.25*size[1]/10), 0)
	pygame.draw.rect(screen, Color.MEDGRAY.value, (25, 110+(3.25*size[1]/10), 1.6*size[0]/10, 30), 0)
	
	
	screen.blit(controller.font.render("Source Threshold", True, 
				controller.color.value), [25+(0.25*size[0]/10), 110])
	screen.blit(controller.font.render("Reactor Threshold", True, 
				controller.color.value), [50+(1.825*size[0]/10), 110])
	screen.blit(controller.font.render("Demand: " + str(controller.requiredOut), True, 
				controller.color.value), [30, 115+(3.25*size[1]/10)])
	
	y = 140
	for source in sources:
		screen.blit(controller.font.render(source.name + ": " + str(source.thres), True, 
					controller.color.value), [30, y])
		y += 25
		
	y = 140
	x = 55 + (1.6*size[0]/10)
	for reactors in batchReactors:
		screen.blit(controller.font.render(reactors.name + ": " + str(round(reactors.reactRate, 3)), 
					True, controller.color.value), [x, y])
		y += 40
	
	screen.blit(controller.font.render("Current Rule Set: " + controller.controlName, 
				True, controller.color.value), [120, 10])
	screen.blit(controller.font.render("Steps: " + str(controller.steps), True, 
				controller.color.value), [920, 5])
	
	
	for button in buttons:
		button.draw()
	
	#Draw simulation elements
	draw_x = 50
	for bc in batchReactors:
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
if enableLog:
	logger.closeFile()
pygame.quit()
#quit()

