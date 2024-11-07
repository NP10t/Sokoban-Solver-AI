import pygame
PANEL_BACKGROUND = (255, 255, 255, 180)  # White with some transparency
from config import *

# Create a transparent surface for panels
def create_transparent_surface(width, height, alpha=140):
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill((255, 255, 255, alpha))
    return surface

class Panel:
    def __init__(self, x, y, width, height, title):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.color = PANEL_BACKGROUND
        self.border_color = WHITE
        self.title_font = pygame.font.SysFont(None, 24)
        self.transparent_surface = create_transparent_surface(width, height)

    def draw(self, surface):
        # Draw semi-transparent background
        surface.blit(self.transparent_surface, self.rect)
        
        # Draw border
        pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=10)
        
        # Draw title with background
        title_surface = self.title_font.render(self.title, True, BLACK)
        title_rect = title_surface.get_rect(
            midtop=(self.rect.centerx, self.rect.top + 10)
        )
        
        # Draw title background
        title_bg_rect = title_rect.copy()
        title_bg_rect.inflate_ip(20, 10)
        pygame.draw.rect(surface, WHITE, title_bg_rect, border_radius=5)
        pygame.draw.rect(surface, self.border_color, title_bg_rect, 1, border_radius=5)
        
        # Draw title text
        surface.blit(title_surface, title_rect)