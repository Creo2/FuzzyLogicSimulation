import sys
import pygame
import numpy
import random
from controller import Controller, get_output_rate
from colour import get_colors,Color
from button import Button, mousebuttondown
from components import BatchConverter,Pipe, ChemicalSource

colours = get_colors()

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
								[  1,   7,   1,   0,   2    ],
								[  1,   7,   2,   0,   4    ],
								[  1,   0,   0,   0,   1    ],
								[  1,   0,   1,   0,   -1.75],
								[  1,   0,   2,   0,   -4   ],
																
								[  2,   0,   0,   1,   1    ],
								[  2,   0,   1,   1,   0.25 ],
								[  0,   5,   1,   1,   2    ],
								[  0,   5,   2,   1,   4    ],
								[  0,   6,   1,   1,   -2   ],
								[  0,   6,   2,   1,   -4   ],
								[  0,   6,   2,   1,   -4   ],
								
								
								[  2,   0,   1,   2,   2    ],
								[  2,   0,   2,   2,   4    ],
								[  2,   1,   0,   2,   1    ],
								[  2,   1,   1,   2,   -1.75],
								[  2,   1,   2,   2,   -4   ],
								
								[  2,   0,   1,   3,   2    ],
								[  2,   0,   2,   3,   4    ],
								[  2,   2,   0,   3,   1    ],
								[  2,   2,   1,   3,   -1.75],
								[  2,   2,   2,   3,   -4   ],
								
								[  4,   0,   0,   4,   -0.5  ],
								[  4,   0,   1,   4,   0.25  ],
								[  4,   0,   2,   4,   1     ],
								[  3,   0,   2,   4,   -1    ],
								
								[  3,   0,   1,   5,   2    ],
								[  3,   0,   2,   5,   4    ],
								[  3,   1,   0,   5,   1    ],
								[  3,   1,   1,   5,   0.5  ],
								[  3,   1,   1,   5,   -1.75],
								[  3,   1,   2,   5,   -4   ],
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
pipes.append(link_0)
batchReactors.append(BatchConverter(780,400,4,[0,0,0,0,0,1,1,0],[link_0],"A",70))
link_1 = Pipe(680,420,100,20,batchReactors[len(batchReactors)-1])
pipes.append(link_1)
link_2 = Pipe(800,260,20,140,batchReactors[len(batchReactors)-1])
pipes.append(link_2)

batchReactors.append(BatchConverter(620,400,5,[1,0,0,0,0,0,0,1],[link_1],"B",70))
pipes.append(Pipe(420,420,200,20,batchReactors[len(batchReactors)-1]))
sources.append(ChemicalSource(400,420,0,[pipes[len(pipes)-1]],20, "B1"))
link_3 = Pipe(640,80,20,320,batchReactors[len(batchReactors)-1])
pipes.append(link_3)

batchReactors.append(BatchConverter(780,200,6,[1,1,1,0,0,0,0,0],[link_2],"C",70))
pipes.append(Pipe(800,100,20,100,batchReactors[len(batchReactors)-1]))
sources.append(ChemicalSource(800,80,0,[pipes[len(pipes)-1]],20,  "C1"))
pipes.append(Pipe(500,220,280,20,batchReactors[len(batchReactors)-1]))
sources.append(ChemicalSource(480,220,1,[pipes[len(pipes)-1]],40, "C2"))
pipes.append(Pipe(940,220,-100,20,batchReactors[len(batchReactors)-1]))
sources.append(ChemicalSource(940,220,2,[pipes[len(pipes)-1]],20, "C3"))

batchReactors.append(BatchConverter(620,20,7,[1,1,0,0,0,0,0,0],[link_3],"D",70))
pipes.append(Pipe(420,40,200,20,batchReactors[len(batchReactors)-1]))
sources.append(ChemicalSource(400,40,0,[pipes[len(pipes)-1]],20, "D1"))
pipes.append(Pipe(880,40,-200,20,batchReactors[len(batchReactors)-1]))
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
buttons.append(Button(screen,"Rule set 1", ( 90, 50), setupRuleSet1, controller))
buttons.append(Button(screen,"Rule set 2", (190, 50), setupRuleSet2, controller))
buttons.append(Button(screen,"Rule set 3", (290, 50), setupRuleSet3, controller))

y = 126+(3.25*size[1]/10)
buttons.append(Button(screen,"+", (120, y), increateDemand, controller, (20, 20)))
buttons.append(Button(screen,"-", (160, y), decreateDemand, controller, (20, 20)))

y = 150
for source in sources:
	buttons.append(Button(screen,"+", (120, y), increaseThres, source, (20, 20)))
	buttons.append(Button(screen,"-", (160, y), decreaseThres, source, (20, 20)))
	y += 25

y = 150
x = 140+(1.6*size[0]/10)

for reactors in batchReactors:
	buttons.append(Button(screen,"+", (x,    y), increaseRR, reactors, (20, 20)))
	buttons.append(Button(screen,"-", (x+40, y), decreaseRR, reactors, (20, 20)))
	y += 40


resetButton = Button(screen,"Reset Simulation", (500, 550), resetSimulation, controller, (130, 30))
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
			# User hit the M key -> toggle membership function
			if event.key == pygame.K_m:
				controller.membership_f += 1
				if (controller.membership_f > 2):
					controller.membership_f = 0
				
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
	screen.blit(controller.font.render("Current Membership Function: " + controller.membership_names[controller.membership_f], 
				True, controller.color.value), [60, 80])
	screen.blit(controller.font.render("Steps: " + str(controller.steps), True, 
				controller.color.value), [920, 5])
	
	
	for button in buttons:
		button.draw()
	
	#Draw simulation elements
	draw_x = 50
	for bc in batchReactors:
		bc.render(screen)
		bc.report(draw_x,screen)
		draw_x += 80
	for pipe in pipes:
		pipe.render(screen)
	for source in sources:
		source.render(screen)

	
	# Update screen with new contents
	pygame.display.flip()
	# Limit fps
	# clock.tick(10)

# We're out of the game loop so shut things down
if enableLog:
	logger.closeFile()
pygame.quit()
#quit()

