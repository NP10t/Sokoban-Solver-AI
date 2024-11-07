import pygame
import sys
import math
# from Lam_chi_can_doc_file_nay import *
from config import *
from images import *
from panel import *
from button import *
from sokobanmap import *


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