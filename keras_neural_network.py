from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Input
from keras.optimizers import Adam

import os

class KerasNeuralNetwork:

    def __init__(self, features, hidden_level_units):

        self.model = None
        self.features = features
        self.hidden_level_units = hidden_level_units

        self.weights_file = 'keras_neural_network_weights.h5'
        self.weights_file_backup = 'keras_neural_network_weights_backup.h5'


    def createModel(self):

        input_layer = Input(shape=(1, self.features), batch_shape=(None, 1, self.features))

        # layer 1
        hidden_layer_1 = Dense(self.hidden_level_units, activation='relu',
                                 kernel_initializer='normal')(input_layer)

        # output1
        output = Dense(1, kernel_initializer='normal', activation='sigmoid')(hidden_layer_1)

        # define model
        self.model = Model(inputs=input_layer, outputs=output)

        optimizer = Adam(lr=0.2)

        self.model.compile(optimizer=optimizer, loss='binary_crossentropy')
        self.model.summary()

    def loadWeights(self):

        if os.path.isfile(self.weights_file) == False:
            return

        self.model.load_weights(self.weights_file)


    def saveWeights(self):

        self.model.save_weights(self.weights_file)
        self.model.save_weights(self.weights_file_backup)


    def trainModel(self, trainX, trainY, epochs):

        # fit model
        self.model.fit(x=trainX,
                  y=trainY,
                  epochs=epochs,
                  verbose=0,
                  shuffle=False)

    def predictWithModel(self, X):

        return self.model.predict(X)

