from typing import List, Dict
from project2.Tournament.TournamentPlotter import TournamentPlotter
from project2.Models.SaveLoadModel import LoadModel, LoadTorchModel
import copy
import json

from project2.visualization.boardAnimator import BoardAnimator


class LocalTournament:

    def __init__(self, agents: List, roundRobin:bool, simWorldTemplate, agentNames: Dict):
        with open('project2/parameters.json') as f:
            parameters = json.load(f)
        numCachedToppPreparations = parameters['anet_n_cached_topp_preparations']
        numToppGamesToPlay = parameters['anet_n_of_topp_games_to_be_played']
        saveInterval = parameters['save_interval']
        fileNamePrefix = parameters['file_name']
        boardSize = parameters['board_size']
        gameType = parameters['game_type']
        self.visualizeBoardWhileRunning = parameters['visualize_board_while_running']
        visualizeInterval = parameters['visualize_interval']

        self.agents = agents
        self.numberOfGames = int(numToppGamesToPlay/4) if numToppGamesToPlay > 4 else 1
        self.roundRobin = roundRobin
        self.simWorldTemplate = simWorldTemplate
        self.agentNames = agentNames
        self.TournamentPlotter = TournamentPlotter(self.agentNames)
        self.boardVisualizer = BoardAnimator(self.simWorldTemplate.boardWidth)
        # Load agents based on parameters
        for i in range(0, numCachedToppPreparations*saveInterval, saveInterval):
            print(f"Load model for TOP: {gameType}{boardSize}{fileNamePrefix}{i}")
            modelName =  gameType + str(boardSize) + fileNamePrefix + str(i)
            NeuralActor = LoadTorchModel(f"{gameType}{boardSize}{fileNamePrefix}{i}")
            self.agentNames[NeuralActor] = fileNamePrefix+str(i)
            self.agents.append(NeuralActor)


    def runTournament(self):
        print("Tournament start")
        if(len(self.agents) >= 2):
            if self.roundRobin:
                totalWins = {}
                versusGames = {}
                for agent in self.agents:
                    totalWins[agent] = 0
                    versusGames[self.agentNames[agent]] = [0]*len(self.agents)
                for i in range(len(self.agents)-1):
                    for j in range(i+1, len(self.agents)):
                        for numGames in range(self.numberOfGames):
                            results = self.playFourGames(self.agents[i], self.agents[j])
                            versusGames[self.agentNames[self.agents[i]]][j] += results[self.agents[i]]
                            versusGames[self.agentNames[self.agents[j]]][i] += results[self.agents[j]]
                            for agent in results.keys():
                                totalWins[agent] += results[agent]
                self.printTotalWins(totalWins)
                self.TournamentPlotter.plottWins(totalWins)
                print("----------\nAgent stats:")
                for agentName in versusGames.keys():
                    print("-------\n   ",agentName)
                    print([x / (self.numberOfGames*4) for x in versusGames[agentName]])
            else:
                for i in range(len(self.agents)-1):
                    pairWins = {self.agents[i]: 0, self.agents[i+1]: 0}
                    for numGames in range(self.numberOfGames):
                            results = self.playFourGames(self.agents[i], self.agents[i+1])
                            for agent in results.keys():
                                pairWins[agent] += results[agent]
                self.printTotalWins(pairWins)
                self.TournamentPlotter.plottWins(pairWins)
        print("Tournament over")

    def printTotalWins(self, totalWins):
        print("Tournament results")
        for agent, wins in totalWins.items():
            print(self.agentNames[agent], ": ", wins, " number of wins")

    def playFourGames(self, agent1, agent2):  # First and second as 1 and -1 = 4 games
        wins = {agent1: 0, agent2: 0}
        playerDict = {-1: agent1, 1: agent2}
        wins[self.playGame(playerDict, -1)] += 1
        wins[self.playGame(playerDict, 1)] += 1
        playerDict = {1: agent1, -1: agent2}
        wins[self.playGame(playerDict, -1)] += 1
        wins[self.playGame(playerDict, 1)] += 1
        return wins

    def playGame(self, playerDict: Dict, startingPlayer: int):
        simWorld = copy.deepcopy(self.simWorldTemplate)
        simWorld.playerTurn = startingPlayer
        while not simWorld.isWinState():  # Noen vinner altid? Mulig vi trenger en til sjekk. Random krasjer hvis possible = 0
            action = playerDict[simWorld.playerTurn].defaultPolicyFindAction(possibleActions = simWorld.getPossibleActions(), state = simWorld.getStateHash())
            simWorld.makeAction(action)
            if self.visualizeBoardWhileRunning:
                self.boardVisualizer.addAnimationState(simWorld.getStateHash())

        if self.visualizeBoardWhileRunning:
            print(f"----Visualizing match-----")
            print(f"Starting player (green): {self.agentNames[playerDict[startingPlayer]]}")
            print(f"Playing against (red): {self.agentNames[playerDict[startingPlayer * -1]]}")
            self.boardVisualizer.animateEpisode()
            self.boardVisualizer.clearEpisodes()
        return playerDict[-simWorld.playerTurn]