import pygame
import random
import os
import GLOBAL_VARS as G


class Pipe(object):
    sprite = pygame.image.load(os.path.join('assets/sprites', 'pipe-green.png'))

    def __init__(self, x, height):
        self.x = x
        self.height = height
        self.width = 52
        self.vel = 3
        self.gap = 120
        self.hitbox_upp = [self.x, 0, self.width, self.height]
        self.hitbox_low = [self.x, self.height + self.gap, self.width, G.SCREEN_HEIGHT]
        self.counted = False

    def show(self, window):
        self.hitbox_upp = [self.x, 0, self.width, self.height]
        self.hitbox_low = [self.x, self.height + self.gap, self.width, G.SCREEN_HEIGHT]

        # pygame.draw.rect(window, (255, 0, 0), self.hitbox_upp, 2)
        # pygame.draw.rect(window, (255, 0, 0), self.hitbox_low, 2)

        window.blit(pygame.transform.rotate(self.sprite, 180), (self.x, - 320 + self.height))
        window.blit(self.sprite, (self.x, self.height + self.gap))

    def collide(self, birdy):
        rect = birdy.hitbox
        if rect[0] + rect[2] > self.hitbox_upp[0] and rect[0] < self.hitbox_upp[0] + self.hitbox_upp[2]:
            if rect[1] + rect[3] > self.hitbox_upp[1] and rect[1] < self.hitbox_upp[1] + self.hitbox_upp[3]:
                # print("COLLISION UPP")
                birdy.dead = True
            elif rect[1] + rect[3] > self.hitbox_low[1] and rect[1] < self.hitbox_low[1] + self.hitbox_low[3]:
                # print("COLLISION LOW")
                birdy.dead = True
        return False


class Obstacles(object):
    def __init__(self):
        self.pipes = []
        self.add_obstacle()

    def show(self, window):
        for pipe in self.pipes:
            pipe.show(window)

    def add_obstacle(self):
        self.pipes.append(Pipe(G.SCREEN_WIDTH + 60, random.randrange(60, 220)))

    def check_collision(self, population):
        for pipe in self.pipes:
            pipe.x -= G.X_VEL
            if pipe.x < pipe.width * -1:
                self.pipes.pop(self.pipes.index(pipe))
            for i in range(population.size):
                if pipe.x < population.birds[i].x - pipe.width and not pipe.counted:
                    pipe.counted = True
                pipe.collide(population.birds[i])

    def get_next_obstacle(self):
        for pipe in self.pipes:
            if pipe.x + 26 > 0.2 * G.SCREEN_WIDTH:
                return pipe.x, pipe.height
