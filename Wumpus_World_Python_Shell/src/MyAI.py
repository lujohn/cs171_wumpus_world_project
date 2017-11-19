# ======================================================================
# FILE:        MyAI.py
#
# AUTHOR:      Abdullah Younis
#
# DESCRIPTION: This file contains your agent class, which you will
#              implement. You are responsible for implementing the
#              'getAction' function and any helper methods you feel you
#              need.
#
# NOTES:       - If you are having trouble understanding how the shell
#                works, look at the other parts of the code, as well as
#                the documentation.
#
#              - You are only allowed to make changes to this portion of
#                the code. Any changes to other portions of the code will
#                be lost when the tournament runs your code.
# ======================================================================

# ---------------------------- Minimal AI: -----------------------------
# First Step is always to move forward.
# If a glitter is ever perceived:
#   Grab it, then head right back to start node and climb
# If a breeze or stench is perceived:
    # Head back to start node and climb 

from Agent import Agent
import queue

class MyAI ( Agent ):

    def __init__ ( self ):
        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================
        
        # -------------------------  State Information ---------------------------
        self.firstTurn = True
        self.wumpusKilled = False
        self.headingHome = False
        self.currentSq = (1,1)
        self.prevPercept = []

        self.facing = 'right'
        # Keep track of world dimension (from "bumps")
        self.xDim = -1
        self.yDim = -1

        self.moveBuffer = list()
        self.pathHistory = list()

        # Matricies are all 10 x 10 grid with entries initialized to False
        self.breezeMat = [[False for x in range(10)] for y in range(10)]
        self.stenchMat = [[False for x in range(10)] for y in range(10)]
        self.safeMat = [[False for x in range(10)] for y in range(10)]

        # Exploration Frontier (LIFO structure)
        self.exploreFrontier = []
        self.exploredMat = []

        # Debugging
        self.headingToSquare = ()

        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================

    def getAction( self, stench, breeze, glitter, bump, scream ):
        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================
        print('facing: (beg. of turn) %s' % self.facing)
        print('Move Buffer (beg. of turn: %s' % (self.moveBuffer) )
        # Moves in the moveBuffer have top priority
        if len(self.moveBuffer) != 0:
            return self.moveBuffer.pop(0)

        # Always grab the gold if found
        if glitter:
            self.goHome(True)
            return Agent.Action.GRAB

        (curX, curY) = self.currentSq 

        if bump:
            # revert currentSq pointer to previous square
            self.currentSq = self.pathHistory[-1]
            if self.facing == 'right':
                self.xDim = self.currentSq[0]
                print('xDim Found!: %d' % self.xDim)
            elif self.facing == 'up':
                self.atTopEdge = True
                self.yDim = self.currentSq[1]
                print('yDim Found!: %d' % self.yDim)

            # self.goHome(climb = True)
            if len(self.exploreFrontier) == 0:
                self.goHome(climb = True)
            else:
                self.goToSquare(self.exploreFrontier.pop())

            return self.moveBuffer.pop(0)
        else:
            # If a stench or breeze is perceived, mark the squares.
            if stench:
                self.stenchMat[curX-1][curY-1] = True
                self.handleDanger(danger = 'stench')
                return self.moveBuffer.pop(0)
            elif breeze:
                self.breezeMat[curX-1][curY-1] = True
                self.handleDanger(danger = 'breeze')
                return self.moveBuffer.pop(0)
            else: 
                # append current square to pathHistory
                self.pathHistory.append(self.currentSq)

                ####### update frontier ######
                self.addNeighborsToFrontier()

                # Get next destination
                if len(self.exploreFrontier) == 0:
                    self.goHome(climb = True)
                    return self.moveBuffer.pop(0)
                else:
                    nextSq = self.exploreFrontier.pop()
                    self.goToSquare(nextSq)
                    # update AI's current location
                    self.currentSq = nextSq
                    return self.moveBuffer.pop(0)

        return Agent.Action.CLIMB
        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================
    
    # ======================================================================
    # YOUR CODE BEGINS
    # ======================================================================
    # def takeMoveFromBuffer(self, move):
    #     if move ==

    def goToSquare(self, dest):
        (curX, curY) = self.currentSq

        # DEBUGGING
        self.headingToSquare = dest

        # Backtrack to a square that is adjacent to the destination
        while not self.isAdjacent(dest):
            self.moveOneSq(self.pathHistory.pop(0))

        # make the move to the destination
        self.moveOneSq(dest)

        print('Move Buffer (inside goTo()): %s\n' % (self.moveBuffer))

    # Check that dest is adjacent to current square 
    def isAdjacent(self, dest):
        (curX, curY) = self.currentSq
        (destX, destY) = dest
        print("currentSq: %s destSq %s" % ((self.currentSq, ), (dest, )))
        return (abs(destX - curX) + abs(destY - curY)) == 1

    def addNeighborsToFrontier(self):
        (curX, curY) = self.currentSq

        ### Modify - for now, only add the forward the left neighbors to frontier ###
        if curY != self.yDim:
            nextSq = (curX, curY + 1)
            if nextSq not in self.pathHistory and nextSq not in self.exploreFrontier:
                self.exploreFrontier.append(nextSq)
                print('Adding %s to frontier' % (nextSq, ))
        if curX != self.xDim:
            nextSq = (curX + 1, curY)
            if nextSq not in self.pathHistory and nextSq not in self.exploreFrontier:
                self.exploreFrontier.append(nextSq)
                print('Adding %s to frontier' % (nextSq, ))

        print('Frontier: %s\n' % self.exploreFrontier)

    def handleDanger(self, danger):
        ### For now, naively go home ###
        self.goHome(climb = True)


    # This function constructs a path from the current square to (1,1)
    def goHome(self, climb):
        print('Heading Home (inside goHome)!\n')
        print('Path History (inside goHome): \n')
        print(self.pathHistory)
        # Construct path to go back to (1,1)
        while len(self.pathHistory) != 0:
            self.moveOneSq(self.pathHistory.pop())

        if climb:
            self.moveBuffer.append(Agent.Action.CLIMB)

        print('Move Buffer (inside goHome()): %s\n' % (self.moveBuffer))
    
    # This function makes a move to an adjacent square. It handles orienting
    # the agent in the right direction and moves the agent to the destination 
    # square
    def moveOneSq(self, dest):

        # do nothing
        if dest == self.currentSq:
            return

        (curX, curY) = self.currentSq
        (destX, destY) = dest

        (dx, dy) = (destX - curX, destY - curY)
        print('(insdie moveOneSq()) dest: %s curSq: %s' % ((dest, ), (self.currentSq, )))
        print('(dx, dy) is %d, %d and agent is facing: %s' % (dx, dy, self.facing))
        # Want to move horizontally        
        if dx != 0:
            # want to go left
            if dx < 0 and self.facing != 'left':
                if self.facing == 'right':
                    # Make a u-turn
                    self.makeUTurn() 
                elif self.facing == 'up':
                    self.moveBuffer.append(Agent.Action.TURN_LEFT)
                elif self.facing == 'down':
                    self.moveBuffer.append(Agent.Action.TURN_RIGHT)
                self.facing = 'left'
            # want to go right (dx > 0)
            elif dx > 0 and self.facing != 'right':
                if self.facing == 'left':
                    # Make a u-turn
                    self.makeUTurn() 
                elif self.facing == 'up':
                    self.moveBuffer.append(Agent.Action.TURN_RIGHT)
                elif self.facing =='down':
                    self.moveBuffer.append(Agent.Action.TURN_LEFT)
                self.facing = 'right'
        # want to move vertically
        elif dy != 0:
            # want to move up
            if dy > 0 and self.facing != 'up':
                if self.facing == 'down':
                    # Make a u-turn
                    self.makeUTurn() 
                elif self.facing == 'left':
                    self.moveBuffer.append(Agent.Action.TURN_RIGHT)
                elif self.facing == 'right':
                    self.moveBuffer.append(Agent.Action.TURN_LEFT)
                self.facing = 'up'
            # want to move down
            if dy < 0 and self.facing != 'down':
                if self.facing == 'up':
                    # Make a u-turn
                    self.makeUTurn() 
                elif self.facing == 'left':
                    self.moveBuffer.append(Agent.Action.TURN_LEFT)
                elif self.facing =='right':
                    self.moveBuffer.append(Agent.Action.TURN_RIGHT)
                self.facing = 'down'

        # move forward
        self.moveBuffer.append(Agent.Action.FORWARD)

        # update current square
        self.currentSq = dest

    def makeUTurn(self):
        self.moveBuffer.append(Agent.Action.TURN_LEFT)
        self.moveBuffer.append(Agent.Action.TURN_LEFT)
    
    # ======================================================================
    # YOUR CODE ENDS
    # ======================================================================