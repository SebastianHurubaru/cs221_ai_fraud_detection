from deep_neural_network.keras_neural_network import *
import pandas as pd

log = logging.getLogger('train_reflex_model.py')

def test_reflex_model(test_data_file):

    df = pd.read_csv(test_data_file)

    myNeuralNetwork = KerasNeuralNetwork(numOfFeatures, numOfHiddenLayerUnits)
    myNeuralNetwork.createModel()
    myNeuralNetwork.loadWeights()

    testX = df.values[:, 1:1 + numOfFeatures].reshape(1, df.values.shape[0], numOfFeatures)
    testY = df.values[:, -1:].reshape(1, df.values.shape[0], numOfOutputs)

    myNeuralNetwork.evaluateModel(testX, testY)

    myNeuralNetwork.plotModel('../data/reflex_nn_architecture.png')


test_reflex_model('../data/test_data.csv')