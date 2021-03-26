import json
import math
from sim_world.nim.Nim import Nim
from MCTS.TreeNode import TreeNode
from sim_world.sim_world import SimWorld
from MCTS.GenerateMCTS import MCTS
from Models.NeuralNet import NeuralActor
from Models import SaveLoadModel
from sim_world.hex.Hex import Hex
from typing import List

def doGames(numberOfTreeGames: int, numberOfGames: int, saveInterval, input_size: int, output_size: int, hiddenLayersDimension: List, learningRate: int, simWorld: SimWorld) -> None:
    ANET = NeuralActor(input_size, output_size, hiddenLayersDimension, learningRate)
    for i in range(numberOfGames):
        currentState = simWorld.getStateHash()
        root = TreeNode(state=currentState, parent=None, possibleActions = output_size)
        mcts = MCTS(
            root=root
        )
        while not simWorld.isWinState():
            #monteCarloSimWorld = SimWorld(root)
            for i in range(numberOfTreeGames):
                mcts.treeSearch(currentState, simWorld)
                reward = mcts.rollout(ANET)
                mcts.backPropogate(reward)
            actionDistributtion = mcts.currentNode.numTakenAction
            RBUF.append((mcts.simWorld.getStateHash(), actionDistributtion))

            # TODO add epsilon
            bestMove = None
            bestMoveValue = -math.inf
            for move in range(len(actionDistributtion)):
                if bestMoveValue < actionDistributtion[move]:
                    bestMoveValue = actionDistributtion[move]
                    bestMove = move

            mcts.makeAction(bestMove)
            mcts.reRootTree()

        ANET.trainOnRBUF(RBUF, minibatchSize = RBUFSamples)
        if numberOfGames % saveInterval == 0:
            saveInterval.SaveModel(ANET.neuralNet.parameters, fileName)
            # TODO Save ANET’s current parameters for later use in tournament play

def main():
    # Load parameters from file
    with open('project2/parameters.json') as f:
        parameters = json.load(f)

    gameType = parameters['game_type']
    boardType = parameters['board_type']
    boardSize = parameters['board_size']
    boardSize = parameters['board_size']
    numEpisodes = parameters['mcts_num_episodes']
    numSearchGamesPerMove = parameters['mcts_n_of_search_games_per_move']
    saveInterval = parameters['save_interval']
    learningRate = parameters['anet_learning_rate']
    activationFunction = parameters['anet_activation_function']
    optimizer = parameters['anet_optimizer']
    hiddenLayersDim = parameters['anet_hidden_layers_and_neurons_per_layer']
    numCachedToppPreparations = parameters['anet_n_cached_topp_preparations']
    numToppGamesToPlay = parameters['anet_n_of_topp_games_to_be_played']
    if gameType == "hex":
        simWorld = Hex(
            boardType=boardType,
            boardWith=boardSize,
            playerTurn=1
            
        )
        input_size =  (boardSize * boardSize) + 1
        output_size = boardSize * boardSize

        #simWorld.playGame()

    elif gameType == "nim":
        simWorld = Nim(
            10,
            3
        )
        input_size =  2
        output_size = 3
        #nim.playGayme()
    else:
        print("Game not specified. Quitting...")
    # is = save interval for ANET (the actor network) parameters

    doGames(
        numberOfTreeGames = numSearchGamesPerMove,
        numberOfGames = numEpisodes, 
        saveInterval = saveInterval, 
        input_size =  input_size,
        output_size = output_size,
        hiddenLayersDimension= hiddenLayersDim,
        learningRate = learningRate,
        simWorld = simWorld
    )

    # clear replay buffer (RBUF)

    # randomly initialize parameters for ANET

    # for each number in actial games

    # simWorld = Initialize the actual game board to an empty board

    # currentState = startingBoardState (trengs denne?)

    # while simWorld not in final state
    # MTCS = initialize monte carlo sim world to same as root
    # for each number_search_games:
    # use three policy Pi to search from root to leaf
    # update MTCS.simWorld with each move

    # use ANET


if __name__ == '__main__':
    print("Run!")
    main()

RBUF = []
RBUFSamples = 10

fileName = "test"
