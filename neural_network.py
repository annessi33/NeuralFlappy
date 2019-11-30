import random
from random import gauss
import tensorflow as tf
from tensorflow import keras


class NeuralNetwork (object):
    def __init__(self, inp, hid, out, mod=None):
        if mod is None:
            self.input_nodes = inp
            self.hidden_nodes = hid
            self.output_nodes = out
            self.model = self.create_model()
        else:
            self.input_nodes = inp
            self.hidden_nodes = hid
            self.output_nodes = out
            self.model = mod

    def create_model(self):
        model = keras.Sequential()
        model.add(keras.layers.Dense(units=self.hidden_nodes,
                                     input_shape=[self.input_nodes],
                                     activation='sigmoid'))
        model.add(keras.layers.Dense(units=self.output_nodes,
                                     activation='softmax'))
        return model

    def predict(self, inputs):
        xs = tf.convert_to_tensor([inputs])
        # with tf.device('/GPU:0'):
        with tf.device('/CPU:0'):
            ys = self.model.predict(xs)
        return ys[0]

    def copy(self):
        model_copy = self.create_model()
        weights = self.model.get_weights()
        weights_copies = weights.copy()
        model_copy.set_weights(weights_copies)
        return NeuralNetwork(self.input_nodes, self.hidden_nodes, self.output_nodes, model_copy)

    def mutate(self, rate):
        weights = self.model.get_weights()
        mutated_weights = weights
        for i in range(weights.__len__()):
            shape = weights[i].shape
            values = weights[i].flatten()
            for j in range(values.size):
                if random.random() < rate:
                    w = values[j]
                    values[j] = w + gauss(0, 1)
            mutated_weights[i] = values.reshape(shape)
        self.model.set_weights(mutated_weights)
