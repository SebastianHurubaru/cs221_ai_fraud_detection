from deep_neural_network.keras_neural_network import *
import pandas as pd

log = logging.getLogger('train_reflex_model.py')

def train_reflex_model(train_data_file):

    df = pd.read_csv(train_data_file)

    myNeuralNetwork = KerasNeuralNetwork(numOfFeatures, numOfHiddenLayerUnits)
    myNeuralNetwork.createModel()
    myNeuralNetwork.loadWeights()

    trainX = df.values[:, 1:1 + numOfFeatures].reshape(df.values.shape[0], 1, numOfFeatures)
    trainY = df.values[:, -1:].reshape(df.values.shape[0], 1, numOfOutputs)
    myNeuralNetwork.trainModel(trainX, trainY, validation_split, num_iterations)

    myNeuralNetwork.saveWeights()

train_reflex_model('../data/train_data.csv')