from config import *

log = logging.getLogger('keras_neural_network')

from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Input
from keras import metrics
from keras.optimizers import Adam
from keras.utils import plot_model

import os


class KerasNeuralNetwork:

    def __init__(self, features, hidden_level_units):
        self.model = None
        self.features = features
        self.hidden_level_units = hidden_level_units

        self.weights_file = '../data/keras_neural_network_weights.h5'

        self.batch_size = 32

    def createModel(self):
        input_layer = Input(shape=(None, self.features), batch_shape=(None, None, self.features))

        # layer 1
        hidden_layer_1 = Dense(self.hidden_level_units, activation='relu',
                               kernel_initializer='normal')(input_layer)

        # layer 2
        hidden_layer_2 = Dense(2 * self.hidden_level_units, activation='relu',
                               kernel_initializer='normal')(hidden_layer_1)

        # layer 3
        hidden_layer_3 = Dense(10 * self.hidden_level_units, activation='relu',
                               kernel_initializer='normal')(hidden_layer_2)

        # layer 4
        hidden_layer_4 = Dense(2 * self.hidden_level_units, activation='relu',
                               kernel_initializer='normal')(hidden_layer_3)

        # layer 5
        hidden_layer_5 = Dense(self.hidden_level_units, activation='relu',
                               kernel_initializer='normal')(hidden_layer_4)

        # output1
        output = Dense(1, kernel_initializer='normal', activation='sigmoid')(hidden_layer_5)

        # define model
        self.model = Model(inputs=input_layer, outputs=output)

        optimizer = Adam()

        self.model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=[metrics.binary_accuracy])
        self.model.summary()

    def loadWeights(self):
        if os.path.isfile(self.weights_file) == False:
            return

        self.model.load_weights(self.weights_file)

    def saveWeights(self):
        self.model.save_weights(self.weights_file)

    def trainModel(self, trainX, trainY, split, epochs):
        # fit model
        self.model.fit(x=trainX,
                       y=trainY,
                       epochs=epochs,
                       validation_split=split,
                       batch_size=self.batch_size,
                       verbose=1,
                       shuffle=True)


    def evaluateModel(self, testX, testY):
        # fit model
        result = self.model.evaluate(x=testX,
                                     y=testY,
                                     batch_size=self.batch_size,
                                     verbose=0)
        log.info('Test results: {} - {}  {} - {}'.format(self.model.metrics_names[0], result[0], self.model.metrics_names[1], result[1]))

    def predictWithModel(self, X):
        return self.model.predict(X)

    def plotModel(self, output_file):
        plot_model(self.model, show_shapes=True, show_layer_names=True, rankdir='TB', to_file=output_file)