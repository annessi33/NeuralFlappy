import numpy as np
import pygame
import os
import GLOBAL_VARS as G
from neural_network import NeuralNetwork


class Bird(object):
    sprite = [
        pygame.image.load(os.path.join('assets/sprites', 'bluebird-downflap.png')),
        pygame.image.load(os.path.join('assets/sprites', 'bluebird-midflap.png')),
        pygame.image.load(os.path.join('assets/sprites', 'bluebird-upflap.png'))
    ]

    best_sprite = [
        pygame.image.load(os.path.join('assets/sprites', 'redbird-downflap.png')),
        pygame.image.load(os.path.join('assets/sprites', 'redbird-midflap.png')),
        pygame.image.load(os.path.join('assets/sprites', 'redbird-upflap.png'))
    ]

    def __init__(self):
        self.x = 0.2 * G.SCREEN_WIDTH
        self.y = 200
        self.width = 34
        self.height = 24
        self.move_count = 0  # to cycle among sprites
        self.acc = 0.0
        self.vel = 0.0
        self.hitbox = [self.x + 6, self.y + 5, self.width - 6, self.height - 5]
        self.dead = False
        self.tf_inputs = []
        self.score = 0
        self.fitness = 0.0
        self.nn = NeuralNetwork(5, 8, 2)
        self.baby = None
        self.is_best = False

    def show(self, window):
        self.hitbox = [self.x + 6, self.y + 5, self.width - 6, self.height - 5]
        # pygame.draw.rect(window, (255, 0, 0), self.hitbox, 2)

        if self.move_count > 8:
            self.move_count = 0
        if self.is_best:
            new_sprite = pygame.transform.rotate(self.best_sprite[self.move_count // 3], self.vel)
        else:
            new_sprite = pygame.transform.rotate(self.sprite[self.move_count // 3], self.vel)
        window.blit(new_sprite, (self.x, self.y))
        if not self.dead:
            self.move_count += 1

    def move(self):
        self.think()
        self.vel += G.Y_ACC
        self.vel = np.clip(self.vel, -40, 20)
        self.y -= self.vel
        self.y = np.clip(self.y, -10, 401 - self.height)

    def update(self):
        if not self.dead:
            self.move()
            self.collide()
            self.score = - G.X_POS
        elif self.x < - self.width - 5:
            pass
        else:
            self.x -= G.X_VEL

    def jump(self):
        self.vel = 10

    def collide(self):
        if self.hitbox[1] + self.hitbox[3] > 400:
            # print("COLLISION TERRAIN")
            self.dead = True
        elif self.hitbox[1] < 0:
            # print("COLLISION SKY")
            self.dead = True
        return False

    def gimme_baby(self):
        self.baby = Bird()
        self.baby.nn = self.nn.copy()
        self.baby.mutate()
        return self.baby

    def clone(self):
        self.baby = Bird()
        self.baby.nn = self.nn.copy()
        return self.baby

    def get_tf_inputs(self, _pipes_):
        next_obstacle = _pipes_.get_next_obstacle()
        self.tf_inputs = []
        self.tf_inputs.append(self.vel / 40.0)
        self.tf_inputs.append(self.y / G.SCREEN_HEIGHT)
        self.tf_inputs.append((next_obstacle[0] - self.x + 26) / G.SCREEN_WIDTH)
        self.tf_inputs.append((next_obstacle[1] - self.y) / G.SCREEN_WIDTH)
        self.tf_inputs.append((next_obstacle[1] - self.y + 120) / G.SCREEN_WIDTH)

    def think(self):
        output = self.nn.predict(self.tf_inputs)
        if output[0] > output[1]:
            self.jump()

    def mutate(self):
        self.nn.mutate(G.MUT_RATE)
