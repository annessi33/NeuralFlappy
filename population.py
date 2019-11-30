import numpy as np
from bird import Bird


class Population(object):
    def __init__(self, size):
        self.size = size
        self.birds = []
        self.new_birds = []
        self.fitness_sum = 0
        self.gen = 1
        self.best_bird = 0
        self.best_score = 0
        for i in range(self.size):
            self.birds.append(Bird())

    def show(self, window):
        for i in range(1, self.size):
            self.birds[i].show(window)
        self.birds[0].show(window)

    def update(self, _pipes_):
        for i in range(self.size):
            self.birds[i].get_tf_inputs(_pipes_)
            self.birds[i].update()
        _pipes_.check_collision(self)

    def all_birds_dead(self):
        for i in range(self.size):
            if not self.birds[i].dead:
                return False
        return True

    def next_generation(self):
        self.new_birds = []
        self.calculate_fitness()
        self.get_best()
        self.new_birds.append(self.birds[self.best_bird].clone())
        self.new_birds[0].is_best = True
        for i in range(1, self.size):
            parent = self.select_parent()
            self.new_birds.append(parent.gimme_baby())
        self.birds = self.new_birds
        self.gen += 1

    def calculate_fitness(self):
        score_sum = 0
        score_max = 0
        for i in range(self.size):
            score_sum += self.birds[i].score
            if self.birds[i].score > score_max:
                score_max = self.birds[i].score
                if score_max > self.best_score:
                    self.best_score = score_max
        for i in range(self.size):
            self.birds[i].fitness = self.birds[i].score / score_sum

    def select_parent(self):
        rand = np.random.rand(1)
        running_sum = 0
        for i in range(self.size):
            running_sum += self.birds[i].fitness
            if running_sum > rand:
                return self.birds[i]
        return None

    def get_best(self):
        max_fit = 0
        max_index = 0
        for i in range(self.size):
            if self.birds[i].fitness > max_fit:
                max_fit = self.birds[i].fitness
                max_index = i
        self.best_bird = max_index

    def get_best_model(self):
        for i in range(self.size):
            if not self.birds[i].dead:
                best_model = self.birds[i].nn.model
                return best_model
