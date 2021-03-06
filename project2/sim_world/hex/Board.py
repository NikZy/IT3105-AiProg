import networkx as nx
import matplotlib.pyplot as plt
import os
import plotly.graph_objects as go
import plotly.basedatatypes as base
from typing import List, Tuple
import plotly.graph_objects as go
from project2.sim_world.hex.Node import Peg
from enum import Enum


class Boardtype(Enum):
    triangle = "triangle"
    diamond = "diamond"


class HexBoard():
    def __init__(self,
                 boardType: Boardtype,
                 boardWidth: int,
                 removeLocations: List[(int)] = [],
                 loadedHexBoardState: List[List[int]] = None
                 ) -> None:
        self.defaultNodeValue = 0
        self.boardWidth = boardWidth
        if(loadedHexBoardState):
            self.board = loadedHexBoardState
        elif (boardType is Boardtype.triangle):
            self.board = self.generateTriangle(width=boardWidth)
        elif (boardType is Boardtype.diamond):
            self.board = self.generateDiamond(width=boardWidth)
        else:  # boardType has to be diamond
            raise ValueError("BoardType has to be triangle or diamond")

    def generateTriangle(self, width: int) -> List[List[int]]:
        board = []
        for i in range(1, width+1):
            board.append(i * [self.defaultNodeValue])
        return board

    def generateDiamond(self, width: int) -> List[List[int]]:
        board = self.generateTriangle(width)
        for i in range(width - 1, 0, -1):
            board.append(i * [self.defaultNodeValue])
        return board

    def __repr__(self):
        return self.board

    def __str__(self):
        return str(self.board)

    def __iter__(self):
        return self.board


class BoardState():
    def __init__(self,
                 hexBoard: HexBoard,
                 formatHexBoard: bool = False, # TODO: Remove?
                 loadedHexBoardState: List[int] = None,
                 boardWidth = None
                 ) -> None:
        self.state = self._boardToNodes(hexBoard=hexBoard)
        self.hexBoard = hexBoard

        # If loading from a tournament state
        if formatHexBoard:
            self.boardWidth = boardWidth
            self.generateTournamentActionMaps()
            formatedBoard = self.tournamentStateToSimworldState(loadedHexBoardState, boardWidth=boardWidth)
            hexboard = HexBoard(
                boardType=Boardtype["diamond"],
                boardWidth= boardWidth,
                loadedHexBoardState=formatedBoard
            )
            self.state = self._boardToNodes(hexboard)


    def getStateList(self) -> List[Peg]:
        return self.state


    def _boardToNodes(self, hexBoard: HexBoard) -> List[List[Peg]]:
        board = hexBoard.board
        pegList = []
        for x in range(len(board)):
            layerList = []
            for y in range(len(board[x])):
                layerList.append(Peg((x, y), board[x][y]))
                if(y > 0):
                    layerList[y].addBiDirectionalNeighbour(
                        layerList[y - 1], "0,-1")
                if(x > 0):
                    layerGrowthFactor = len(board[x - 1]) - len(board[x])
                    secoundParentConnection = y + layerGrowthFactor  # other node above you
                    if(y < len(pegList[x-1])):
                        # add yourself as connection to node above you
                        pegList[x-1][y].addBiDirectionalNeighbour(
                            layerList[y], "-1," + str(-layerGrowthFactor))
                    if(secoundParentConnection >= 0 and secoundParentConnection < len(pegList[x - 1])):
                        # add yourself as connection to other node above you
                        pegList[x-1][secoundParentConnection].addBiDirectionalNeighbour(
                            layerList[y], "-1," + str(layerGrowthFactor))

            pegList.append(layerList)
        return pegList

    def countPegs(self):
        counter = 0
        for layer in self.state:
            for peg in layer:
                counter += peg.pegValue
        return counter

    def setPegValue(self, location: Tuple, newValue: int) -> bool:
        self.state[location[0]][location[1]].pegValue = newValue
        return True

    def getPegNode(self, location: Tuple):
        return self.state[location[0]][location[1]]

    def generateTournamentActionMaps(self):  # {simworld action (row, column): tournament acition (row, column)}
        self.simWorldToTournament = {}
        for c in range(len(self.state)):
            for r in range(len(self.state[c])):
                col = c
                row = r
                if(col < self.boardWidth): #Riktig?
                    self.simWorldToTournament[(c,r)] = (col-row,row)
                else:
                    self.simWorldToTournament[(c,r)] = (self.boardWidth-row-1,row+col-self.boardWidth+1)
        self.tournamentToSimworld = {}
        for key in self.simWorldToTournament.keys():
            self.tournamentToSimworld[self.simWorldToTournament[key]] = key
        return self.simWorldToTournament

    def tournamentStateToSimworldState(self, state: List, boardWidth: int) -> list:  # state is list [player, 0,0,1,2,0,...] -> [[0,0],[1,0],[1,1]] (player missing)
        simWorldBoard = []
        playerTurn = 1 if state[0] == 1 else -1

        for i in range(1, boardWidth+1):
            simWorldBoard.append(i * [0])
        for i in range(boardWidth- 1, 0, -1):
            simWorldBoard.append(i * [0])  # Creates empty sim worl board
        for col in range(len(simWorldBoard)):
            for row in range(len(simWorldBoard[col])):
                if(col < boardWidth):
                    self.simWorldToTournament[(col,row)] = (col-row,row)
                else:
                    self.simWorldToTournament[(col,row)] = (boardWidth-row-1,row+col-boardWidth+1)
        index = 1
        for col in range(boardWidth):
            for row in range(boardWidth):
                coord = self.tournamentToSimworld[(col, row)]
                simWorldBoard[coord[0]][coord[1]] = state[index]
                index += 1
        return simWorldBoard

    def __repr__(self):
        return self.state

    def __str__(self):
        return str(self.state)


if __name__ == "__main__":
    #print(HexBoard(Boardtype["triangle"], 4))
    board = HexBoard(Boardtype["diamond"], 4)
    state = BoardState(board)
    print(state)
