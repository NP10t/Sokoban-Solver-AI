from config import *
import pygame

class Button:
    def __init__(self, x, y, width, height, text, color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = color
        self.hover_color = tuple(max(0, min(255, c + 30)) for c in color)
        self.current_color = color
        self.text_color = text_color
        self.font = pygame.font.SysFont(None, 28)
        self.is_hovered = False

    def draw(self, surface):
        # Update color based on hover state
        self.current_color = self.hover_color if self.is_hovered else self.base_color
        
        # Draw button background with slight transparency
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*self.current_color, 230), s.get_rect(), border_radius=5)
        surface.blit(s, self.rect)
        
        # Draw border
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def update_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)