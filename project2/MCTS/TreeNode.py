import math

class TreeNode:
    def __init__(self, state, possibleActions:int,parent=None):
        self.numTimesVisited = 0,
        self.numTakenAction = [0.00001] * possibleActions
        self.totalEvaluation = 0  # Accumulated  evaluation of this node
        self.children = {}
        self.parent = parent
        self.state = state
        self.c = 1
    def getExpectedResult(self, action: int) -> float:
        return self.totalEvaluation / self.numTakenAction[action]

    def addChild(self, action: int, child) -> TreeNode:
        if action in self.children.keys():
            raise Exception("duplicate child is illigal (no twins!)")
        self.children[action] = child
        child.parent = self
        return child
        
    def getExplorationBias(self, action: int) -> float:
        return self.c * math.sqrt(math.log(self.numTimesVisited) / self.numTakenAction[action])

    def addActionTaken(self, action: int):
        self.numTakenAction[action] += 1