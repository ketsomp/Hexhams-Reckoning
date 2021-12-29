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

tile_size = 40

# True - facing right
# False - facing left
pov = True

# file paths
IconPath = '/Users/Aniket/Documents/Python Files/Hexhams Reckoning/assets/mario.png'
SpriteRImagePath = '/Users/Aniket/Documents/Python Files/Hexhams Reckoning/assets/mario_walking/mario6.png'
SpriteLImagePath = '/Users/Aniket/Documents/Python Files/Hexhams Reckoning/assets/firemario_L.png'
Enemy1ImagePath = '/Users/Aniket/Documents/Python Files/Hexhams Reckoning/assets/goomba.png'
MusicPath = '/Users/Aniket/Documents/Python Files/Hexhams Reckoning/assets/mario_soundtrack.mp3'
ProjectilePath = '/Users/Aniket/Documents/Python Files/Hexhams Reckoning/assets/fireball.png'
ProjectileSoundEffectPath = '/Users/Aniket/Documents/Python Files/Hexhams Reckoning/assets/fireball.mp3'
BackgroundPath = '/Users/Aniket/Documents/Python Files/Hexhams Reckoning/assets/grass_background.png'
ShootingSoundEffectPath = '/Users/Aniket/Documents/Python Files/Hexhams Reckoning/assets/fireball.mp3'
GameOverSoundEffectPath = '/Users/Aniket/Documents/Python Files/Hexhams Reckoning/assets/game_over_sound_effect.mp3'
GameCompleteSoundEffectPath = '/Users/Aniket/Documents/Python Files/Hexhams Reckoning/assets/game_complete_sound_effect.mp3'

# screen specifications
screen_width = 800
screen_height = 800
icon = pygame.image.load(IconPath)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Hexham's Reckoning")
pygame.display.set_icon(icon)

# background
BackgroundPath = '/Users/Aniket/Documents/Python Files/Hexhams Reckoning/assets/bg.png'
backgroundimg = pygame.image.load(BackgroundPath)
bg = pygame.transform.scale((backgroundimg), (screen_width, screen_height))


def draw_grid():
    for line in range(0, 20):
        pygame.draw.line(screen, (255, 255, 255), (0, line *
                         tile_size), (screen_width, line * tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line *
                         tile_size, 0), (line * tile_size, screen_height))


class Player():
    def __init__(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.count = 0
        for n in range(1, 9):
            img_right = pygame.image.load(
                f'/Users/Aniket/Documents/Python Files/Hexhams Reckoning/assets/mario_walking/Rmario{n}.png')
            img_right = pygame.transform.scale(img_right, (40, 80))
            # flip on x axis for moving left
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction=0

    def update(self):
        #change in x and y
        dx = 0
        dy = 0
        walk_cooldown = 5
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

        # update player coords
        self.rect.x += dx
        self.rect.y += dy

        # draw player on screen
        screen.blit(self.image, self.rect)


class World():
    def __init__(self, data):
        self.tile_list = []

        # load images
        dirt_img = pygame.image.load(
            '/Users/Aniket/Documents/Python Files/Hexhams Reckoning/assets/dirt.png')
        grass_img = pygame.image.load(
            '/Users/Aniket/Documents/Python Files/Hexhams Reckoning/assets/grass.png')
        tree_img = pygame.image.load(
            '/Users/Aniket/Documents/Python Files/Hexhams Reckoning/assets/tree.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(
                        dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(
                        grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    img = pygame.transform.scale(
                        tree_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


world_data = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 3, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

player = Player(100, screen_height-120)
world = World(world_data)

# game loop
running = True
while running:
    clock.tick(fps)
    screen.blit(bg, (0, 0))
    world.draw()

    player.update()

    # draw_grid()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.update()
