import pygame
import colorsys

def text(surface:pygame.Surface, txt:str, position:tuple, FUENTE:pygame.font, COLOR:tuple):
	font_text = FUENTE.render(txt, 1, (COLOR))
	surface.blit(font_text, position)

def player_colors(count: int, seed: int) -> tuple[tuple[int, int, int], ...]:
    offset = (seed % 360) / 360
    return tuple(
        tuple(round(c * 255)
              for c in colorsys.hsv_to_rgb((offset + i / count) % 1.0, 0.85, 0.95))
        for i in range(count)
    )