import pygame 
import sys
from colour import Color
class Button():
    def __init__(self, screen, txt, location, action, input, size=(80, 30), font_name="georgia", font_size=16):
        self.color 	= Color.WHITE  # the static (normal) color
        self.bg 	= Color.WHITE  # actual background color, can change on mouseover
        self.fg 	= Color.BLACK  # text color
        self.size 	= size
        self.font = pygame.font.SysFont(font_name, font_size)
        self.txt = txt
        self.txt_surf = self.font.render(self.txt, 1, self.fg.value)
        self.txt_rect = self.txt_surf.get_rect(center=[s//2 for s in self.size])
        self.screen = screen
        self.surface = pygame.surface.Surface(size)
        self.rect = self.surface.get_rect(center=location)
		
        self.call_back_ = action
        self.input = input
		
		
    def draw(self):
        self.mouseover()

        self.surface.fill(self.bg.value)
        self.surface.blit(self.txt_surf, self.txt_rect)
        self.screen.blit(self.surface, self.rect)

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

