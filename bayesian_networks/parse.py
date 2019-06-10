import csv, re, collections
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix

def discretize(val):
    if val >= 0 and val < 0.25:
        return 0
    elif val < 0.50:
        return 1
    elif val < 0.75:
        return 2
    else:
        return 3

discrImpl = discretize
CUTOFF_VALUE = 0.4


class BayesNet:
    SKIP_FIRST = 1
    NO_SKIP_FIRST = 0

    def __init__(self, discrImpl):
        # required for post processing
        self.discr = discrImpl

        # holds the trained model, i.e the number of samples that belong to each bucket
        # the training is done using maximum likelihood probability estimation
        self.model = collections.defaultdict(int)


    def partition(self, entry):
        # PERCENTAGE CEASED OFFICERS
        PCO = self.discr(float(entry[3])/float(entry[1])) if int(entry[1]) != 0 else self.discr(0)

        # PERCENTAGE NON-PERSON OFFICERS
        PNPO = self.discr(float(entry[4])/float(entry[1])) if int(entry[1]) != 0 else self.discr(0)

        # PERCENTAGE CEASED PSC
        PCP = self.discr(float(entry[7])/float(entry[5])) if int(entry[5]) != 0 else self.discr(0)

        # PERCENTAGE NON-PERSON PSC
        PNPP = self.discr(float(entry[8])/float(entry[5])) if int(entry[5]) != 0 else self.discr(0)

        return (PCO, PNPO, PCP, PNPP)


    def processEntry(self, entry):
        self.model[self.partition(entry), int(entry[10])] += 1



    def infer(self, entry, laplace_value = 0):
        probBadA = self.model[self.partition(entry), 1]
        probGoodA = self.model[self.partition(entry), 0]
        probBad = (probBadA + laplace_value) / float(probGoodA + probBadA + laplace_value) if float(probGoodA + probBadA + laplace_value) > 0 else 0.5

        return probBad

    def trainModel(self, filename, skip_first):
        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter = ',')

            if skip_first == self.SKIP_FIRST:
                next(csv_reader, None)

            for row in csv_reader:
                BayesModel.processEntry(row)


    def trainModelClean(self, filename):
        self.model = collections.defaultdict(int)
        self.trainModel(filename)


    def testModel(self, filename, cutoff, skip_first):
        correct = 0
        wrong = 0

        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter = ',')

            if skip_first == self.SKIP_FIRST:
                next(csv_reader, None)

            for row in csv_reader:
                probBad = BayesModel.infer(row)

                if probBad >= cutoff and int(row[10]):
                    correct += 1
                elif probBad < cutoff and not int(row[10]):
                    correct += 1
                else:
                    wrong += 1

        return correct / float(correct + wrong)

    def construct_confusion_matrix(self, filename, cutoff, skip_first):
        true_labels = []
        false_labels = []

        with open('test_data.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter = ',')

            if skip_first == self.SKIP_FIRST:
                next(csv_reader, None)

            for row in csv_reader:
                true_labels.append(int(row[10]))
                
                probBad = BayesModel.infer(row)

                if probBad >= cutoff:
                    false_labels.append(1)
                else:
                    false_labels.append(0)

        BayesNet.plot_confusion_matrix(confusion_matrix(true_labels, false_labels, labels=[0, 1]))

    @staticmethod
    def plot_confusion_matrix(cm, title = 'Confusion matrix for fraud estimation using Bayesian Networks'):
        labels = ["Non-fraudulent", "Fraudulent"]
        plt.imshow(cm, interpolation = 'nearest', cmap = plt.cm.Blues)
        plt.title(title)
        plt.colorbar()
        tick_marks = np.arange(2)
        plt.xticks(tick_marks, labels, rotation = 45)
        plt.yticks(tick_marks, labels)
        plt.tight_layout()
        plt.ylabel('True label')
        plt.xlabel('Predicted label')
        plt.show()



BayesModel = BayesNet(discrImpl)
BayesModel.trainModel("train_data.csv", BayesModel.SKIP_FIRST)
train_accuracy = BayesModel.testModel("test_data.csv", CUTOFF_VALUE, BayesModel.SKIP_FIRST)
print train_accuracy
test_accuracy = BayesModel.testModel("train_data.csv", CUTOFF_VALUE, BayesModel.SKIP_FIRST)
print test_accuracy

BayesModel.construct_confusion_matrix("test_data.csv", CUTOFF_VALUE, BayesModel.SKIP_FIRST)
