import pygame
import sys

# Khởi tạo Pygame
pygame.init()

# Cài đặt màn hình
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sokoban Game")

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Kích thước ô
TILE_SIZE = 64

folder = "images2/"

# Tải và scale hình ảnh
def load_and_scale_image(filename, size=(TILE_SIZE, TILE_SIZE)):
    try:
        image = pygame.image.load(filename)
        return pygame.transform.scale(image, size)
    except pygame.error as e:
        print(f"Không thể tải hình ảnh {filename}: {e}")
        return None

# Các hình ảnh
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
    'side_floor': load_and_scale_image(folder+'sidefloor.png')
}

# Bản đồ trò chơi
class SokobanMap:
    def __init__(self):
        # Bản đồ với nhiều goals và boxes
        self.map = [
            ['obs', 'obs', 'obs', 'obs', 'obs', 'obs', 'obs', 'obs', 'obs'],
            ['obs', 'floor', 'floor', 'floor', 'floor', 'floor', 'floor', 'floor', 'obs'],
            ['obs', 'floor', 'goal', 'floor', 'floor', 'floor', 'floor', 'floor', 'obs'],
            ['obs', 'floor', 'floor', 'box', 'floor', 'goal', 'floor', 'floor', 'obs'],
            ['obs', 'floor', 'floor', 'floor', 'floor', 'floor', 'floor', 'floor', 'obs'],
            ['obs', 'floor', 'floor', 'floor', 'goal', 'floor', 'floor', 'floor', 'obs'],
            ['obs', 'obs', 'obs', 'obs', 'obs', 'obs', 'obs', 'obs', 'obs']
        ]
        self.player_pos = [1, 1]
        self.player_direction = 'down'
        self.goals = self.find_goals()
        self.boxes = self.find_boxes()

    def find_goals(self):
        return [(x, y) for y, row in enumerate(self.map) 
                for x, cell in enumerate(row) if cell == 'goal']

    def find_boxes(self):
        return [(x, y) for y, row in enumerate(self.map) 
                for x, cell in enumerate(row) if cell == 'box' or cell == 'boxg']

    def draw(self, screen):
        for y, row in enumerate(self.map):
            for x, cell in enumerate(row):
                # Vẽ nền floor cho mọi ô
                screen.blit(IMAGES['floor'], (x * TILE_SIZE, y * TILE_SIZE))
                
                # Vẽ goal nếu là goal
                if cell == 'goal':
                    screen.blit(IMAGES['goal'], (x * TILE_SIZE, y * TILE_SIZE))
                
                # Vẽ obs, box
                if cell == 'obs':
                    screen.blit(IMAGES['obs'], (x * TILE_SIZE, y * TILE_SIZE))
                elif cell == 'box':
                    screen.blit(IMAGES['box'], (x * TILE_SIZE, y * TILE_SIZE))
                elif cell == 'boxg':
                    screen.blit(IMAGES['boxg'], (x * TILE_SIZE, y * TILE_SIZE))
        
        # Vẽ người chơi
        screen.blit(IMAGES[f'player_{self.player_direction}'], 
                    (self.player_pos[0] * TILE_SIZE, self.player_pos[1] * TILE_SIZE))

    def move_player(self, dx, dy):
        # Cập nhật hướng người chơi
        if dx == 1:
            self.player_direction = 'right'
        elif dx == -1:
            self.player_direction = 'left'
        elif dy == 1:
            self.player_direction = 'down'
        elif dy == -1:
            self.player_direction = 'up'

        # Tọa độ mới
        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy

        # Kiểm tra di chuyển hợp lệ
        if self.map[new_y][new_x] == 'floor':
            self.player_pos = [new_x, new_y]
        elif self.map[new_y][new_x] == 'box' or self.map[new_y][new_x] == 'boxg':
            # Kiểm tra có thể đẩy hộp không
            box_new_x = new_x + dx
            box_new_y = new_y + dy
            
            # Nếu ô tiếp theo là floor hoặc goal
            if self.map[box_new_y][box_new_x] in ['floor', 'goal']:
                # Di chuyển người chơi và hộp
                self.player_pos = [new_x, new_y]
                
                # Nếu hộp đang ở goal và được đẩy ra khỏi goal
                if self.map[new_y][new_x] == 'boxg':
                    self.map[new_y][new_x] = 'goal'
                else:
                    self.map[new_y][new_x] = 'floor'
                
                # Nếu đẩy hộp vào goal
                if self.map[box_new_y][box_new_x] == 'goal':
                    self.map[box_new_y][box_new_x] = 'boxg'
                else:
                    self.map[box_new_y][box_new_x] = 'box'

        # Kiểm tra chiến thắng
        self.check_win()

    def check_win(self):
        current_box_positions = {pos for pos in self.find_boxes()}
        goal_positions = set(self.goals)
        
        if current_box_positions == goal_positions:
            print("Chúc mừng! Bạn đã chiến thắng!")
            pygame.quit()
            sys.exit()

# Game loop
def main():
    clock = pygame.time.Clock()
    game_map = SokobanMap()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game_map.move_player(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    game_map.move_player(1, 0)
                elif event.key == pygame.K_UP:
                    game_map.move_player(0, -1)
                elif event.key == pygame.K_DOWN:
                    game_map.move_player(0, 1)

        # Xóa màn hình
        screen.fill(WHITE)
        
        # Vẽ bản đồ
        game_map.draw(screen)
        
        # Cập nhật màn hình
        pygame.display.flip()
        
        # Giới hạn FPS
        clock.tick(10)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()