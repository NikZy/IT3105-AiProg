from NeuralNet import NeuralNetwork
from NeuralNet import StateToArray
from SimWorld import SAP

import torch
import torch.nn as nn
import math
import tensorflow as tf
import numpy as np
import torch.optim as optim


class CriticNeural:
    def __init__(self,
                 boardSize,
                 boardType,
                 hiddenLayersDim,
                 learningRate=0.1,
                 eligibilityDecay=0.9,
                 valueTable={},
                 discountFactor=0.9
                 ) -> None:
        self.valueTable = valueTable
        self.eligibilityDecay = eligibilityDecay
        self.eligibility = {}
        self.tdError = 0
        self.learningRate = learningRate
        self.discountFactor = discountFactor
        # TODO: Pass in parameters
        inputSize = 0
        if boardType == "triangle":
            inputSize = ((boardSize ** 2) + boardSize) / 2
        elif boardType == "diamond":
            inputSize = boardSize ** 2
        self.neuralNet = NeuralNetwork(
            input_size=inputSize,
            hidden_layers_dim=hiddenLayersDim
        )
        self.optimizer = optim.SGD(
            self.neuralNet.parameters(), lr=self.learningRate)

        self.criterion = nn.MSELoss()

    def resetEligibility(self):
        self.eligibility = {}

    def getValueTable(self) -> dict:
        return self.valueTable

    def getValue(self, state: list) -> float:
        state = StateToArray(state)
        return self.neuralNet(torch.tensor([int(s) for s in state], dtype=torch.float32)).item()

    # def setValue(self, key, value):
    #     self.valueTable[key] = value

    def updateTDError(self, reward, state, nextState):
        self.tdError = reward + \
            (self.discountFactor * self.getValue(nextState)) - self.getValue(state)

    def modify_gradients(self, gradients, parameters):
        print(parameters, gradients)
        print(len(parameters), len(gradients))
        """for num, f in parameters:
            self.e[num] = self.get_e(num) + f.grad * \
                ((2 * float(td_error)) ** (-1))
            f.grad = float(td_error) * self.e[num]"""

        return gradients

    def getEligibility(self, nodeIndex):
        if nodeIndex not in self.eligibility:
            self.eligibility[nodeIndex] = 0
        return self.eligibility[nodeIndex]

    def updateValue(self, stateActionPair: SAP):
        state = StateToArray(stateActionPair.state)
        input_tensor = torch.tensor(
            [int(s)for s in state], dtype=torch.float32)

        self.optimizer.zero_grad()
        output = self.neuralNet(input_tensor)

        if self.tdError == 0:
            self.tdError = 0.000000000001

        loss = self.criterion(output + self.tdError, output)

        loss.backward()

        for nodeIndex, node in enumerate(self.neuralNet.parameters()):
            self.eligibility[nodeIndex] = self.getEligibility(nodeIndex) + node.grad * \
                ((2 * float(self.tdError)) ** (-1))
            node.grad = float(self.tdError) * self.eligibility[nodeIndex]

        self.optimizer.step()

    def gen_loss(self, features, targets, avg=False):
        # Feed-forward pass to produce outputs/predictions
        predictions = self.model(features)
        # model.loss = the loss function
        loss = self.model.loss(targets, predictions)
        return tf.reduce_mean(loss).numpy() if avg else loss

    def decayEligibility(self, StateActionPair):
        currentEligibility = self.eligibility[StateActionPair.stateHash]
        self.eligibility[StateActionPair.stateHash] = currentEligibility * \
            self.discountFactor * self.eligibilityDecay
