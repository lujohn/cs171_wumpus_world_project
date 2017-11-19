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
        self.wumpusDead = False
        self.headingHome = False
        self.haveArrow = True
        self.currentSq = (1,1)
        self.prevPercept = []

        self.facing = 'right'
        # Keep track of world dimension (from "bumps")
        self.xDim = -1
        self.yDim = -1

        # Buffers the immediate next moves to take. These have 
        # top priority.
        self.moveBuffer = list()

        # Stores the path taken from (1,1) to current node. 
        # Treat as LIFO stack
        self.pathHistory = list()

        # Matricies are all 10 x 10 grid with entries initialized to False
        self.breezeMat = [[False for x in range(10)] for y in range(10)]
        self.stenchMat = [[False for x in range(10)] for y in range(10)]
        # self.safeMat = [[False for x in range(10)] for y in range(10)]

        # Exploration Frontier (LIFO structure)
        self.exploreFrontier = []

        # Tracks the squares that have been visited (stores (x,y) tuples)
        self.exploredSquares = []

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
        print('Explored: (beg. of turn: %s' % self.exploredSquares)
        print('Path History: (beg. of turn: %s' % self.pathHistory)
        print('Frontier (beg. of turn: %s' % self.exploreFrontier)
        # Moves in the moveBuffer have top priority
        if len(self.moveBuffer) != 0:
            return self.moveBuffer.pop(0)

        # Always grab the gold if found
        if glitter:
            self.goHome(True)
            return Agent.Action.GRAB

        if scream:
            self.wumpusDead = True
            print('Wumpus is Dead!')


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
                self.goToSquare(self.popFrontier())

            return self.moveBuffer.pop(0)
        else:
            dangers = []
            # If a stench or breeze is perceived, mark the squares.
            if stench and not self.wumpusDead:
                self.stenchMat[curX-1][curY-1] = True
                dangers.append('stench')
            
            if breeze:
                self.breezeMat[curX-1][curY-1] = True
                dangers.append('breeze')

            if len(dangers) != 0:
                self.handleDanger(dangers)
                return self.moveBuffer.pop(0)
            
            # ------------- No Dangers Present -------------
            # append current square to pathHistory
            self.pathHistory.append(self.currentSq)

            ####### update frontier ######
            self.addNeighborsToFrontier()

            # Get next destination
            if len(self.exploreFrontier) == 0:
                self.goHome(climb = True)
                return self.moveBuffer.pop(0)
            else:
                nextSq = self.popFrontier()
                self.goToSquare(nextSq)
                # update AI's current location
                self.currentSq = nextSq
                return self.moveBuffer.pop(0)


        # ##### should never reach here ####
        return Agent.Action.CLIMB
        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================
    
    # ======================================================================
    # YOUR CODE BEGINS
    # ======================================================================
    def handleDanger(self, dangers):
        ## Implement EVALUATE DANGER ##

        #### For now, do not handle both cases
        if 'breeze' in dangers and 'stench' in dangers:
            nextSq = self.popFrontier()
            if not nextSq:
                self.goHome(climb = True)
            else:
                self.goToSquare(nextSq)  
            return        

        # Note: stench will be in dangers list only if wumpus is not dead
        ### Naively shoot the arrow forward.
        if 'stench' in dangers:
            if self.haveArrow:
                self.moveBuffer.append(Agent.Action.SHOOT)
                self.haveArrow = False
                return
            else:
                nextSq = self.popFrontier()
                if not nextSq:
                    self.goHome(climb = True)
                else:
                    self.goToSquare(nextSq)


        if 'breeze' in dangers:
            nextSq = self.popFrontier()
            if not nextSq:
                self.goHome(climb = True)
            else:
                self.goToSquare(nextSq)


    def popFrontier(self):
        if len(self.exploreFrontier) == 0:
            return None

        nextSq = self.exploreFrontier.pop()
        print('Popped %s from frontier\n' % (nextSq, ))
        return nextSq

    # def takeMoveFromBuffer(self, move):
    #     if move ==

    def goToSquare(self, dest):

        if self.currentSq == dest:
            return 

        # Backtrack to a square that is adjacent to the destination
        while not self.isAdjacent(dest):
            prevNode = self.pathHistory.pop()
            self.moveOneSq(prevNode)

        self.pathHistory.append(self.currentSq)

        # make the move to the destination
        self.moveOneSq(dest)

        print('Move Buffer (inside goTo()): %s\n' % (self.moveBuffer))

    # Check that dest is adjacent to current square 
    def isAdjacent(self, dest):
        (curX, curY) = self.currentSq
        (destX, destY) = dest
        return (abs(destX - curX) + abs(destY - curY)) == 1

    def addNeighborsToFrontier(self):
        (curX, curY) = self.currentSq

        ### Modify - for now, only add the forward the left neighbors to frontier ###
        if curY != self.yDim:
            nextSq = (curX, curY + 1)
            if nextSq not in self.exploredSquares and nextSq not in self.exploreFrontier:
                self.exploreFrontier.append(nextSq)
                print('Adding %s to frontier' % (nextSq, ))
        if curX != self.xDim:
            nextSq = (curX + 1, curY)
            if nextSq not in self.exploredSquares and nextSq not in self.exploreFrontier:
                self.exploreFrontier.append(nextSq)
                print('Adding %s to frontier' % (nextSq, ))

        print('Frontier: %s\n' % self.exploreFrontier)


    # This function constructs a path from the current square to (1,1)
    def goHome(self, climb):
        print('Heading Home (inside goHome)!\n')
        print(self.pathHistory)
        # Construct path to go back to (1,1)
        # while len(self.pathHistory) != 0:
        #     self.moveOneSq(self.pathHistory.pop())
        self.goToSquare((1,1))

        if climb:
            self.moveBuffer.append(Agent.Action.CLIMB)
    
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
        print('dest: %s curSq: %s (inside moveOneSq()) ' % ((dest, ), (self.currentSq, )))
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

        # Mark current square as explored
        if self.currentSq not in self.exploredSquares:
            self.exploredSquares.append(self.currentSq)

        # update current square to destination square
        self.currentSq = dest

    def makeUTurn(self):
        self.moveBuffer.append(Agent.Action.TURN_LEFT)
        self.moveBuffer.append(Agent.Action.TURN_LEFT)
    
    # ======================================================================
    # YOUR CODE ENDS
    # ======================================================================