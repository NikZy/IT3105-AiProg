import json
import math
from project2.sim_world.nim.Nim import Nim
from project2.MCTS.TreeNode import TreeNode
from project2.sim_world.sim_world import SimWorld
from project2.MCTS.GenerateMCTS import MCTS
from project2.Models.NeuralNet import NeuralActor
from project2.Models import SaveLoadModel
from project2.sim_world.hex.Hex import Hex
from typing import List, Tuple
from project2.Client_side.BasicClientActor import BasicClientActor
import random
from typing import List
from project2.Models.SaveLoadModel import SaveModel
import copy

class ReinforcementLearningSystem:
    def __init__(
            self,
            numberOfTreeGames: int,
            numberOfGames: int,
            saveInterval:int,
            ANET:NeuralActor,
            explorationBias:float,
            epsilon :float,
            RBUFsamples:int,
            exponentialDistributionFactor:float,
            simWorldTemplate: SimWorld,
            fileName: str
    ):
        self.RBuffer = []
        self.numberOfTreeGames = numberOfTreeGames
        self.numberOfGames = numberOfGames
        self.saveInterval = saveInterval
        self.ANET = ANET
        self.explorationBias = explorationBias
        self.epsilon = epsilon
        self.RBUFsamples = RBUFsamples
        self.exponentialDistributionFactor = exponentialDistributionFactor
        self.simWorldTemplate = simWorldTemplate
        self.fileName = fileName

    def mctsSearch(self, simWorld) -> int:
        state =simWorld.getStateHash()
        mcts = MCTS(
            root= TreeNode(
                state = state,
                parent = None,
                possibleActions=simWorld.getMaxPossibleActionSpace(),
            ),
            ExplorationBias=1
        )
        for gameNr in range(self.numberOfTreeGames):
            mcts.treeSearch(state,simWorld)
            reward = mcts.rollout(self.ANET)
            mcts.backPropogate(reward)

        actionDistributtion = mcts.normaliseActionDistribution(stateHash=str(simWorld.getStateHash()))
        print("Action dist", actionDistributtion)

        # TODO: Use different action policy for tournament?
        bestAction = self.chooseActionPolicy(
            actionDistribution=actionDistributtion,
            simWorld=simWorld
        )
        return bestAction



    def trainNeuralNet(self, numberOfGames):
        print("Training neuralnet")
        SaveModel(self.ANET.neuralNet, self.fileName + "0")
        for game in range(numberOfGames):
            print(f"Playing game number: {game}")
            simWorld = copy.deepcopy(self.simWorldTemplate)
            # Random start player
            if(0.5> random.uniform(0,1)):
                simWorld.playerTurn = -1

            currentState = simWorld.getStateHash()
            root = TreeNode(state=currentState, parent=None, possibleActions = simWorld.getMaxPossibleActionSpace())
            mcts = MCTS(
                root=root,
                ExplorationBias = self.explorationBias
            )
            while not simWorld.isWinState():
                for e in range(self.numberOfTreeGames):
                    mcts.treeSearch(currentState, simWorld)
                    reward = mcts.rollout(self.ANET)
                    mcts.backPropogate(reward)

                actionDistribution =  mcts.normaliseActionDistribution(stateHash=str(simWorld.getStateHash()))
                print(actionDistribution)

                self.RBuffer.append((mcts.currentNode.state, actionDistribution))

                bestMove = self.chooseActionPolicy(
                    actionDistribution=actionDistribution,
                    simWorld=simWorld,
                )
                #print("SW, BM", simWorld.state, (bestMove+1), actionDistribution)

                # Sync both sim worlds to be equal
                mcts.simWorld = copy.deepcopy(simWorld)
                mcts.makeAction(bestMove)
                simWorld.makeAction(bestMove)
                mcts.reRootTree()

            # Print ANET Values for debugging
            """
            for i in range(1, 12 +1):
                nonstaones = [0] * (12 - i)
                nonnonstaones = [1] * (i)
                state = [-1] + nonstaones + nonnonstaones
                state2 = [1] + nonstaones + nonnonstaones
                print(i, ANET.getDistributionForState(state), ANET.defaultPolicyFindAction([0,1],state))
                print(i, ANET.getDistributionForState(state2), ANET.defaultPolicyFindAction([0,1],state2))
            """
            self.ANET.trainOnRBUF(RBUF = self.RBuffer, minibatchSize = self.RBUFsamples, exponentialDistributionFactor = self.exponentialDistributionFactor)

            if (game) % self.saveInterval == 0 and game != 0:
                SaveModel(self.ANET.neuralNet,self.fileName + str(game + 1))

        self.playAgainstAnet()


    def playAgainstAnet(self):
        simWorld = copy.deepcopy(self.simWorldTemplate)
        simWorld.playAgainst(self.ANET)

    def chooseActionPolicy(self, actionDistribution, simWorld) -> int:
        bestMove = 0
        if self.epsilon > random.uniform(0, 1) and (not simWorld.isWinState()):
            if len(simWorld.getPossibleActions()) > 1:
                bestMove = simWorld.getPossibleActions()[random.randint(0, len(simWorld.getPossibleActions()) - 1)]
        else:
            bestMove = None
            bestMoveValue = -math.inf
            for move in range(len(actionDistribution)):
                if bestMoveValue <actionDistribution[move] and move in simWorld.getPossibleActions():
                    bestMoveValue = actionDistribution[move]
                    bestMove = move
        return bestMove

    def saveModel(self):
        pass
