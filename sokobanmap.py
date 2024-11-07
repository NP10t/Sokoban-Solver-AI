import pygame
from button import *
from images import *
from victoryscreen import VictoryScreen
import threading
from sokobansolver import *


vietnam = 1


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


# Load and scale background image
def load_background(filename):
    try:
        image = pygame.image.load(filename)
        return pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print(f"Couldn't load background image: {e}")
        return None

    

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
                    i+=1
                elif char == '*':
                    row.append('boxg'+str(self.obs_weight[i]))
                    i+=1
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
                
            # print(w)
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