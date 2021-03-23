from sim_world.sim_world import SimWorld
from sim_world.hex.Board import Boardtype, BoardState
from sim_world.hex.Board import HexBoard, Boardtype
from sim_world.hex.VisualizeBoard import VisualizePegs
from typing import List, Tuple


class Hex(SimWorld):
    """
        Hex board game
    """

    def __init__(
        self,
        boardType: str,
        boardWith: int,
        playerTurn: int
    ):
        self.playerTurn = playerTurn
        self.boardWidth = boardWith
        hexBoard = HexBoard(Boardtype[boardType], boardWith)
        self.state = BoardState(hexBoard)
        # Dic[actionNumberIndex] -> (x, y) cordinates
        self.possibleActions = self.generatePossibleActions()

        self.upperLeft, self.upperRight, self.lowerLeft, self.lowerRight = self.generateBoardSideCordinates()
        # TODO: Add action log

    def generatePossibleActions(self):
        board = self.state.state
        actions = {}
        count = 0
        for x in range(len(board)):
            for y in range(len(board[x])):
                actions[count] = (x, y)
                count += 1
        return actions

    def getPossibleActions(self):
        return self.possibleActions.keys()

    def isAllowedAction(self, actionTuple: Tuple[int]) -> bool:
        for key in self.getPossibleActions():
            value = self.possibleActions.get(key)
            if value == actionTuple:
                return key
        return False
        # return True if action in self.possibleActions.values() else False

    def makeAction(self, action: int):
        action = self.possibleActions.get(action)
        self.state.setPegValue(action, self.playerTurn)  # Update boardState
        # remove action from possibleActions
        self.possibleActions[action] = None
        self.changePlayerTurn()

    def isWinState(self) -> bool:
        k = 4 - 1
        pass

    def generateBoardSideCordinates(self):
        """
            The sides of the board used to check if a win state is reached.
            Player 1 must have a connected path from upperLeft location to a lowerRight location.
            Player 2 must have the same for upperRight, to lowerLeft
            Example locations of a board with width 3:
                upperLeft = [00, 10, 20]
                upperRight = [11, 22, 33]
                lowerLeft = [30, 40, 50]
                lowerRight = [42, 51, 60]
        """
        upperLeft = [(n, 0) for n in range(self.boardWidth - 1)]
        upperRight = [(x, x) for x in range(1, self.boardWidth)]
        lowerLeft = [(x, 0)
                     for x in range(self.boardWidth - 1, self.boardWidth*2 - 2)]
        lowerRight = [(x, y) for x, y in zip(range(
            self.boardWidth, self.boardWidth*2 - 1), range(self.boardWidth - 2, -1, -1))]

        return upperLeft, upperRight, lowerLeft, lowerRight

    def depthFirstSearch(self, node, isTheRightState):
        # if isTheRightState
        #  return True
        # for child in children:
        # depthFirstSearch(child)
        pass

    def getReward(self) -> int:
        pass

    def changePlayerTurn(self) -> int:
        self.playerTurn = 1 if self.playerTurn == -1 else -1
        return self.playerTurn

    def getStateHash(self) -> str:
        pass

    def getMaxPossibleActionSpace(self) -> int:
        return self.boardWidth**2

    def visualizeBord(self):
        VisualizePegs(
            pegList=self.state
        )

    def playGame(self):
        self.generateBoardSideCordinates()
        while (not self.isWinState()):
            self.changePlayerTurn()
            print(self.possibleActions)
            self.visualizeBord()
            playerInput = input(
                f"Player {self.playerTurn}, where do you place your peg? "
            )
            actionTuple = tuple(list(map(int, playerInput.split(','))))
            print(actionTuple)
            actionNumber = self.isAllowedAction(actionTuple)
            print(actionNumber)
            if(actionNumber == False and actionNumber != 0):
                raise Exception("Not a valid action")
            self.makeAction(actionNumber)


class Cordinates:
    def __init__(self, x, y):
        self.x = x
        self.y = y