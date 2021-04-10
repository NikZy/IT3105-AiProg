import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import random
from typing import List
from torch.autograd import Variable
import torch.nn.functional as F
import torch.optim as optim
import math
import random

class NeuralNetwork(nn.Module):
    def __init__(self, input_size, output_size, hiddenLayersDimension=[]):
        super(NeuralNetwork, self).__init__()

        self.layers = nn.ModuleList()

        current_dim = input_size

        for dimension in hiddenLayersDimension:
            self.layers.append(nn.Linear(int(current_dim), dimension))
            current_dim = dimension

        self.layers.append(nn.Linear(current_dim, output_size))
        

    def forward(self, input):
        # Hidden layers
        for layer in self.layers[:-1]:
            input = F.relu(layer(input))  # Se på å bruke noe sigmoid eller noe annet også kanskje?
            
        # Output layer
        # Hyperbolic tangent
        out = torch.tanh(self.layers[-1](input))
        # print("out: ", out)
        return out
        
class NeuralActor ():
    def __init__(self,
                 inputSize,
                 outputSize,
                 hiddenLayersDim,
                 learningRate=0.9,
                 epsilon = 0
                 ):
        self.learningRate = learningRate

        self.neuralNet = NeuralNetwork(
            input_size=inputSize,
            hiddenLayersDimension=hiddenLayersDim,
            output_size = outputSize
        )
        # Optimizer stochastic gradient descent
        self.optimizer = optim.SGD(
            self.neuralNet.parameters(), lr=self.learningRate)

        self.lossFunction = nn.MSELoss()
        self.epsilon = epsilon

    '''def loss2(self, output, target):
        sum = 0
        print(output, target)
        for k in range(len(output)):
            print(self.safelog(output[k]))
            sum -= target[k]*self.safelog(output[k])
        loss = torch.tensor(sum)
        return loss

    def safelog(self, tensor, base=0.0001):
        return math.log(max(tensor,base))'''

    def trainOnRBUF(self, RBUF, minibatchSize:int): 
        # print("RBUF", RBUF)
        minibatch = random.sample(RBUF, k=minibatchSize)
        for item in minibatch:
            state = item[0]
            actionDistribution = item[1]
            # Map state to a pytorch friendly format
            input = torch.tensor(
                [int(s)for s in state], dtype=torch.float32)

            # We have to zero out gradients for each pass, or they will accumulate
            self.optimizer.zero_grad()
            output = self.neuralNet(input)#.tolist()
            
            #print(torch.tensor(actionDistribution), output)
            input2 = Variable(torch.randn(3, 1), requires_grad=True)
            target2 = Variable(torch.randn(3, 1))
            # print(input2, target2)


            loss = self.lossFunction(output, torch.tensor(actionDistribution))
            # self.loss2(output, actionDistribution) 
            # print("loss", loss)

            # Store the gradients for the network
            loss.backward(retain_graph = True)

            # Update the weights for the network using the gradients stored above
            self.optimizer.step()

    def getDistributionForState(self, state: List):
        input = torch.tensor(
            [int(s)for s in state], dtype=torch.float32)
        self.optimizer.zero_grad()
        output = self.neuralNet(input)
        # print("output", output)
        return output.detach().numpy()

    def defaultPolicyFindAction(self, possibleActions, state) -> int:
        distribution  = self.getDistributionForState(state)
        #print("distrubution, state", distribution, state)
        bestActionValue = -math.inf
        bestActionIndex = 0
        for index, value in enumerate(distribution):
            if index in possibleActions:
                if value > bestActionValue:
                    bestActionValue = value 
                    bestActionIndex = index
        if self.epsilon > random.uniform(0, 1) and len(possibleActions) != 0:
            bestActionIndex = possibleActions[random.randint(0, len(possibleActions) -1)]
        return bestActionIndex