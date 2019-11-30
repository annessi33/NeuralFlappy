import pygame
import os
import numpy as np
from tensorflow import keras
from population import Population
from obstacles import Obstacles

import GLOBAL_VARS as G

pygame.init()
clock = pygame.time.Clock()

win = pygame.display.set_mode((G.SCREEN_WIDTH, G.SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Network')

bg = pygame.image.load(os.path.join('assets/sprites', 'background-day.png')).convert()
base = pygame.image.load(os.path.join('assets/sprites', 'base.png')).convert()
gameover = pygame.image.load(os.path.join('assets/sprites', 'gameover.png')).convert_alpha()
bg_end = pygame.image.load(os.path.join('assets/sprites', 'message.png')).convert_alpha()

numbers = [
    pygame.image.load('assets/sprites/0.png').convert_alpha(),
    pygame.image.load('assets/sprites/1.png').convert_alpha(),
    pygame.image.load('assets/sprites/2.png').convert_alpha(),
    pygame.image.load('assets/sprites/3.png').convert_alpha(),
    pygame.image.load('assets/sprites/4.png').convert_alpha(),
    pygame.image.load('assets/sprites/5.png').convert_alpha(),
    pygame.image.load('assets/sprites/6.png').convert_alpha(),
    pygame.image.load('assets/sprites/7.png').convert_alpha(),
    pygame.image.load('assets/sprites/8.png').convert_alpha(),
    pygame.image.load('assets/sprites/9.png').convert_alpha()
]


def display_score(n, x, y):
    spacing = 24
    i = 0
    for nr in [int(d) for d in str(n)]:
        win.blit(numbers[nr], (x + i * spacing, y))
        i += 1


def save_model():
    global run
    model = pop.get_best_model()
    filename = "last_model_gen_" + str(pop.gen) + ".h5"
    model.save(filename)
    win.blit(gameover, (G.SCREEN_WIDTH / 2 - 96, G.SCREEN_HEIGHT / 2 - 21))
    run = False


def load_model():
    model = keras.models.load_model("best_model.h5")
    pop.birds[0].nn.model = model
    pop.birds[0].is_best = True
    pop.best_bird = 0


def redraw_window():
    win.blit(bg, (0, 0))
    pipes.show(win)
    win.blit(base, (- 48 + G.X_POS % 48, 400))
    pop.show(win)

    display_score(score, G.SCREEN_WIDTH / 2, 20)

    string_gen = "Generation: " + str(pop.gen)
    string_fit = "Best score: " + str(np.clip(int((pop.best_score - 130) / 180), 0, None))
    font = pygame.font.SysFont("monospace", 14, bold=True)
    text_gen = font.render(string_gen, 1, (0, 0, 0))
    text_fit = font.render(string_fit, 1, (0, 0, 0))
    win.blit(text_gen, (140, 460))
    win.blit(text_fit, (140, 480))

    draw_graph(pop.birds[pop.best_bird].nn)

    pygame.display.update()  # updates the screen


class Vector(object):
    def __init__(self):
        self.x, self.y = [], []


def draw_graph(nn):  # just look away, nothing to see here :)
    # 112 height x 288 width
    nodes = [nn.input_nodes, nn.hidden_nodes, nn.output_nodes]
    weights = nn.model.get_weights()
    w = np.concatenate((weights[0].flatten(), weights[2].flatten())).flatten()
    vec, pos = Vector(), Vector()
    x, y, rad = 50, 12, 3
    x_0 = 20
    y_0 = [int(G.SCREEN_HEIGHT - 87 + (max(nodes) - nodes[i]) / 2 * y) for i in range(0, nodes.__len__())]
    for nr in range(nodes.__len__()-1):
        for i in range(nodes[nr]):
            for j in range(nodes[nr+1]):
                vec.x.append(x)
                vec.y.append((j - i) * y - y_0[nr] + y_0[nr+1])
                pos.x.append(x_0 + x * nr)
                pos.y.append(y * i + y_0[nr])
    w[abs(w) < 0.2] = 0
    w[w < -1] = -1
    w[w > 1] = 1
    w *= 5
    vec_len = vec.x.__len__()
    for i in range(vec_len):
        if w[i] > 0:
            col = (255, 0, 0)
        else:
            col = (0, 0, 255)
        if not w[i] == 0:
            pygame.draw.line(win, col, [pos.x[i], pos.y[i]], [pos.x[i]+vec.x[i], pos.y[i]+vec.y[i]], abs(w[i]))
    for i in range(vec_len):
        pygame.draw.circle(win, (0, 0, 0), [pos.x[i], pos.y[i]], rad)
    for i in range(nn.output_nodes):  # please, don't judge me for this
        pygame.draw.circle(win, (0, 0, 0), [pos.x[vec_len-i-1]+vec.x[vec_len-i-1],
                                            pos.y[vec_len-i-1]+vec.y[vec_len-i-1]], rad)


pop = Population(G.POP_SIZE)
pipes = Obstacles()

# load_model()

run = True
while run:
    G.X_POS -= G.X_VEL

    for event in pygame.event.get():  # Loop through a list of events
        if event.type == pygame.QUIT:  # See if the user clicks the red x
            run = False    # End the loop
            pygame.quit()  # Quit the game
            quit()

    if G.X_POS % 180 == 0:
        pipes.add_obstacle()

    if pop.all_birds_dead():
        pop.next_generation()
        pipes = Obstacles()
        G.X_POS = 0
    else:
        pop.update(pipes)

    score = np.clip(int((- G.X_POS - 130) / 180), 0, None)
    if score > G.MAX_SCORE:
        save_model()

    redraw_window()
    clock.tick(G.FPS)
