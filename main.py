import pygame
import sys
import math
from PIL import Image, ImageEnhance
# from Lam_chi_can_doc_file_nay import *
import threading
from SokobanSolver import *

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

vietnam = 1

class Map:
    def __init__(self, file_name):
        self.map = []
        self.weight = []
        self.file_name = file_name
        self.read_file(file_name)
    
    def read_file(self, file_name):
        try:
            with open(file_name, 'r') as f:
                weight = f.readline()
                self.weight = [int(x) for x in weight.split()]
                # print(self.weight)
                self.map = f.read()

            
        except FileNotFoundError:
            print(f"File {file_name} không tìm thấy.")

class MapSelectPopup:
    def __init__(self):
        self.is_active = False
        self.maps = []
        
        # Đọc các file từ input-01.txt đến input-10.txt và thêm vào self.maps
        for i in range(1, 11):  # Từ input-01.txt đến input-10.txt
            file_name = f'input-{i:02d}.txt'  # Tạo tên file theo định dạng input-01.txt, input-02.txt, ...
            map_name = f"Map {i:02d}"
            self.maps.append(Map(file_name))
    
        self.button_height = 40
        self.button_margin = 5
        self.popup_width = 300
        self.popup_height = (self.button_height + self.button_margin) * len(self.maps) + 60
        
        # Tạo surface cho popup với alpha
        self.surface = pygame.Surface((self.popup_width, self.popup_height), pygame.SRCALPHA)
        
        # Tính toán vị trí popup để nó xuất hiện ở giữa màn hình
        self.x = (SCREEN_WIDTH - self.popup_width) // 2
        self.y = (SCREEN_HEIGHT - self.popup_height) // 2
        
        # Tạo các button cho từng map
        self.buttons = []
        for i, map in enumerate(self.maps):
            btn_y = 40 + i * (self.button_height + self.button_margin)
            btn = Button(
                20,  # x relative to popup
                btn_y,
                self.popup_width - 40,  # width with margins
                self.button_height,
                'Map ' + map.file_name[6:8],
                GREEN
            )
            self.buttons.append(btn)

    def show(self):
        self.is_active = True

    def hide(self):
        self.is_active = False

    def handle_click(self, pos, game_map):
        if not self.is_active:
            return False
            
        # Convert screen position to popup-relative position
        rel_pos = (pos[0] - self.x, pos[1] - self.y)
        
        # Check if click is outside popup
        if not (0 <= rel_pos[0] <= self.popup_width and 0 <= rel_pos[1] <= self.popup_height):
            self.hide()
            return True
            
        # Check button clicks
        for i, button in enumerate(self.buttons):
            # Adjust button position to be relative to popup
            if button.is_clicked(rel_pos):
                # Load the selected map
                file_name, map_data = self.maps[i].file_name, self.maps[i].map
                game_map.reset()  # Reset current map state
                game_map.original_level = map_data
                game_map.obs_weight = self.maps[i].weight
                # print(game_map.obs_weight)
                game_map.file_name = file_name
                game_map.obs_weight = self.maps[i].weight
                game_map.load_map(map_data)
                self.hide()
                return True
                
        return True
    
    def draw(self, screen):
        if not self.is_active:
            return
            
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        # Reset and fill popup surface
        self.surface.fill((255, 255, 255, 240))  # Semi-transparent white
        
        # Draw popup title
        font = pygame.font.SysFont(None, 36)
        title = font.render("Select Map", True, BLACK)
        title_rect = title.get_rect(centerx=self.popup_width//2, y=10)
        self.surface.blit(title, title_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.surface)
        
        # Draw border
        pygame.draw.rect(self.surface, WHITE, (0, 0, self.popup_width, self.popup_height), 2, border_radius=10)
        
        # Draw popup on screen
        screen.blit(self.surface, (self.x, self.y))

    def update_hover(self, pos):
        if not self.is_active:
            return
            
        # Convert screen position to popup-relative position
        rel_pos = (pos[0] - self.x, pos[1] - self.y)
        
        for button in self.buttons:
            # Update button hover state using relative position
            button.update_hover(rel_pos)

pygame.init()
# Screen setup
info = pygame.display.Info()    
SCREEN_WIDTH = info.current_w - 100
SCREEN_HEIGHT = info.current_h - 100
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Sokoban Game")

pygame.mixer.music.load("music/asian-new-year-celebration-144761.mp3")

# Lặp lại âm thanh
pygame.mixer.music.play(-1)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
# YELLOW = (255, 205, 0)
YELLOW = (240,140,22)
GREEN = (0, 255, 0)
# RED = (255, 0, 0)
RED = (155, 36, 35)
GREEN = (103,182,143)
PANEL_BACKGROUND = (255, 255, 255, 180)  # White with some transparency

# Panel dimensions
PANEL_MARGIN = 20
PANEL_WIDTH = 320

TILE_SIZE = 64
folder = "images2/"

def surface_to_pil(surface):
    """Convert pygame Surface to PIL Image."""
    data = pygame.image.tostring(surface, "RGBA")
    width, height = surface.get_size()
    return Image.frombytes("RGBA", (width, height), data)

def pil_to_surface(pil_img):
    """Convert PIL Image back to pygame Surface."""
    mode = pil_img.mode
    size = pil_img.size
    data = pil_img.tobytes()
    return pygame.image.fromstring(data, size, mode)

def apply_dark_overlay(surface, opacity=0.2):
    # Chuyển pygame Surface sang PIL Image
    pil_img = surface_to_pil(surface)
    
    # Tạo lớp phủ màu đen trong PIL và áp dụng lên ảnh
    overlay = Image.new("RGBA", pil_img.size, (0, 0, 0, int(255 * opacity)))
    darkened_image = Image.alpha_composite(pil_img, overlay)
    
    # Chuyển PIL Image ngược lại sang pygame Surface
    return pil_to_surface(darkened_image.convert("RGBA"))

def load_and_scale_image(filename, size=(TILE_SIZE, TILE_SIZE)):
    try:
        image = pygame.image.load(filename)
        return pygame.transform.scale(image, size)
    except pygame.error as e:
        print(f"Không thể tải hình ảnh {filename}: {e}")
        return None
folder_gach_Viet_Nam = "gachvietnam/"

IMAGES = {
    'box': load_and_scale_image(folder+'box.png'),
    'boxg': load_and_scale_image(folder+'boxg.png'),
    'floor': load_and_scale_image(folder+'floor.png'),
    'goal': load_and_scale_image(folder+'goal.png'),
    'obs': load_and_scale_image(folder+'obs.png'),
    'player_down': load_and_scale_image(folder+'playerD.png'),
    'player_left': load_and_scale_image(folder+'playerL.png'),
    'player_right': load_and_scale_image(folder+'playerR.png'),
    'player_up': load_and_scale_image(folder+'playerU.png'),
    'side_floor': load_and_scale_image(folder+'sidefloor.png'),
    'background': (folder+'background.jpg'),
    'gachvietnam00': apply_dark_overlay(load_and_scale_image(folder_gach_Viet_Nam+'gachvietnam00.png')),
    'gachvietnam01': apply_dark_overlay(load_and_scale_image(folder_gach_Viet_Nam+'gachvietnam01.png')),
    'gachvietnam10': apply_dark_overlay(load_and_scale_image(folder_gach_Viet_Nam+'gachvietnam10.png')),
    'gachvietnam11': apply_dark_overlay(load_and_scale_image(folder_gach_Viet_Nam+'gachvietnam11.png')),
    'khantraiban': load_and_scale_image(folder_gach_Viet_Nam+'khantraiban.png'),
    'ngoinha': (folder_gach_Viet_Nam+'ngoinha.jpg'),
    'duahau': load_and_scale_image(folder_gach_Viet_Nam+'duahau.png'),
    'duahau_g': load_and_scale_image(folder_gach_Viet_Nam+'duahau_g.png'),
    'tuongnha': load_and_scale_image(folder_gach_Viet_Nam+'tuongnha.png'),
}

# Load and scale background image
def load_background(filename):
    try:
        image = pygame.image.load(filename)
        return pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print(f"Couldn't load background image: {e}")
        return None

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
    

class PopupMessage:
    def __init__(self):
        self.is_active = False
        self.message = ""
        self.start_time = 0
        self.duration = 2000  # Default duration
        self.font = pygame.font.SysFont(None, 36)
        self.alpha = 0
        self.fade_speed = 80
        self.is_solution_popup = False  # Flag để xác định loại popup
        
        # Kích thước cho popup thông thường
        self.width = 340
        self.height = 150
        # Kích thước nhỏ hơn cho popup solution
        self.small_width = 240
        self.small_height = 80
        
    def show(self, message, is_solution=False, duration=2000):
        self.message = message
        self.is_active = True
        self.start_time = pygame.time.get_ticks()
        self.alpha = 0
        self.duration = duration
        self.is_solution_popup = is_solution

    def hide(self):
        self.is_active = False
        
    def update(self, current_time):
        if self.is_active:
            # Fade in
            if self.alpha < 255:
                self.alpha = min(255, self.alpha + self.fade_speed)
            
            # Auto hide after duration
            if current_time - self.start_time > self.duration:
                if self.alpha > 0:
                    # self.alpha = max(0, self.alpha - self.fade_speed)
                    self.hide()
                else:
                    self.hide()

    def draw(self, screen):
        if self.is_active:
            # Chọn kích thước dựa vào loại popup
            width = self.small_width if self.is_solution_popup else self.width
            height = self.small_height if self.is_solution_popup else self.height
            
            # Tính toán vị trí
            if self.is_solution_popup:
                # Đặt popup solution ở góc trên bên phải
                popup_x = SCREEN_WIDTH - width - 600
                popup_y = 20
            else:
                # Đặt popup thông thường ở giữa màn hình
                popup_x = (SCREEN_WIDTH - width) // 2
                popup_y = (SCREEN_HEIGHT - height) // 2
            
            # Tạo surface cho popup
            popup_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            
            # Chỉ vẽ overlay mờ cho popup không phải solution
            if not self.is_solution_popup:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, int(self.alpha * 0.5)))
                screen.blit(overlay, (0, 0))
            
            # Vẽ background của popup
            pygame.draw.rect(popup_surface, (255, 255, 255, self.alpha), 
                           (0, 0, width, height), border_radius=10)
            pygame.draw.rect(popup_surface, (100, 100, 100, self.alpha), 
                           (0, 0, width, height), 2, border_radius=10)
            
            # Điều chỉnh font size cho popup solution
            if self.is_solution_popup:
                self.font = pygame.font.SysFont(None, 24)
            else:
                self.font = pygame.font.SysFont(None, 36)
            
            # Render và vẽ text
            text_surface = self.font.render(self.message, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(width//2, height//2))
            
            # Điều chỉnh alpha cho text
            text_surface.set_alpha(self.alpha)
            
            # Vẽ text lên popup surface
            popup_surface.blit(text_surface, text_rect)
            
            # Vẽ popup lên screen
            screen.blit(popup_surface, (popup_x, popup_y))
    
class SokobanMap:
    def __init__(self, level, obs_weight):
        self.popup = PopupMessage()
        self.original_level = level
        self.file_name = "input-01.txt"
        self.obs_weight = obs_weight
        self.load_map(level)
        self.player_direction = 'down'
        self.goals = self.find_goals()
        self.boxes = self.find_boxes()
        self.steps = 0
        self.winning = False
        self.auto_moves = ""
        self.current_move_index = 0
        self.is_auto_playing = False
        self.move_delay = 500
        self.last_move_time = 0
        self.weight = 0
        self.weight_arr = []
        
        

    def start_solving(self, algorithm):
        # Hiện popup "Finding solution..."
        self.popup.show("Finding solution...", is_solution=False, duration=200000)
        
        # Force a complete screen update
        pygame.display.flip()
        pygame.event.pump()  # Process any pending events
        
        # Create a function to handle the solving process
        def solve_process():
            print(self.file_name[6:8], algorithm)
            self.auto_moves, self.weight_arr = solve_with_strategy(self.file_name[6:8], algorithm)
            # print(self.auto_moves)
            # print(self.auto_moves)
            
            # print(solve_with_strategy(self.file_name[6:8], algorithm))
            
            # Update the game state in the main thread using a flag
            self.solution_found = True
            if self.auto_moves:
                self.is_auto_playing = True
                self.current_move_index = 0
            else:
                self.is_auto_playing = False
        
        # Start solving in a separate thread
        solver_thread = threading.Thread(target=solve_process)
        solver_thread.start()
        
    def update(self, current_time):
        # Add this method to handle solution completion
        if hasattr(self, 'solution_found') and self.solution_found:
            self.solution_found = False  # Reset the flag
            if self.auto_moves:
                self.popup.show(f"Solution found! ({len(self.auto_moves)} moves)", 
                              is_solution=True, duration=2000)
            else:
                self.popup.show("No solution found!", is_solution=True, duration=2000)

    def reset(self):
        """Khôi phục bản đồ về trạng thái ban đầu"""
        self.load_map(self.original_level)
        self.player_direction = 'down'
        self.goals = self.find_goals()
        self.boxes = self.find_boxes()
        self.steps = 0
        self.weight = 0
        self.winning = False
        self.current_move_index = 0
        self.is_auto_playing = False

    def load_map(self, level):
        # Chuyển chuỗi bản đồ thành một danh sách các danh sách
        self.map = []
        self.player_pos = None
        i = 0
        for y, line in enumerate(level.split('\n')):
            row = []
            for x, char in enumerate(line):
                if char == '#':
                    row.append('obs')
                elif char == ' ':
                    row.append('floor')
                elif char == '.':
                    row.append('goal')
                elif char == '$':
                    row.append('box'+str(self.obs_weight[i]))
                elif char == '*':
                    row.append('boxg'+str(self.obs_weight[i]))
                elif char == '@':
                    row.append('floor')
                    self.player_pos = [x, y]  # Vị trí của người chơi
                elif char == '+':
                    row.append('goal')
                    self.player_pos = [x, y]
                else:
                    row.append('floor')
            self.map.append(row)


    def find_goals(self):
        return [(x, y) for y, row in enumerate(self.map) 
                for x, cell in enumerate(row) if cell == 'goal' or 'boxg' in cell]

    def find_boxes(self):
        return [(x, y) for y, row in enumerate(self.map) 
                for x, cell in enumerate(row) if 'box' in cell]
    
    def draw(self, screen):
        # print(self.weight)
        # Vẽ nền game area
        # screen.blit(game_area_background, game_area_rect)
        # pygame.draw.rect(screen, BLACK, game_area_rect, 2, border_radius=10)
        
        # Tính toán vị trí để vẽ các phần tử trong game
        # SCREEN_WIDTH - PANEL_WIDTH - 2*PANEL_MARGIN, SCREEN_HEIGHT - 2*PANEL_MARGIN)
        game_area_x = SCREEN_WIDTH - PANEL_WIDTH - 2*PANEL_MARGIN # game_area_rect.x
        game_area_y = SCREEN_HEIGHT - 2*PANEL_MARGIN # game_area_rect.y
        game_area_x = game_area_x // 2 - TILE_SIZE * len(self.map[0]) // 2
        game_area_y = game_area_y // 2 - TILE_SIZE * len(self.map) // 2

        # i = 0
        # Vẽ các phần tử game hiện có
        for y, row in enumerate(self.map):
            for x, cell in enumerate(row):
                # Tính toán tọa độ vẽ với offset từ game_area_rect
                draw_x = game_area_x + (x * TILE_SIZE)
                draw_y = game_area_y + (y * TILE_SIZE)
                
                if vietnam:
                    screen.blit(IMAGES['gachvietnam' + str(y % 2) + str(x % 2)], (draw_x, draw_y))
                else:
                    screen.blit(IMAGES['floor'], (draw_x, draw_y))
                
                if cell == 'goal':
                    if vietnam:
                        screen.blit(IMAGES['khantraiban'], (draw_x, draw_y))
                    else:
                        screen.blit(IMAGES['goal'], (draw_x, draw_y))
                
                if cell == 'obs':
                    screen.blit(IMAGES['obs'], (draw_x, draw_y))
                    
                # elif cell == 'box':
                #     if vietnam:
                #         screen.blit(IMAGES['duahau'], (draw_x, draw_y))
                #     else:
                #         screen.blit(IMAGES['box'], (draw_x, draw_y))
                        
                #     font = pygame.font.SysFont(None, 24)  # Chọn font và kích thước
                #     print(i)
                #     weight_text = font.render(str(self.obs_weight[i]), True, (255, 0, 0))  # Tạo văn bản với giá trị từ self.obs_weight[i]

                #     # Vẽ con số lên vật thể
                #     screen.blit(weight_text, (draw_x + 10, draw_y + 10))  # Điều chỉnh vị trí của con số (thêm 10 pixel để tránh che lên vật thể)

                #     # Tăng giá trị chỉ số i
                #     i += 1
                elif 'boxg' in cell:
                    if vietnam:
                        screen.blit(IMAGES['duahau_g'], (draw_x, draw_y))
                    else:
                        screen.blit(IMAGES['boxg'], (draw_x, draw_y))
                        
                    # Chọn font và kích thước
                    font = pygame.font.SysFont(None, 24)

                    # In ra chỉ số i để kiểm tra
                    # print(i)
                    
                    # Tạo văn bản với giá trị từ self.obs_weight[i]
                    weight_text = font.render(cell[4:], True, (0, 0, 0))  # Chữ màu đen

                    # Lấy kích thước của văn bản để tạo nền trắng vừa vặn
                    text_width, text_height = weight_text.get_size()

                    # Vẽ nền trắng phía sau văn bản
                    pygame.draw.rect(screen, GREEN, (draw_x + 10, draw_y + 10, text_width + 6, text_height + 6))

                    # Vẽ con số lên vật thể với nền trắng
                    screen.blit(weight_text, (draw_x + 10 + 3, draw_y + 10 + 3))  # Vẽ chữ lên với một chút dịch chuyển để nằm trong nền trắng
                        
                elif 'box' in cell:
                    if vietnam:
                        screen.blit(IMAGES['duahau'], (draw_x, draw_y))
                    else:
                        screen.blit(IMAGES['box'], (draw_x, draw_y))

                    # Chọn font và kích thước
                    font = pygame.font.SysFont(None, 24)

                    # In ra chỉ số i để kiểm tra
                    # print(i)
                    
                    # Tạo văn bản với giá trị từ self.obs_weight[i]
                    weight_text = font.render(cell[3:], True, (0, 0, 0))  # Chữ màu đen

                    # Lấy kích thước của văn bản để tạo nền trắng vừa vặn
                    text_width, text_height = weight_text.get_size()

                    # Vẽ nền trắng phía sau văn bản
                    pygame.draw.rect(screen, GREEN, (draw_x + 10, draw_y + 10, text_width + 6, text_height + 6))

                    # Vẽ con số lên vật thể với nền trắng
                    screen.blit(weight_text, (draw_x + 10 + 3, draw_y + 10 + 3))  # Vẽ chữ lên với một chút dịch chuyển để nằm trong nền trắng

        
        # Vẽ người chơi
        player_x = game_area_x + (self.player_pos[0] * TILE_SIZE)
        player_y = game_area_y + (self.player_pos[1] * TILE_SIZE)
        screen.blit(IMAGES[f'player_{self.player_direction}'], (player_x, player_y))

        if self.winning:
            # win_font = pygame.font.SysFont(None, 72)
            # win_text = win_font.render("Congratulations!", True, RED)
            # win_rect = win_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            # screen.blit(win_text, win_rect)
            # draw_victory_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
            victory_screen = VictoryScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
            victory_screen.show()
            victory_screen.draw(screen)


    def move_player(self, dx, dy):
        if dx == 1:
            self.player_direction = 'right'
        elif dx == -1:
            self.player_direction = 'left'
        elif dy == 1:
            self.player_direction = 'down'
        elif dy == -1:
            self.player_direction = 'up'

        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy

        if self.map[new_y][new_x] == 'floor' or self.map[new_y][new_x] == 'goal':
            self.player_pos = [new_x, new_y]
            self.steps += 1
        elif self.map[new_y][new_x].startswith('box'):
            w = ''
            if self.map[new_y][new_x].startswith('boxg'):
                w = self.map[new_y][new_x][4:]
            else:
                w = self.map[new_y][new_x][3:]
                
            self.weight += int(w)
                
            box_new_x = new_x + dx
            box_new_y = new_y + dy
                        
            if self.map[box_new_y][box_new_x] in ['floor', 'goal']:
                self.player_pos = [new_x, new_y]
                self.steps += 1
                
                if self.map[new_y][new_x].startswith('boxg'):
                    self.map[new_y][new_x] = 'goal'
                else:
                    self.map[new_y][new_x] = 'floor'
                
                if self.map[box_new_y][box_new_x] == 'goal':
                    self.map[box_new_y][box_new_x] = 'boxg' + w
                else:
                    self.map[box_new_y][box_new_x] = 'box' + w



        self.check_win()

    def check_win(self):
        current_box_positions = {pos for pos in self.find_boxes()}
        goal_positions = set(self.goals)
        
        if current_box_positions == goal_positions:
            self.winning = True
            self.is_auto_playing = False

    def auto_play(self, current_time):
        if not self.is_auto_playing:
            return
        
        if not self.is_auto_playing or self.winning:
            return

        # Thực hiện di chuyển theo thời gian
        if current_time - self.last_move_time > self.move_delay:
            if self.current_move_index < len(self.auto_moves):
                move = self.auto_moves[self.current_move_index]
                if ord(move) < 96:
                    self.weight += self.weight_arr[self.current_move_index]
                move = move.upper()
                if move == 'L':
                    self.move_player(-1, 0)
                elif move == 'R':
                    self.move_player(1, 0)
                elif move == 'U':
                    self.move_player(0, -1)
                elif move == 'D':
                    self.move_player(0, 1)
                
                self.current_move_index += 1
                self.last_move_time = current_time
            else:
                self.is_auto_playing = False

def main():
    clock = pygame.time.Clock()

    map_popup = MapSelectPopup()
    game_map = SokobanMap(map_popup.maps[0].map, map_popup.maps[0].weight)
    # game_map.obs_weight = 

    # Load background image
    if vietnam:
        background = load_background(IMAGES['ngoinha'])
    else:
        background = load_background(IMAGES['background'])  # Đặt đường dẫn đến hình nền của bạn
    
    # # Create game area surface
    game_area = pygame.Surface((SCREEN_WIDTH - PANEL_WIDTH - 2*PANEL_MARGIN, SCREEN_HEIGHT - 2*PANEL_MARGIN))
    game_area_rect = game_area.get_rect(x=PANEL_MARGIN, y=PANEL_MARGIN)

    # Create panels
    right_panel_x = SCREEN_WIDTH - PANEL_WIDTH - PANEL_MARGIN
    
    stats_panel = Panel(
        right_panel_x, 
        PANEL_MARGIN, 
        PANEL_WIDTH, 
        100, 
        "Statistics"
    )

    # Algorithms panel
    algorithms_panel = Panel(
        right_panel_x,
        stats_panel.rect.bottom + PANEL_MARGIN - 10,
        PANEL_WIDTH,
        220,
        "Algorithms"
    )

    # Controls panel
    controls_panel = Panel(
        right_panel_x,
        algorithms_panel.rect.bottom + PANEL_MARGIN - 10,
        PANEL_WIDTH,
        170,
        "Controls"
    )

    maps_panel = Panel(
        right_panel_x,
        controls_panel.rect.bottom + PANEL_MARGIN - 10,
        PANEL_WIDTH,
        80, 
        "Select Map"
    )

    # Create buttons
    button_width = 160
    button_height = 35
    button_margin = 10

    # Algorithm buttons
    alg_x = algorithms_panel.rect.x + (algorithms_panel.rect.width - button_width) // 2
    auto_play_BFS_btn = Button(alg_x, algorithms_panel.rect.y + 40, 
                              button_width, button_height, "BFS", GREEN)
    auto_play_DFS_btn = Button(alg_x, auto_play_BFS_btn.rect.bottom + button_margin, 
                              button_width, button_height, "DFS", GREEN)
    auto_play_A_star_btn = Button(alg_x, auto_play_DFS_btn.rect.bottom + button_margin, 
                                 button_width, button_height, "A Star", GREEN)
    auto_play_UCS_btn = Button(alg_x, auto_play_A_star_btn.rect.bottom + button_margin, 
                              button_width, button_height, "UCS", GREEN)

    # Control buttons
    ctrl_x = controls_panel.rect.x + (controls_panel.rect.width - button_width) // 2
    pause_btn = Button(ctrl_x, controls_panel.rect.y + 40, 
                      button_width, button_height, "Pause", GRAY)
    continue_btn = Button(ctrl_x, pause_btn.rect.bottom + button_margin, 
                         button_width, button_height, "Continue", YELLOW)
    reset_btn = Button(ctrl_x, continue_btn.rect.bottom + button_margin, 
                      button_width, button_height, "Reset", RED)
    
    map_x = maps_panel.rect.x + (maps_panel.rect.width - button_width) // 2
    select_map_btn = Button(map_x, maps_panel.rect.y + 40,
                          button_width, button_height, "Select Map", GREEN)

    all_buttons = [
        auto_play_BFS_btn, auto_play_DFS_btn, auto_play_A_star_btn, auto_play_UCS_btn,
        pause_btn, continue_btn, reset_btn,
        # map1_btn, map2_btn, map3_btn,
        select_map_btn
    ]

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        
        game_map.update(current_time)
        
        # Update popup
        game_map.popup.update(current_time)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            dur = 600
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if map_popup.is_active:
                    if map_popup.handle_click(mouse_pos, game_map):
                        continue
                    
                if pause_btn.is_clicked(mouse_pos):
                    game_map.is_auto_playing = False
                    game_map.popup.show("Game Paused", is_solution=True, duration=dur)
                
                if auto_play_DFS_btn.is_clicked(mouse_pos):
                    game_map.start_solving("dfs")
                    
                if auto_play_BFS_btn.is_clicked(mouse_pos):
                    game_map.start_solving("bfs")
                    
                if auto_play_A_star_btn.is_clicked(mouse_pos):
                    game_map.start_solving("a*")
                
                if auto_play_UCS_btn.is_clicked(mouse_pos):
                    game_map.start_solving("ucs")
                
                #####
                
                if continue_btn.is_clicked(mouse_pos):
                    game_map.is_auto_playing = True
                    game_map.popup.show("Game Continued", is_solution=True, duration=dur)
                
                if reset_btn.is_clicked(mouse_pos):
                    game_map.reset()
                    game_map.popup.show("Game Reset", is_solution=True, duration=dur)
                    
                if select_map_btn.is_clicked(mouse_pos):
                    map_popup.show()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game_map.move_player(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    game_map.move_player(1, 0)
                elif event.key == pygame.K_UP:
                    game_map.move_player(0, -1)
                elif event.key == pygame.K_DOWN:
                    game_map.move_player(0, 1)

        # Update button hover states
        # for button in all_buttons:
        #     button.update_hover(mouse_pos)
        if map_popup.is_active:
            map_popup.update_hover(mouse_pos)
        else:
            for button in all_buttons:
                button.update_hover(mouse_pos)

        # Automatic play
        game_map.auto_play(current_time)

        # Draw everything
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(YELLOW)

        # Draw semi-transparent game area background
        game_area_background = create_transparent_surface(game_area_rect.width, game_area_rect.height)
        screen.blit(game_area_background, game_area_rect)
        pygame.draw.rect(screen, WHITE, game_area_rect, 2, border_radius=10)
        
        # Draw game
        game_map.draw(screen)
        
        # Draw panels
        stats_panel.draw(screen)
        algorithms_panel.draw(screen)
        controls_panel.draw(screen)
        maps_panel.draw(screen)
        map_popup.draw(screen)

        # Draw statistics
        stats_font = pygame.font.SysFont(None, 32)
        
        steps_text = stats_font.render(f"Steps: {game_map.steps}", True, BLACK)
        steps_bg_rect = steps_text.get_rect(topleft=(stats_panel.rect.x + 20, stats_panel.rect.y + 50))
        steps_bg_rect.inflate_ip(20, 10)
        pygame.draw.rect(screen, WHITE, steps_bg_rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, steps_bg_rect, 1, border_radius=5)
        screen.blit(steps_text, (stats_panel.rect.x + 20, stats_panel.rect.y + 50))
        
        # Vẽ số bước + 3
        steps_plus_text = stats_font.render(f"Weight: {game_map.weight}", True, BLACK)
        # Đặt vị trí cách ô steps 20 pixels
        steps_plus_bg_rect = steps_plus_text.get_rect(topleft=(steps_bg_rect.right + 20, stats_panel.rect.y + 50))
        steps_plus_bg_rect.inflate_ip(20, 10)
        pygame.draw.rect(screen, WHITE, steps_plus_bg_rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, steps_plus_bg_rect, 1, border_radius=5)
        screen.blit(steps_plus_text, (steps_bg_rect.right + 20, stats_panel.rect.y + 50))

        # Draw all buttons
        for button in all_buttons:
            button.draw(screen)

        game_map.popup.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()