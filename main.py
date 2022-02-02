from threading import Timer
from time import sleep
from paths import Paths
import pickle
from os import path
import math
import pygame
from pygame import mixer

pygame.init()
mixer.init()

# fps
clock = pygame.time.Clock()
fps = 60

# score
score = 0
font = pygame.font.Font('freesansbold.ttf', 16)

textX = 10
textY = 10
# Wait before shooting again (secs)
shoot_delay = 0.1

# define game variables
tile_size = 40
game_over = 0
main_menu = True
map = 1
max_maps = 9
score = 0
lives=3
projectiles=3

enemy_speed = 1

# colors
white = (255, 255, 255)
blue = (0, 0, 255)

# True - facing right
# False - facing left
pov = True

# screen specifications
screen_width = 800
screen_height = 800
icon = pygame.image.load(Paths['Icon'])
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Hexham's Reckoning")
pygame.display.set_icon(icon)

# fonts
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)
font_title = pygame.font.SysFont('Herculanum', 70)

# background
backgroundimg = pygame.image.load(Paths['Background'])
bg = pygame.transform.scale((backgroundimg), (screen_width, screen_height))

# load images
restart_img = pygame.image.load(Paths['RestartButton'])
start_img = pygame.image.load(Paths['StartButton'])
exit_img = pygame.image.load(Paths['ExitButton'])
projectile_img = pygame.image.load(Paths['Projectile'])
coin_img = pygame.image.load(Paths['Coin'])
mute_img = pygame.image.load(Paths['MuteButton'])
mute_img = pygame.transform.scale(mute_img, (100, 100))
fireball_img = pygame.image.load(Paths['Fireball'])
fireball_img = pygame.transform.scale(fireball_img, (20, 20))
# load sounds
ost_music = pygame.mixer.Sound(Paths['Music1'])
ost_music.set_volume(0.1)
ost_music.play(-1)
coin_fx = pygame.mixer.Sound(Paths['CoinSFX'])
coin_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound(Paths['GameOverSoundEffect'])
game_over_fx.set_volume(0.5)
game_complete_fx = pygame.mixer.Sound(Paths['GameCompleteSoundEffect'])
game_complete_fx.set_volume(0.5)
shoot_fx = pygame.mixer.Sound(Paths['ProjectileSoundEffect'])
shoot_fx.set_volume(0.5)

dead_enemies = []

row_count = col_count = 0


def draw_grid():
    for line in range(0, 20):
        pygame.draw.line(screen, (255, 255, 255), (0, line *
                         tile_size), (screen_width, line * tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line *
                         tile_size, 0), (line * tile_size, screen_height))


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def isClose(x1, y1, x2, y2):
    distance = math.sqrt((math.pow(x1-x2, 2)) + (math.pow(y1-y2, 2)))
    if distance < 300:
        return True
    else:
        return False

# reset map


def reset_map(map):
    player.reset(100, screen_height-130)  # coords of player spawn
    enemy1_group.empty()
    lava_group.empty()
    exit_group.empty()
    bullet_group.empty()
    # load level data and create new world
    p = path.join(Paths["Prefix"], 'levels', f'level{map}_data')
    if path.exists(p):
        pickle_in = open(p, 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        # get cursor position
        pos = pygame.mouse.get_pos()

        # check mouseover and click conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        # draw button
        screen.blit(self.image, self.rect)
        return action


class Player():
    shoot_wait = 0
    def __init__(self, x, y):
        self.reset(x, y)
    def __enddelay__(self):
        self.shoot_wait = 0
    def update(self, game_over):
        #change in x and y
        dx = 0
        dy = 0
        walk_cooldown = 5
        if game_over == 0:
            # get keystrokes
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                dx -= 5
                self.count += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.count += 1
                self.direction = 1
            if key[pygame.K_UP]:
                dy -= 5
            if key[pygame.K_DOWN]:
                dy += 5
            if key[pygame.K_SPACE]:
                if self.shoot_wait == 0 and projectiles>0:
                    self.shoot()
                    shoot_fx.play()
                    self.shoot_wait = 1
                    Timer(shoot_delay, self.__enddelay__).start()
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.count = 0
                self.index = 0

                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # handle animation
            if self.count > walk_cooldown:
                self.count = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # check for collision
            for tile in world.tile_list:
                # check for collision on y axis
                if tile[1].colliderect(self.rect.x, self.rect.y+dy, self.width, self.height):
                    dy = 0
                if tile[1].colliderect(self.rect.x+dx, self.rect.y, self.width, self.height):
                    dx = 0
            # check for collision with enemies
            if pygame.sprite.spritecollide(self, enemy1_group, False):
                game_over = -1
                ost_music.stop()
                if not is_muted:
                    game_over_fx.play()

            # check for collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                ost_music.stop()
                if not is_muted:
                    game_over_fx.play()
            # check for collision with edge
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            # update player coords
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            draw_text('Game Over!', font, blue,
                      (screen_width//2)-150, screen_height//2)
            if self.rect.y > 200:
                self.rect.y -= 5

        # draw player on screen
        screen.blit(self.image, self.rect)
        return game_over

    def shoot(self):
        global projectiles
        if self.direction == 1:
            bullet = Bullet(self.rect.x+self.width, self.rect.y+self.height//2, self.direction)
            bullet_group.add(bullet)
            projectiles-=1
        elif self.direction == -1:
            bullet = Bullet(self.rect.x, self.rect.y+self.height//2, self.direction)
            bullet_group.add(bullet)
            projectiles-=1

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.count = 0
        for n in range(1, 9):
            # mass load images for walking animation
            img_right = pygame.image.load(path.join(
                Paths['Prefix'], "mario_walking", f"Rmario{n}.png"))
            img_right = pygame.transform.scale(img_right, (40, 80))
            # flip on x axis for moving left
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load(Paths['DeadPlayer'])
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = 1


class World():
    def __init__(self, data):
        self.tile_list = []

        # load images
        dirt_img = pygame.image.load(
            path.join(Paths['Prefix'], 'dirt.png'))
        grass_img = pygame.image.load(
            path.join(Paths['Prefix'], 'grass.png'))
        tree_img = pygame.image.load(
            path.join(Paths['Prefix'], 'tree.png'))

        def draw_tile(image):
            img = pygame.transform.scale(image, (tile_size, tile_size))
            img_rect = img.get_rect()
            img_rect.x = col_count * tile_size
            img_rect.y = row_count * tile_size
            tile = (img, img_rect)
            self.tile_list.append(tile)

        row_count = 0
        enemy_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    draw_tile(dirt_img)
                if tile == 2:
                    draw_tile(grass_img)
                if tile == 3:
                    enemy_count += 1
                    if not enemy_count in dead_enemies:
                        enemy1 = Enemy(col_count*tile_size,
                                   row_count*tile_size, Paths['Enemy1Image'],enemy_count)
                        enemy1_group.add(enemy1)
                if tile == 4:
                    draw_tile(tree_img)
                if tile == 5:
                    item = Item(col_count*tile_size+(tile_size//2),
                                row_count*tile_size+(tile_size//2))
                    item_group.add(item)
                if tile == 6:
                    lava = Lava(col_count*tile_size, row_count*tile_size)
                    lava_group.add(lava)
                if tile == 7:
                    coin = Coin(col_count*tile_size+(tile_size//2),
                                row_count*tile_size+(tile_size//2))
                    coin_group.add(coin)
                if tile == 8:
                    exit = Exit(col_count*tile_size, row_count*tile_size)
                    exit_group.add(exit)

                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
          #  pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.image = fireball_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = direction
        self.speed = 5

    def update(self):
        if self.direction == 1:
            self.rect.x += self.speed
        elif self.direction == -1:
            self.rect.x -= self.speed
        if self.rect.x > screen_width or self.rect.x < 0:
            self.kill()
        killed = pygame.sprite.spritecollide(self, enemy1_group, True)
        if killed:
            self.kill()
            dead_enemies.append(killed[0].id)
        

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, path, id):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load(path)
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
        self.edx = self.edy = 0
        self.id = id

    def update(self):
        # enemies movement
        self.rect.x += self.edx
        self.rect.y += self.edy
        if isClose(player.rect.x, player.rect.y, self.rect.x, self.rect.y):
            # target player if player gets too close
            if self.rect.x < player.rect.x:
                self.edx = enemy_speed
            else:
                self.edx = -enemy_speed
            if self.rect.y < player.rect.y:
                self.edy = enemy_speed
            else:
                self.edy = -enemy_speed
        else:
            # continue to passively move
            self.edx = self.edy = 0
            self.rect.x += self.move_direction
            self.move_counter += 1
            if self.move_counter > 50:
                self.move_direction *= -1
                self.move_counter *= -1
        # keep enemies from crossing out of bounds
        if self.rect.x >= screen_width-50:
            self.edx = -self.edx
        if self.rect.y >= screen_width-50:
            self.edy = -self.edy


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(Paths['Lava'])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(Paths['Exit'])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load(Paths['Coin'])
        self.image = pygame.transform.scale(img, (tile_size//2, tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load(Paths['Projectile'])
        self.image = pygame.transform.scale(img, (tile_size//2, tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


# instances
player = Player(100, screen_height-120)

enemy1_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()

# coin icon for score
score_coin = Coin(tile_size//2, tile_size//2)
coin_group.add(score_coin)

# fireball icon for score
item_counter = Item(tile_size//2-5, tile_size//2+25)
coin_group.add(item_counter)

# load in level data and create world
p = path.join(Paths["Prefix"], 'levels', f'level{map}_data')
if path.exists(p):
    pickle_in = open(p, 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

# buttons
restart_button = Button(screen_width//2-50, screen_height//2+100, restart_img)
start_button = Button(screen_width//2-350, screen_height//2, start_img)
exit_button = Button(screen_width//2+150, screen_height//2, exit_img)
exit_button_2=Button(screen_width//2-150,screen_height//2+100,exit_img)
mute_button = Button(screen_width-100, screen_height-100, mute_img)
is_muted = False
# game loop
running = True
while running:
    clock.tick(fps)
    screen.blit(bg, (0, 0))
    if mute_button.draw():
        is_muted = not is_muted
        mute_button.image = pygame.transform.flip(
            mute_button.image, True, False)
        if is_muted:
            ost_music.stop()
        else:
            ost_music.play(-1)

    if main_menu:
        draw_text("Hexham's Reckoning", font_title, white, 50, 200)
        draw_text('Objective: Collect 90 coins', font_score, white, 275, 600)
        draw_text('Avoid enemies', font_score, white, 275, 650)
        if exit_button.draw():
            running = False
        if start_button.draw():
            main_menu = False
    else:
        world.draw()

        if game_over == 0:
            bullet_group.update()
            enemy1_group.update()
            draw_text(f'Map: {map}', font_score, white, screen_width-75, 10)
            draw_text(f'Lives: {lives}',font_score,white,10,60)

            # update score
            # check if coin collected
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                if not is_muted:
                    coin_fx.play()
            draw_text('X '+str(score), font_score, white, tile_size-10, 10)

            if pygame.sprite.spritecollide(player, item_group, True):
                projectiles += 1
                if not is_muted:
                    coin_fx.play()
            draw_text('X '+str(projectiles), font_score, white, tile_size-10, 40)

        enemy1_group.draw(screen)
        lava_group.draw(screen)
        exit_group.draw(screen)
        coin_group.draw(screen)
        bullet_group.draw(screen)
        item_group.draw(screen)

        game_over = player.update(game_over)

        # if player dies
        if game_over == -1:
            if lives>1:
                if restart_button.draw():  # if restart button clicked
                    lives-=1
                    if not is_muted:
                        ost_music.play()
                    game_over_fx.stop()
                    world_data = []
                    world = reset_map(map)
                    game_over = 0
                    score = 0
            else:
                if exit_button_2.draw():
                    running=False

        # if player exits
        if game_over == 1:
            dead_enemies = []
            map += 1
            if map <= max_maps:
                # reset level for next map
                world_data = []
                world = reset_map(map)
                game_over = 0
            else:
                # end game
                draw_text('You Win!', font, blue,
                          (screen_width//2)-140, screen_height//2)
                ost_music.stop()
                game_complete_fx.play()

                if restart_button.draw():
                    map = 1
                    world_data = []
                    world = reset_map(map)
                    game_over = 0
                    score = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.update()
