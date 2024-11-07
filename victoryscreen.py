import pygame
import math
class VictoryScreen:
    def __init__(self, screen_width, screen_height):
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.show_time = 0
        self.is_showing = False
        self.fade_alpha = 255  # Độ trong suốt
        
        # Màu sắc
        self.RED = (255, 0, 0)
        self.GOLD = (255, 215, 0)
        self.WHITE = (255, 255, 255)
        
        # Khởi tạo font nhỏ hơn
        try:
            self.win_font = pygame.font.Font("freesansbold.ttf", 36)  # Giảm kích thước font chính
        except:
            self.win_font = pygame.font.SysFont(None, 36)
        self.sub_font = pygame.font.SysFont(None, 24)  # Giảm kích thước font phụ
        
        # Surface trong suốt để làm hiệu ứng fade
        self.overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        
    def show(self):
        self.show_time = pygame.time.get_ticks()
        self.is_showing = True
        self.fade_alpha = 255
        
    def draw(self, screen):
        if not self.is_showing:
            return
            
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.show_time
        
        # Bắt đầu fade out sau 2 giây
        if elapsed_time > 2000:  # 2000ms = 2 giây
            # Giảm độ trong suốt trong 1 giây
            fade_progress = (elapsed_time - 2000) / 1000  # 1000ms = 1 giây
            self.fade_alpha = max(0, 255 * (1 - fade_progress))
            
            # Kết thúc hiển thị khi đã fade out hoàn toàn
            if self.fade_alpha <= 0:
                self.is_showing = False
                return
        
        # Xóa overlay
        self.overlay.fill((0, 0, 0, 0))
        
        # Text chính với hiệu ứng bóng đổ
        win_text = self.win_font.render("Congratulations!", True, self.GOLD)
        shadow_text = self.win_font.render("Congratulations!", True, self.RED)
        
        # Vị trí text
        win_rect = win_text.get_rect(center=(self.SCREEN_WIDTH//2, self.SCREEN_HEIGHT//2))
        shadow_rect = shadow_text.get_rect(center=(self.SCREEN_WIDTH//2 + 2, self.SCREEN_HEIGHT//2 + 2))  # Giảm khoảng cách bóng đổ
        
        # Vẽ các ngôi sao
        time = current_time / 1000
        for i in range(8):
            angle = time + i * math.pi/4
            star_x = self.SCREEN_WIDTH//2 + math.cos(angle) * 80  # Giảm khoảng cách ngôi sao
            star_y = self.SCREEN_HEIGHT//2 + math.sin(angle) * 80
            
            points = []
            for j in range(5):
                point_angle = angle + j * 2 * math.pi/5
                points.append((
                    star_x + math.cos(point_angle) * 10,  # Giảm kích thước ngôi sao
                    star_y + math.sin(point_angle) * 10
                ))
            pygame.draw.polygon(self.overlay, (*self.GOLD, self.fade_alpha), points)
        
        # Vẽ khung viền
        border_width = 5  # Giảm độ rộng của khung viền
        pygame.draw.rect(self.overlay, (*self.GOLD, self.fade_alpha), (
            self.SCREEN_WIDTH//2 - win_rect.width//2 - 10,
            self.SCREEN_HEIGHT//2 - win_rect.height//2 - 10,
            win_rect.width + 20,
            win_rect.height + 20
        ), border_width)
        
        # Vẽ text với opacity
        shadow_surface = pygame.Surface(shadow_text.get_size(), pygame.SRCALPHA)
        shadow_surface.blit(shadow_text, (0, 0))
        shadow_surface.set_alpha(self.fade_alpha)
        
        text_surface = pygame.Surface(win_text.get_size(), pygame.SRCALPHA)
        text_surface.blit(win_text, (0, 0))
        text_surface.set_alpha(self.fade_alpha)
        
        # Vẽ lên overlay
        self.overlay.blit(shadow_surface, shadow_rect)
        self.overlay.blit(text_surface, win_rect)
        
        def draw_text_with_border(surface, text, font, position, text_color, border_color, border_width=1):  # Giảm độ rộng viền
            text_surface = font.render(text, True, text_color)
            text_rect = text_surface.get_rect(center=position)

            # Tạo các bản sao của text dịch chuyển theo các hướng để tạo viền
            for dx, dy in [(-border_width, 0), (border_width, 0), (0, -border_width), (0, border_width),
                        (-border_width, -border_width), (border_width, -border_width),
                        (-border_width, border_width), (border_width, border_width)]:
                border_surface = font.render(text, True, border_color)
                surface.blit(border_surface, text_rect.move(dx, dy))

            # Vẽ text chính ở trung tâm
            surface.blit(text_surface, text_rect)
        
        # Vẽ text phụ
        if elapsed_time < 2000:  # Chỉ hiển thị trong 2 giây đầu
            sub_text = "CLICK RESET TO REPLAY!"
            sub_font = self.sub_font
            sub_position = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 60)  # Giảm khoảng cách text phụ
            
            # Tạo một Surface bán trong suốt cho text
            sub_surface = pygame.Surface(self.sub_font.size(sub_text), pygame.SRCALPHA)
            draw_text_with_border(sub_surface, sub_text, sub_font, sub_surface.get_rect(center=(sub_surface.get_width() // 2, sub_surface.get_height() // 2)).center, self.GOLD, self.RED)
            
            sub_surface.set_alpha(self.fade_alpha)  # Đặt độ mờ cho text
            sub_rect = sub_surface.get_rect(center=sub_position)
            self.overlay.blit(sub_surface, sub_rect)
        
        # Vẽ overlay lên màn hình chính
        screen.blit(self.overlay, (0, 0))