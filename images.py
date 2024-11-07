images_folder = "images/"
from PIL import Image, ImageEnhance
import pygame
from config import *

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

IMAGES = {
    'box': load_and_scale_image(images_folder+'box.png'),
    'boxg': load_and_scale_image(images_folder+'boxg.png'),
    'floor': load_and_scale_image(images_folder+'floor.png'),
    'goal': load_and_scale_image(images_folder+'goal.png'),
    'obs': load_and_scale_image(images_folder+'obs.png'),
    'player_down': load_and_scale_image(images_folder+'playerD.png'),
    'player_left': load_and_scale_image(images_folder+'playerL.png'),
    'player_right': load_and_scale_image(images_folder+'playerR.png'),
    'player_up': load_and_scale_image(images_folder+'playerU.png'),
    'side_floor': load_and_scale_image(images_folder+'sidefloor.png'),
    'background': (images_folder+'background.jpg'),
    'gachvietnam00': apply_dark_overlay(load_and_scale_image(images_folder+'gachvietnam00.png')),
    'gachvietnam01': apply_dark_overlay(load_and_scale_image(images_folder+'gachvietnam01.png')),
    'gachvietnam10': apply_dark_overlay(load_and_scale_image(images_folder+'gachvietnam10.png')),
    'gachvietnam11': apply_dark_overlay(load_and_scale_image(images_folder+'gachvietnam11.png')),
    'khantraiban': load_and_scale_image(images_folder+'khantraiban.png'),
    'ngoinha': (images_folder+'ngoinha.jpg'),
    'duahau': load_and_scale_image(images_folder+'duahau.png'),
    'duahau_g': load_and_scale_image(images_folder+'duahau_g.png'),
    'tuongnha': load_and_scale_image(images_folder+'tuongnha.png'),
}