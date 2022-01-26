import pickle
from os import path
import math
from re import X
import pygame
from pygame import mixer
from pygame.constants import K_RIGHT

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

# define game variables
tile_size = 40
game_over = 0
main_menu = True
map = 5
max_maps = 9
score = 0

# colors
white = (255, 255, 255)
blue = (0, 0, 255)

# True - facing right
# False - facing left
pov = True

# file paths
from paths import Paths
# Replacing
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
font_title=pygame.font.SysFont('Herculanum',70)


# background
backgroundimg = pygame.image.load(Paths['Background'])
bg = pygame.transform.scale((backgroundimg), (screen_width, screen_height))

# load images
restart_img = pygame.image.load(Paths['RestartButton'])
start_img = pygame.image.load(Paths['StartButton'])
exit_img = pygame.image.load(Paths['ExitButton'])
projectile_img = pygame.image.load(Paths['Projectile'])
coin_img = pygame.image.load(Paths['Coin'])

# load sounds
ost_music = pygame.mixer.Sound(Paths['Music1'])
ost_music.play(-1)
coin_fx = pygame.mixer.Sound(Paths['CoinSFX'])
coin_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound(Paths['GameOverSoundEffect'])
game_over_fx.set_volume(0.5)
game_complete_fx = pygame.mixer.Sound(Paths['GameCompleteSoundEffect'])
game_complete_fx.set_volume(0.5)

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
    def __init__(self, x, y):
        self.reset(x, y)

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
                game_over_fx.play()

            # check for collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                ost_music.stop()
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
                      (screen_width//2)-200, screen_height//2)
            if self.rect.y > 200:
                self.rect.y -= 5

        # draw player on screen
        screen.blit(self.image, self.rect)
       # pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.count = 0
        for n in range(1, 9):
            # mass load images for walking animation
            img_right = pygame.image.load(path.join(
                Paths['Prefix'],"mario_walking",f"Rmario{n}.png"))
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
        self.direction = 0


class World():
    def __init__(self, data):
        self.tile_list = []

        # load images
        dirt_img = pygame.image.load(
            path.join(Paths['Prefix'],'dirt.png'))
        grass_img = pygame.image.load(
            path.join(Paths['Prefix'],'grass.png'))
        tree_img = pygame.image.load(
            path.join(Paths['Prefix'],'tree.png'))

        one_img=pygame.image.load('/Users/Aniket/Documents/Python Files/Hexhams-Reckoning/assets/numbers/one.webp')
        two_img= pygame.image.load('/Users/Aniket/Documents/Python Files/Hexhams-Reckoning/assets/numbers/two.webp')
        three_img= pygame.image.load('/Users/Aniket/Documents/Python Files/Hexhams-Reckoning/assets/numbers/three.png')
        four_img= pygame.image.load('/Users/Aniket/Documents/Python Files/Hexhams-Reckoning/assets/numbers/four.png')
        five_img= pygame.image.load('/Users/Aniket/Documents/Python Files/Hexhams-Reckoning/assets/numbers/five.webp')
        six_img= pygame.image.load('/Users/Aniket/Documents/Python Files/Hexhams-Reckoning/assets/numbers/six.png')
        seven_img= pygame.image.load('/Users/Aniket/Documents/Python Files/Hexhams-Reckoning/assets/numbers/seven.png')
        eight_img= pygame.image.load('/Users/Aniket/Documents/Python Files/Hexhams-Reckoning/assets/numbers/eight.webp')
        nine_img= pygame.image.load('/Users/Aniket/Documents/Python Files/Hexhams-Reckoning/assets/numbers/nine.webp')



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
                    enemy1 = Enemy(col_count*tile_size,
                                   row_count*tile_size, Paths['Enemy1Image'])
                    enemy1_group.add(enemy1)
                if tile == 4:
                    draw_tile(tree_img)
                if tile == 5:
                    draw_tile(projectile_img)
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
                if tile==9:
                    draw_tile(one_img)
                if tile==10:
                    draw_tile(two_img)
                if tile==11:
                    draw_tile(three_img)
                if tile==12:
                    draw_tile(four_img)
                if tile==13:
                    draw_tile(five_img)
                if tile==14:
                    draw_tile(six_img)
                if tile==15:
                    draw_tile(seven_img)
                if tile==16:
                    draw_tile(eight_img)
                if tile==17:
                    draw_tile(nine_img)
                
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
          #  pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)

enemy_speed=1


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
        self.edx=self.edy=0

    def update(self):
        # enemies movement
        self.rect.x+=self.edx
        self.rect.y+=self.edy
        if isClose(player.rect.x,player.rect.y,self.rect.x,self.rect.y):
            #target player if player gets too close
            if self.rect.x<player.rect.x:
                self.edx=enemy_speed
            else:
                self.edx=-enemy_speed
            if self.rect.y<player.rect.y:
                self.edy=enemy_speed
            else:
                self.edy=-enemy_speed
        else:
            #continue to passively move
            self.edx=self.edy=0
            self.rect.x += self.move_direction
            self.move_counter += 1
            if self.move_counter > 50:
                self.move_direction *= -1
                self.move_counter *= -1
        #keep enemies from crossing out of bounds
        if self.rect.x>=screen_width-50:
            self.edx=-self.edx
        if self.rect.y>=screen_width-50:
            self.edy=-self.edy
        
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


# instances
player = Player(100, screen_height-120)

enemy1_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

# coin icon for score
score_coin = Coin(tile_size//2, tile_size//2)
coin_group.add(score_coin)

# load in level data and create world
p = path.join(Paths["Prefix"],'levels',f'level{map}_data')
if path.exists(p):
    pickle_in = open(p, 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

# buttons
restart_button = Button(screen_width//2-50, screen_height//2+100, restart_img)
start_button = Button(screen_width//2-350, screen_height//2, start_img)
exit_button = Button(screen_width//2+150, screen_height//2, exit_img)

# game loop
running = True
while running:
    clock.tick(fps)
    screen.blit(bg, (0, 0))

    if main_menu:
        draw_text("Hexham's Reckoning",font_title,white,50,200)
        draw_text('Objective: Collect 90 coins',font_score,white,275,600)
        draw_text('Avoid enemies',font_score,white,275,650)
        if exit_button.draw():
            running = False
        if start_button.draw():
            main_menu = False
    else:
        world.draw()

        if game_over == 0:
            enemy1_group.update()
            draw_text(f'Map: {map}', font_score, white, screen_width-75, 10)

            # update score
            # check if coin collected
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                coin_fx.play()
            draw_text('X '+str(score), font_score, white, tile_size-10, 10)

        enemy1_group.draw(screen)
        lava_group.draw(screen)
        exit_group.draw(screen)
        coin_group.draw(screen)

        game_over = player.update(game_over)

        # if player dies
        if game_over == -1:
            if restart_button.draw():  # if restart button clicked
                ost_music.play()
                game_over_fx.stop()
                world_data = []
                world = reset_map(map)
                game_over = 0
                score = 0
        # if player exits
        if game_over == 1:
            map += 1
            if map <= max_maps:
                # reset level for next map
                world_data = []
                world = reset_map(map)
                game_over = 0
            else:
                #end game
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
