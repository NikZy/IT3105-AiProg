import json
import math
from project2.sim_world.nim.Nim import Nim
from project2.MCTS.TreeNode import TreeNode
from project2.sim_world.sim_world import SimWorld
from project2.MCTS.GenerateMCTS import MCTS
from project2.Models.NeuralNet import NeuralActor
from project2.Models.RandomAgent import RandomAgent
from project2.Models import SaveLoadModel
from project2.sim_world.hex.Hex import Hex
from project2.Tournament.LocalTournament import LocalTournament
from typing import List
from project2.Client_side.BasicClientActor import BasicClientActor
import random
from typing import List
from project2.Models.SaveLoadModel import SaveModel, LoadModel, LoadTorchModel
import copy
from project2.RLS import ReinforcementLearningSystem


RBUF = []
fileName = "test"

def main():
    # Load parameters from file
    with open('project2/parameters.json') as f:
        parameters = json.load(f)

    operationMode = parameters["operation_mode"]
    gameType = parameters['game_type']
    boardType = parameters['board_type']
    boardSize = parameters['board_size']

    learningRate = parameters['anet_learning_rate']
    activationFunction = parameters['anet_activation_function']
    outputActivationFunction = parameters['output_activation_function']
    optimizer = parameters['anet_optimizer']
    convLayersDim = parameters['anet_conv_layers_and_neurons_per_layer']
    denseLayersDim = parameters['anet_dense_layers_and_neurons_per_layer']
    lossFunction = parameters['loss_function']
    anetGenerationModelToLoad = parameters["anet_model_to_load"]

    explorationBias = parameters['explorationBias']
    RBUFsamples = parameters['RBUFsamples']
    exponentialDistributionFactor = parameters['exponentialDistributionFactor']

    numEpisodes = parameters['mcts_num_episodes']
    numSearchGamesPerMove = parameters['mcts_n_of_search_games_per_move']
    saveInterval = parameters['save_interval']
    fileNamePrefix = parameters['file_name']
    visualizeBoardWhileRunning = parameters['visualize_board_while_running']
    visualizeInterval = parameters['visualize_interval']
    modelSaveLocation = parameters["model_save_location"]

    numCachedToppPreparations = parameters['anet_n_cached_topp_preparations']
    numToppGamesToPlay = parameters['anet_n_of_topp_games_to_be_played']

    if gameType == "hex":
        simWorld = Hex(
            boardType=boardType,
            boardWidth=boardSize,
            playerTurn=1,
            # loadedHexBoardState=[-1, 0, 0, 0, 1, -1, 0, 0, 0, 0],
        )
        input_size =  (boardSize * boardSize) + 1
        output_size = boardSize * boardSize

        #simWorld.playGame()

    elif gameType == "nim":
        simWorld = Nim(
            boardSize,
            2
        )
        input_size =  boardSize + 1
        output_size = 2
        #nim.playGayme()
    else:
        print("Game not specified. Quitting...")

    # Initiate Neural Net
    if len(anetGenerationModelToLoad) == 0:
        print("Creating a new Neural Network")
        ANET = NeuralActor(
            input_size = input_size,
            output_size = output_size,
            denseLayersDim = denseLayersDim,
            convLayersDim = convLayersDim,
            learningRate = learningRate,
            lossFunction = lossFunction,
            optimizer = optimizer,
            activation = activationFunction,
            outputActivation = outputActivationFunction
        )
        anetGenerationNumber = 0
    else:
        # Load from a previoussly trained model
        print(f"Loading anet: {gameType + str(boardSize )+fileNamePrefix + anetGenerationModelToLoad}")
        ANET = LoadTorchModel(fileName=gameType+ str(boardSize)+fileNamePrefix + anetGenerationModelToLoad)
        anetGenerationNumber = int(anetGenerationModelToLoad)

    # Initiate ReinforcementLearningSystem
    RLS = ReinforcementLearningSystem(
            numberOfTreeGames = numSearchGamesPerMove,
            numberOfGames = numEpisodes,
            saveInterval = saveInterval,
            ANET = ANET,
            explorationBias = explorationBias,
            RBUFsamples = RBUFsamples,
            exponentialDistributionFactor = exponentialDistributionFactor,
            simWorldTemplate = simWorld,
            fileName = gameType + str(boardSize) + fileNamePrefix,
            visualizeBoardWhileRunning = visualizeBoardWhileRunning,
            visualizeInterval = visualizeInterval
    )

    # is = save interval for ANET (the actor network) parameters
    if(operationMode == "play"):
        print("Operation mode: Play")
        simWorld.playGame()

    elif(operationMode == "playAgainst"):
        print("Operation mode: Play against neural net")
        ANET = LoadTorchModel(fileName=gameType+ str(boardSize)+fileNamePrefix + str(numCachedToppPreparations * saveInterval))
        simWorld.playAgainst(ANET)
    
    elif (operationMode == "train"):
        print("Operation mode: train")
        print(input_size, output_size, convLayersDim, denseLayersDim, learningRate)
        RLS.trainNeuralNet(numberOfGames=numEpisodes, anetGenerationNumber = anetGenerationNumber)

    elif operationMode == "tournament":
        print("Operation mode: Tournament")
        bsa = BasicClientActor(
            verbose=True,
            RLS = RLS
        )
        bsa.connect_to_server()
    elif operationMode == "topp":
        print("Operation mode: TOPP (Local tournament)")
        testTournament(
            simWorldTemplate=simWorld,
        )
    else:
        raise Exception("Operation  mode not specified choose (play/train)")

def testTournament(simWorldTemplate: SimWorld):
    agents = [
    ]
    agentNames = {
    }
    testTournament = LocalTournament(agents=agents, roundRobin = True, simWorldTemplate= simWorldTemplate, agentNames=agentNames)
    testTournament.runTournament()


if __name__ == '__main__':
    print("Run!")
    main()
