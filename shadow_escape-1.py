# Shadow Escape: Police Chase
# A simple mobile-friendly Pygame game for Pydroid 3.
# Controls: tap LEFT / RIGHT buttons, or swipe left/right.
# Tap RESTART after a crash.

import random
import pygame

pygame.init()

# Pygame's default window adapts to the device. On Android, run in landscape
# for a wider road if your device supports rotation.
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Shadow Escape: Police Chase")
clock = pygame.time.Clock()

WIDTH, HEIGHT = screen.get_size()
if WIDTH < 320 or HEIGHT < 240:
    screen = pygame.display.set_mode((720, 480))
    WIDTH, HEIGHT = screen.get_size()

FONT = pygame.font.Font(None, max(24, HEIGHT // 22))
SMALL = pygame.font.Font(None, max(18, HEIGHT // 30))
BIG = pygame.font.Font(None, max(42, HEIGHT // 10))

# Colors
DARK = (13, 18, 32)
ROAD = (48, 51, 60)
ROAD_EDGE = (225, 220, 190)
LANE = (235, 230, 205)
WHITE = (245, 245, 245)
RED = (230, 55, 65)
BLUE = (60, 145, 245)
YELLOW = (250, 205, 65)
GREEN = (70, 210, 125)
GREY = (100, 110, 125)

ROAD_WIDTH = int(WIDTH * 0.62)
ROAD_LEFT = (WIDTH - ROAD_WIDTH) // 2
ROAD_RIGHT = ROAD_LEFT + ROAD_WIDTH
LANES = 3
LANE_WIDTH = ROAD_WIDTH // LANES
CAR_W = max(34, LANE_WIDTH // 2)
CAR_H = max(58, int(CAR_W * 1.55))
PLAYER_Y = int(HEIGHT * 0.72)

def lane_x(lane):
    return ROAD_LEFT + lane * LANE_WIDTH + LANE_WIDTH // 2

def draw_car(surface, x, y, color, police=False):
    rect = pygame.Rect(int(x - CAR_W // 2), int(y - CAR_H // 2), CAR_W, CAR_H)
    pygame.draw.rect(surface, color, rect, border_radius=max(5, CAR_W // 7))
    # Windows
    window = pygame.Rect(rect.x + CAR_W // 5, rect.y + CAR_H // 5,
                         CAR_W * 3 // 5, CAR_H // 4)
    pygame.draw.rect(surface, (25, 35, 50), window, border_radius=4)
    # Headlights
    pygame.draw.rect(surface, YELLOW, (rect.x + 4, rect.y + 3, max(5, CAR_W // 5), 5))
    pygame.draw.rect(surface, YELLOW, (rect.right - max(5, CAR_W // 5) - 4, rect.y + 3,
                                       max(5, CAR_W // 5), 5))
    # Rear lights
    pygame.draw.rect(surface, RED, (rect.x + 4, rect.bottom - 7, max(5, CAR_W // 5), 4))
    pygame.draw.rect(surface, RED, (rect.right - max(5, CAR_W // 5) - 4, rect.bottom - 7,
                                    max(5, CAR_W // 5), 4))
    if police:
        bar_y = rect.y + CAR_H // 3
        pygame.draw.rect(surface, RED, (rect.x + CAR_W // 5, bar_y, CAR_W // 3, 6))
        pygame.draw.rect(surface, BLUE, (rect.x + CAR_W // 2, bar_y, CAR_W // 3, 6))
    return rect

def draw_text(text, font, color, center):
    image = font.render(text, True, color)
    screen.blit(image, image.get_rect(center=center))

def new_game():
    return {
        "player_lane": 1,
        "traffic": [],
        "score": 0.0,
        "speed": 4.0,
        "spawn_timer": 0,
        "road_offset": 0,
        "game_over": False,
        "police_y": int(HEIGHT * 0.90),
        "best": best_score,
    }

try:
    best_score = int(open("shadow_escape_best.txt", "r").read().strip())
except Exception:
    best_score = 0

game = new_game()
touch_left = pygame.Rect(int(WIDTH * 0.06), int(HEIGHT * 0.82), int(WIDTH * 0.22), int(HEIGHT * 0.13))
touch_right = pygame.Rect(int(WIDTH * 0.72), int(HEIGHT * 0.82), int(WIDTH * 0.22), int(HEIGHT * 0.13))

def draw_button(rect, label):
    pygame.draw.rect(screen, (38, 48, 70), rect, border_radius=12)
    pygame.draw.rect(screen, (125, 150, 185), rect, width=2, border_radius=12)
    draw_text(label, FONT, WHITE, rect.center)

running = True
while running:
    dt = min(clock.tick(60) / 16.6667, 2.0)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                running = False
            if not game["game_over"]:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    game["player_lane"] = max(0, game["player_lane"] - 1)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    game["player_lane"] = min(LANES - 1, game["player_lane"] + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                game = new_game()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            px, py = event.pos
            if game["game_over"]:
                restart_rect = pygame.Rect(WIDTH // 2 - int(WIDTH * .19), HEIGHT // 2 + int(HEIGHT * .10),
                                           int(WIDTH * .38), int(HEIGHT * .12))
                if restart_rect.collidepoint(px, py) or True:
                    game = new_game()
            else:
                if touch_left.collidepoint(px, py):
                    game["player_lane"] = max(0, game["player_lane"] - 1)
                elif touch_right.collidepoint(px, py):
                    game["player_lane"] = min(LANES - 1, game["player_lane"] + 1)
        elif event.type == pygame.FINGERDOWN:
            px, py = int(event.x * WIDTH), int(event.y * HEIGHT)
            if game["game_over"]:
                game = new_game()
            else:
                if px < WIDTH // 2:
                    game["player_lane"] = max(0, game["player_lane"] - 1)
                else:
                    game["player_lane"] = min(LANES - 1, game["player_lane"] + 1)

    # Background and road
    screen.fill(DARK)
    pygame.draw.rect(screen, (20, 48, 42), (0, 0, ROAD_LEFT, HEIGHT))
    pygame.draw.rect(screen, (20, 48, 42), (ROAD_RIGHT, 0, WIDTH - ROAD_RIGHT, HEIGHT))
    pygame.draw.rect(screen, ROAD, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))
    pygame.draw.line(screen, ROAD_EDGE, (ROAD_LEFT + 4, 0), (ROAD_LEFT + 4, HEIGHT), 4)
    pygame.draw.line(screen, ROAD_EDGE, (ROAD_RIGHT - 4, 0), (ROAD_RIGHT - 4, HEIGHT), 4)

    if not game["game_over"]:
        game["score"] += 0.12 * game["speed"] * dt
        game["speed"] = min(10.0, 4.0 + game["score"] / 90)
        game["road_offset"] = (game["road_offset"] + game["speed"] * 8 * dt) % 70

        # Dashed lane markers
        for lane in range(1, LANES):
            x = ROAD_LEFT + lane * LANE_WIDTH
            for y in range(-70, HEIGHT + 70, 70):
                yy = int(y + game["road_offset"])
                pygame.draw.rect(screen, LANE, (x - 3, yy, 6, 34), border_radius=2)

        # Traffic spawning
        game["spawn_timer"] += dt
        if game["spawn_timer"] > max(17, 48 - game["speed"] * 2):
            game["spawn_timer"] = 0
            lane = random.randrange(LANES)
            # Avoid spawning directly in the player's lane close by.
            if lane != game["player_lane"] or random.random() > 0.35:
                game["traffic"].append({
                    "lane": lane,
                    "y": -CAR_H,
                    "color": random.choice([RED, BLUE, YELLOW, GREY, (160, 90, 210)]),
                })

        # Move traffic and check collisions
        player_x = lane_x(game["player_lane"])
        player_rect = pygame.Rect(player_x - CAR_W // 2, PLAYER_Y - CAR_H // 2, CAR_W, CAR_H)
        for car in game["traffic"]:
            car["y"] += game["speed"] * 7 * dt
            car_rect = pygame.Rect(lane_x(car["lane"]) - CAR_W // 2,
                                   int(car["y"] - CAR_H // 2), CAR_W, CAR_H)
            if player_rect.colliderect(car_rect):
                game["game_over"] = True
            draw_car(screen, lane_x(car["lane"]), car["y"], car["color"])
        game["traffic"] = [car for car in game["traffic"] if car["y"] < HEIGHT + CAR_H]

        # Player and pursuing police car
        draw_car(screen, player_x, PLAYER_Y, GREEN)
        police_y = int(HEIGHT * 0.90 - min(HEIGHT * 0.13, game["score"] * 0.2))
        draw_car(screen, player_x, police_y, WHITE, police=True)

        # HUD
        draw_text("SHADOW ESCAPE", SMALL, WHITE, (WIDTH // 2, 24))
        draw_text("SCORE: " + str(int(game["score"])), FONT, YELLOW, (WIDTH // 2, 58))
        draw_text("BEST: " + str(best_score), SMALL, WHITE, (WIDTH // 2, 88))
        draw_button(touch_left, "◀ LEFT")
        draw_button(touch_right, "RIGHT ▶")

    else:
        # Freeze and draw the road/traffic, then show game-over panel.
        for lane in range(1, LANES):
            x = ROAD_LEFT + lane * LANE_WIDTH
            pygame.draw.line(screen, LANE, (x, 0), (x, HEIGHT), 2)
        draw_text("GAME OVER", BIG, RED, (WIDTH // 2, HEIGHT // 2 - int(HEIGHT * .12)))
        draw_text("Score: " + str(int(game["score"])), FONT, WHITE,
                  (WIDTH // 2, HEIGHT // 2 - int(HEIGHT * .02)))
        draw_text("Tap anywhere to restart", SMALL, WHITE,
                  (WIDTH // 2, HEIGHT // 2 + int(HEIGHT * .07)))
        draw_text("Best: " + str(best_score), SMALL, YELLOW,
                  (WIDTH // 2, HEIGHT // 2 + int(HEIGHT * .17)))

        if int(game["score"]) > best_score:
            best_score = int(game["score"])
            try:
                with open("shadow_escape_best.txt", "w") as f:
                    f.write(str(best_score))
            except Exception:
                pass

    pygame.display.flip()

pygame.quit()
