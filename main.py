from os import walk
import pygame
import random
import math

from pygame.constants import K_RIGHT

pygame.init()

# fps
clock = pygame.time.Clock()
fps = 60

# score
score = 0
font = pygame.font.Font('freesansbold.ttf', 16)

textX = 10
textY = 10

# define game variables
tile_size = 40
game_over = False
main_menu=True

# True - facing right
# False - facing left
pov = True

# file paths
PrefixPath = '/Users/Aniket/Documents/Python Files/Hexhams_Reckoning/assets/'
IconPath = PrefixPath+'mario.png'
SpriteRImagePath = PrefixPath+'mario_walking/mario6.png'
SpriteLImagePath = PrefixPath+'firemario_L.png'
Enemy1ImagePath = PrefixPath+'goomba.png'
MusicPath = PrefixPath+'mario_soundtrack.mp3'
ProjectilePath = PrefixPath+'fireball.png'
ProjectileSoundEffectPath = PrefixPath+'fireball.mp3'
BackgroundPath = PrefixPath+'grass_background.png'
ShootingSoundEffectPath = PrefixPath+'fireball.mp3'
GameOverSoundEffectPath = PrefixPath+'game_over_sound_effect.mp3'
GameCompleteSoundEffectPath = PrefixPath+'game_complete_sound_effect.mp3'
LavaPath = PrefixPath+'lava.png'
DeadPlayerPath = PrefixPath+'ghost.png'
RestartButtonPath = PrefixPath+'restart_btn.png'
StartButtonPath=PrefixPath+'start_btn.png'
ExitButtonPath=PrefixPath+'exit_btn.png'

# screen specifications
screen_width = 800
screen_height = 800
icon = pygame.image.load(IconPath)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Hexham's Reckoning")
pygame.display.set_icon(icon)

# background
BackgroundPath = PrefixPath+'bg.png'
backgroundimg = pygame.image.load(BackgroundPath)
bg = pygame.transform.scale((backgroundimg), (screen_width, screen_height))

#load button images
restart_img = pygame.image.load(RestartButtonPath)
start_img = pygame.image.load(StartButtonPath)
exit_img = pygame.image.load(ExitButtonPath)


row_count = col_count = 0


def draw_grid():
    for line in range(0, 20):
        pygame.draw.line(screen, (255, 255, 255), (0, line *
                         tile_size), (screen_width, line * tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line *
                         tile_size, 0), (line * tile_size, screen_height))


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked=False

    def draw(self):
        action=False 
        # get cursor position
        pos = pygame.mouse.get_pos()

        #check mouseover and click conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]==1 and self.clicked==False:
                action=True
                self.clicked=True

        if pygame.mouse.get_pressed()[0]==0:
            self.clicked=False
        # draw button
        screen.blit(self.image, self.rect)
        return action


class Player():
    def __init__(self, x, y):
        self.reset(x,y)

    def update(self, game_over):
        #change in x and y
        dx = 0
        dy = 0
        walk_cooldown = 5
        if not game_over:
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
                game_over = True
            # check for collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = True

            # update player coords
            self.rect.x += dx
            self.rect.y += dy

        elif game_over:
            self.image = self.dead_image
            if self.rect.y > 200:
                self.rect.y -= 5

        # draw player on screen
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        return game_over

    def reset(self,x,y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.count = 0
        for n in range(1, 9):
            # mass load images for walking animation
            img_right = pygame.image.load(
                f"{PrefixPath}mario_walking/Rmario{n}.png")
            img_right = pygame.transform.scale(img_right, (40, 80))
            # flip on x axis for moving left
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load(DeadPlayerPath)
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = 0

class World():
    def __init__(self, data):
        self.tile_list = []

        # load images
        dirt_img = pygame.image.load(
            PrefixPath+'dirt.png')
        grass_img = pygame.image.load(
            PrefixPath+'grass.png')
        tree_img = pygame.image.load(
            PrefixPath+'tree.png')

        def draw_tile(image):
            img = pygame.transform.scale(image, (tile_size, tile_size))
            img_rect = img.get_rect()
            img_rect.x = col_count * tile_size
            img_rect.y = row_count * tile_size
            tile = (img, img_rect)
            self.tile_list.append(tile)

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    draw_tile(dirt_img)
                if tile == 2:
                    draw_tile(grass_img)
                if tile == 3:
                    draw_tile(tree_img)
                if tile == 4:
                    enemy1 = Enemy(col_count*tile_size,
                                   row_count*tile_size, Enemy1ImagePath)
                    enemy1_group.add(enemy1)
                if tile == 5:
                    lava = Lava(col_count*tile_size, row_count*tile_size)
                    lava_group.add(lava)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, path):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load(path)
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        # enemies moving
        self.rect.x += self.move_direction
        self.move_counter += 1
        if self.move_counter > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(LavaPath)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# world map data
world_data = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 0, 3, 0, 4, 0, 0, 0, 0, 1],
    [1, 0, 3, 0, 0, 0, 0, 0, 5, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# instances
player = Player(100, screen_height-120)

enemy1_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()

world = World(world_data)

# buttons
restart_button = Button(screen_width//2-50, screen_height//2+100, restart_img)
start_button=Button(screen_width//2-350,screen_height//2,start_img)
exit_button=Button(screen_width//2+150,screen_height//2,exit_img)

# game loop
running = True
while running:
    clock.tick(fps)
    screen.blit(bg, (0, 0))
    
    if main_menu:
        if exit_button.draw():
            running=False
        if start_button.draw():
            main_menu=False
    else:
        world.draw()

        if not game_over:
            enemy1_group.update()

        enemy1_group.draw(screen)

        lava_group.draw(screen)

        game_over = player.update(game_over)

        # if player dies
        if game_over:
            if restart_button.draw():
                player.reset(100, screen_height-120)
                game_over=False


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.update()
