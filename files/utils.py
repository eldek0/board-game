import pygame

def text(surface:pygame.Surface, txt:str, position:tuple, FUENTE:pygame.font, COLOR:tuple):
	font_text = FUENTE.render(txt, 1, (COLOR))
	surface.blit(font_text, position)

def text_centered(surface:pygame.Surface, txt:str, rect:pygame.Rect, FUENTE:pygame.font, COLOR:tuple):
	img = FUENTE.render(txt, 1, (COLOR))
	surface.blit(img, img.get_rect(center=rect.center))
