import pygame
from math import sqrt

# Initializing Pygame
pygame.init()

# Setting the screen
desktop_info = pygame.display.Info()
screen = pygame.display.set_mode((desktop_info.current_w, desktop_info.current_h))
display_size = screen.get_size()
pygame.mouse.set_visible(False)

# Display info
width = display_size[0]
height = display_size[1]
center = (display_size[0] / 2, display_size[1] / 2)

# Setting boundaries
walls_distance = width / 4
right_limit = center[0] + walls_distance - 50
left_limit = center[0] - walls_distance

# Setting ball
ball_x = center[0]
ball_y = center[1] + 150
ball_dx = sqrt(1/4)
ball_dy = sqrt(1/4)
ball_colour = (209, 209, 209)
top_speed = sqrt(ball_dx ** 2 + ball_dy ** 2)

# Setting bricks
bricks_distance = (right_limit - left_limit + 55) / 14
brick_width = 60
brick_height = 16
bricks = []
bricks_x = []
bricks_y = []

# bricks RGB colours
colours = [(161, 9, 0), (199, 127, 0), (0, 129, 35), (198, 199, 24)]

for i in range(14):
    bricks_x.append(int(left_limit + 10 + bricks_distance * i))
for j in range(8):
    bricks_y.append(int(height * 0.2 + (bricks_distance - 45) * j))

for j in range(8):
    for i in range(14):
        bricks.append([bricks_x[i], bricks_y[j]])

# Creating an auxiliary list of bricks
initial_bricks = []

for i in range(len(bricks)):
    initial_bricks.append(bricks[i])

brick_count = len(bricks)

# Player initial coordinates ((screen width - player width)/2)
player_x = (width - 32) / 2
player_y = height - 50
player_colour = (0, 129, 198)

hud_font = pygame.font.SysFont('unispacebold', 80)
hud_colour = (208, 208, 208)

sound = pygame.mixer.Sound('blip.wav')

start = False
breather = False
done = False


# Mouse-controlled player movement
def player_movement():
    global player_x

    right_dist = right_limit - player_x + 5
    left_dist = player_x - left_limit - 17
    speed_limit = 15
    mouse_movement = pygame.mouse.get_rel()[0]

    # If player move right
    if mouse_movement > 0 and player_x < right_limit + 5:
        if right_dist > speed_limit and mouse_movement > speed_limit:
            player_x += speed_limit
        elif right_dist > mouse_movement and speed_limit > mouse_movement:
            player_x += mouse_movement
        elif right_dist < speed_limit and right_dist < mouse_movement:
            player_x += right_dist

    # If player moves left
    if mouse_movement < 0 and player_x > left_limit + 17:
        if left_dist > speed_limit and abs(mouse_movement) > speed_limit:
            player_x += -speed_limit
        elif left_dist > abs(mouse_movement) and speed_limit > abs(mouse_movement):
            player_x += mouse_movement
        elif left_dist < speed_limit and left_dist < abs(mouse_movement):
            player_x += -left_dist


# Resetting mouse to the center of the screen
def reset_mouse_position():
    if pygame.mouse.get_pos()[0] > 600 or pygame.mouse.get_pos()[0] < 400:
        pygame.mouse.set_pos(512, 360)
    if pygame.mouse.get_pos()[1] > 500 or pygame.mouse.get_pos()[1] < 200:
        pygame.mouse.set_pos(512, 360)


def ball_collision():
    global ball_x, ball_y, ball_dx, ball_dy, score, brick_count, lives, level, breather, top_speed

    player_center = player_x + 20

    # Ball collision with walls
    if ball_x < left_limit + 17:
        ball_x = left_limit + 17
        ball_dx *= -1
        pygame.mixer.Sound.play(sound)
    if ball_x > right_limit + 40:
        ball_x = right_limit + 40
        ball_dx *= -1
        pygame.mixer.Sound.play(sound)

    # Ball collision with ceiling
    if ball_y < height * 0.03:
        ball_dy *= -1
        pygame.mixer.Sound.play(sound)

    if start:
        # Ball collision with player
        if player_x < ball_x + 9 < player_x + 49 and player_y - 9 < ball_y < player_y:
            if ball_dy > 0:
                ball_dx = ((ball_x + 4 - player_center)/25)
                dx_square = ((ball_dx**2) * top_speed / (ball_dx**2 + ball_dy**2))
                dy_square = top_speed - dx_square

                if ball_dx < 0:
                    ball_dx = -sqrt(dx_square)
                else:
                    ball_dx = sqrt(dx_square)
                ball_dy = sqrt(dy_square)
                ball_dy *= -1
                pygame.mixer.Sound.play(sound)

    # Ball collision with floor on start screen
    else:
        if player_y - 9 < ball_y < player_y:
            ball_dy *= -1
            pygame.mixer.Sound.play(sound)

    # Player misses the ball and loses 1 life
    if ball_y > height:
        ball_y = center[1] + 150
        lives -= 1
        level = 1
        ball_dx = sqrt(1 / 4)
        ball_dy = sqrt(1 / 4)
        top_speed = sqrt(ball_dx ** 2 + ball_dy ** 2)
        breather = True

    # Collision with bricks
    for k in range(len(bricks)):
        if bricks[k][0] < ball_x + 9 < bricks[k][0] + brick_width + 9:
            if ball_dy < 0 and bricks[k][1] + brick_height > ball_y > bricks[k][1] + brick_height - 8:
                if start:
                    score += 1 + 2*(int((111 - k)/28))
                    bricks[k] = [width+5, height+5]
                    brick_count -= 1
                ball_dy *= -1
                sound.play(2*(int((111 - k)/28)))

                # Level up and faster ball
                if ((111 - k) / 28) >= level:
                    level += int(((111 - k) / 28)/2)
                    top_speed *= (level + 2)/3
                    ball_dx *= (level + 2)/3
                    ball_dy *= (level + 2)/3

            # Collision with bricks from above
            elif ball_dy > 0 and ball_y == bricks[k][1]:
                if start:
                    score += 1 + 2 * (int((111 - k) / 28))
                    bricks[k] = [width+5, height+5]
                    brick_count -= 1
                ball_dy *= -1
                pygame.mixer.Sound.play(sound)

                # Level up and faster ball
                if (int((111 - k) / 28))/2 >= level:
                    level += (int((112 - k) / 28))/2
                    top_speed += (level + 3)/4
                    ball_dx += (level + 3) / 4
                    ball_dy += (level + 3) / 4


def draw_ball():
    global ball_x, ball_y

    ball = pygame.Rect(ball_x, ball_y, 10, 9)
    ball_x += ball_dx
    ball_y += ball_dy
    pygame.draw.rect(screen, ball_colour, ball)


def draw_wall():
    ceiling = pygame.Rect(left_limit, 0, (walls_distance * 2), (height * 0.03))
    left_wall = pygame.Rect(left_limit, 0, 17, height)
    right_wall = pygame.Rect(right_limit + 45, 0, 17, height)
    pygame.draw.rect(screen, ball_colour, ceiling)
    pygame.draw.rect(screen, ball_colour, left_wall)
    pygame.draw.rect(screen, ball_colour, right_wall)


def draw_bricks():
    for k in range(len(bricks)):
        brick = pygame.Rect(bricks[k][0], bricks[k][1], brick_width, brick_height)
        pygame.draw.rect(screen, colours[int(k / (14 * 2))], brick)


def draw_hud():
    hud_player = hud_font.render(f"1", False, hud_colour)
    hud_lives = hud_font.render(f"{4 - lives}", False, hud_colour)
    hud_score = hud_font.render(f"{score:03}", False, hud_colour)
    hud_null = hud_font.render(f"000", False, hud_colour)
    screen.blit(hud_player, (left_limit + 40, 40))
    screen.blit(hud_lives, (center[0] + 40, 40))
    screen.blit(hud_score, (left_limit + 100, 120))
    screen.blit(hud_null, (center[0] + 100, 120))


# Initial stats
lives = 3
score = 0
level = 1

# Game loop
while not done:
    screen.fill('black')

    # Winning or losing
    if brick_count == 0 or lives == 0:
        start = False

    # Quitting
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN and (event.key == pygame.K_q or event.key == pygame.K_ESCAPE):
            done = True

    # Start screen
    while not start and not done:
        screen.fill('black')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_q or event.key == pygame.K_ESCAPE):
                done = True

            # Mouse button to start the game
            if event.type == pygame.MOUSEBUTTONDOWN:
                start = True
                breather = True
                brick_count = 112
                lives = 3
                score = 0

                for i in range(len(bricks)):
                    bricks[i] = initial_bricks[i]

        # Floor on start screen
        floor = pygame.Rect(left_limit, player_y, walls_distance * 2, 15)
        pygame.draw.rect(screen, player_colour, floor)

        draw_ball()
        ball_collision()
        draw_bricks()
        draw_wall()
        draw_hud()

        reset_mouse_position()

        pygame.display.flip()

    # Breather
    while breather and not done:
        screen.fill('black')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_q or event.key == pygame.K_ESCAPE):
                done = True

            # Mouse button to launch the ball
            if event.type == pygame.MOUSEBUTTONDOWN:
                breather = False
                ball_y = center[1] + 150
                ball_dy = abs(ball_dx)

        player_movement()
        player = pygame.Rect(player_x, player_y, 40, 15)
        pygame.draw.rect(screen, player_colour, player)

        draw_bricks()
        draw_wall()
        draw_hud()

        reset_mouse_position()

        pygame.display.flip()

    draw_ball()
    ball_collision()
    draw_bricks()
    draw_wall()
    draw_hud()

    player_movement()
    player = pygame.Rect(player_x, player_y, 40, 15)
    pygame.draw.rect(screen, player_colour, player)

    reset_mouse_position()

    pygame.display.flip()
