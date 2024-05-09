import pygame
import math
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

window_width, window_height = 600, 600
game_height = 478

game_window = pygame.display.set_mode((window_width, window_height))

pygame.display.set_caption('Bat Glide')


# get images
start_bg = pygame.image.load('assets/background/start_bg.png')
title_img = pygame.image.load('assets/background/title.png')
main_bg = pygame.image.load('assets/background/main_bg.png')
ground_bg = pygame.image.load('assets/background/test.png').convert()
ground_bg_width = ground_bg.get_width()
start_btn_img = pygame.image.load('assets/buttons/start_btn.png')
exit_btn_img = pygame.image.load('assets/buttons/exit_btn.png')
restart_btn_img = pygame.image.load('assets/buttons/restart_btn.png')
game_over_img = pygame.image.load('assets/background/game_over.png')

# get sound effects
wing_flap_sfx = pygame.mixer.Sound('assets/sounds/fly_sfx.wav')
point_sfx = pygame.mixer.Sound('assets/sounds/point_sfx.wav')

# plays the bg music at title screen
bg_sfx = pygame.mixer.music.load('assets/sounds/background_music.wav')
pygame.mixer.music.play(-1)

# score text variables
font = pygame.font.SysFont('Impact', 60)
white = (255, 255, 255)

# game variables
scroll_speed = 0
tiles = math.ceil(window_width / ground_bg_width) + 1
flying = False
game_over = False
stalactite_gap = 150
stalactite_frequency = 1000 #milliseconds
last_stalactite = pygame.time.get_ticks() - stalactite_frequency
score = 0
pass_stalactite = False

def sfx_play(sfx_file):
    sfx_file.play()

def object_collide_sfx():
    pygame.mixer.music.load('assets/sounds/hit_sfx.wav')
    pygame.mixer.music.play(0)

def sfx_pause():
    pygame.mixer.pause()


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    game_window.blit(img, (x, y))


def reset_game():
    stalactite_group.empty()
    bat_position.rect.x = 100
    bat_position.rect.y = game_height / 2
    score = 0
    return score

# player's character
class Bat(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        self.velocity = 0
        self.clicked = False

        for num in range(1, 4):
            img = pygame.image.load(f'assets/bat/bat{num}.png')
            small_img = pygame.transform.scale(img, (50, 42))
            self.images.append(small_img)

        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):

        if flying == True:

            # game gravity
            self.velocity += 0.5

            if self.velocity > 8:
                self.velocity = 8


            if self.rect.bottom < 478:
                self.rect.y += int(self.velocity)

        if game_over == False:

            # bat jump
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                sfx_play(wing_flap_sfx)
                self.velocity = -10
            
            # prevents the bat to jump so high by long press
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False


            # animation of bat flying
            self.counter += 1
            fly_cooldown = 5

            if self.counter > fly_cooldown:
                self.counter = 0
                self.index += 1

                # checks if the index of image is out of range and reset it.
                if self.index >= len(self.images):
                    self.index = 0
            
            self.image = self.images[self.index]

            # rotates the bat
            self.image = pygame.transform.rotate(self.images[self.index], self.velocity * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)


class Stalactite(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/stalactites/stalactite.png')
        self.rect = self.image.get_rect()

        # position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(stalactite_gap / 2)]
        
        if position == -1:
            self.rect.topleft = [x, y + int(stalactite_gap / 2)]

    
    def update(self):
        self.rect.x -= 4
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):

        action = False

        # get mouse position
        position = pygame.mouse.get_pos()

        # check if mouse hit the button
        if self.rect.collidepoint(position):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        game_window.blit(self.image, (self.rect.x, self.rect.y))
        
        return action

bat_group = pygame.sprite.Group()
stalactite_group = pygame.sprite.Group()

bat_position = Bat(100, int(game_height / 2))

bat_group.add(bat_position)

# buttons
start_btn = Button(window_width // 2 - 100, window_height // 2, start_btn_img)
exit_btn = Button(window_width // 2 - 100, window_height // 2 + 70, exit_btn_img)
restart_btn = Button(window_width // 2 - 100, window_height // 2 - 80, restart_btn_img)
exit_menu_btn = Button(window_width // 2 - 100, window_height // 2 - 10, exit_btn_img)



def main_game():

    run = True
    global scroll_speed, flying, game_over, last_stalactite, stalactite_frequency, score, pass_stalactite

    while run:

        clock.tick(fps)

        # set image position into the game window
        game_window.blit(main_bg, (0, 0))

        bat_group.draw(game_window)
        bat_group.update()

        stalactite_group.draw(game_window)
        

        # set the ground image
        for i in range(0, 2):
            game_window.blit(ground_bg, (i * ground_bg_width + scroll_speed, 478)) 
        
        # check the score
        if len(stalactite_group) > 0:
            if bat_group.sprites()[0].rect.left > stalactite_group.sprites()[0].rect.left\
                and bat_group.sprites()[0].rect.right < stalactite_group.sprites()[0].rect.right\
                and pass_stalactite == False:
                pass_stalactite = True
                
            
            if pass_stalactite == True:
                if bat_group.sprites()[0].rect.right > stalactite_group.sprites()[0].rect.right:
                    sfx_play(point_sfx) # plays point sound
                    score += 1
                    pass_stalactite = False
        
        draw_text(str(score), font, white, int(window_width / 2), 20)
        
       
        # detect collision
        if pygame.sprite.groupcollide(bat_group, stalactite_group, False, False) or bat_position.rect.top < 0:
            object_collide_sfx()
            game_over = True
            

       


        # check if the bat hit the ground
        if bat_position.rect.bottom >= 478:
            game_over = True
            flying = False


        if game_over == False and flying == True:

            #generate new stalactites
            current_time = pygame.time.get_ticks()
            if current_time - last_stalactite > stalactite_frequency:
                stalactite_height = random.randint(-100, 100)
                bottom_stalactite = Stalactite(window_width, int(game_height / 2) + stalactite_height, -1)
                top_stalactite = Stalactite(window_width, int(game_height / 2) + stalactite_height, 1)
                stalactite_group.add(bottom_stalactite)
                stalactite_group.add(top_stalactite)
                last_stalactite = current_time



            # set the ground image to be scrolling
            for i in range(0, tiles):
                game_window.blit(ground_bg, (i * ground_bg_width + scroll_speed, 478))

            scroll_speed -= 10


            # reset scroll
            if abs(scroll_speed) > ground_bg_width:
                scroll_speed = 0

            stalactite_group.update()

                
        # check for game over and restart
        if game_over == True:
            game_window.blit(game_over_img, (110, 110))
            
            if restart_btn.draw() == True:
                pygame.mixer.music.stop()
                game_over = False
                score = reset_game()
                
            if exit_menu_btn.draw() == True:
                run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
                flying = True

        pygame.display.update()

    pygame.quit()


def main():

    run = True

    while run:

        game_window.blit(start_bg, (0, 0))
        game_window.blit(title_img, (170, 110))

        if start_btn.draw() == True:
                pygame.mixer.music.stop() #stops the bg music
                main_game()


        if exit_btn.draw() == True:
                run = False


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        pygame.display.update()

    pygame.quit()
   




# runs main game function
main()