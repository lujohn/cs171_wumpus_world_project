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
        self.wumpusLocation = None
        self.wumpusFoundFrom = None
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
        # self.breezeMat = [[False for x in range(10)] for y in range(10)]
        # self.stenchMat = [[False for x in range(10)] for y in range(10)]
        # self.safeMat = [[False for x in range(10)] for y in range(10)]
        self.breezeSq = []
        self.stenchSq = []
        self.safeSq = []


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
        print('Stench Sq found: %s' % self.stenchSq)
        print('Breeze Sq found: %s' % self.breezeSq)
        print('Explored: (beg. of turn: %s' % self.exploredSquares)
        print('Path History: (beg. of turn: %s' % self.pathHistory)
        print('Frontier (beg. of turn: %s' % self.exploreFrontier)
        print('Wumpus at: %s found from: %s' % (self.wumpusLocation, self.wumpusFoundFrom) )
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
            # Append the square that wumpus was on to frontier
            self.addNeighborsToFrontier()

        # if frontier is empty try killing wumpus
        # if len(self.exploreFrontier) == 0 and self.wumpusLocation != None:
        #     self.killWumpus()
        #     print("KILLLLLLLLLINÑ")
        #     return self.moveBuffer.pop()


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
                #self.stenchMat[curX-1][curY-1] = True
                if self.currentSq not in self.stenchSq:
                    self.stenchSq.append(self.currentSq)
                dangers.append('stench')
            
            if breeze:
                #self.breezeMat[curX-1][curY-1] = True
                if self.currentSq not in self.breezeSq:
                    self.breezeSq.append(self.currentSq)
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
        # Store wumpus location but do not kill until necessary
        if 'stench' in dangers:

            # Find wumpus if not found already
            if self.wumpusLocation == None:
                wumpusSq = self.findWumpusSquare()
                if wumpusSq:
                    self.wumpusLocation = wumpusSq
                    self.wumpusFoundFrom = self.currentSq

            # if wumpus location is still unknown, explore the next item in frontier
            if self.wumpusLocation == None:
                nextSq = self.popFrontier()
                if not nextSq:
                    # If there are no more moves in the frontier, just shoot the arrow
                    self.goHome(climb = True)
                    return
                else:
                    self.goToSquare(nextSq)
           
            # If wumpusLocation is known, decide whether to kill it.
            # If there are other nodes in the frontier, explore those first
            if self.wumpusLocation != None:
                if len(self.exploreFrontier) != 0:
                    # Explore other paths before killing wumpus
                    nextSq = self.popFrontier()
                    self.goToSquare(nextSq)
                    return
                else:
                    # if self.haveArrow:
                    #     self.killWumpus()
                    # else:
                    #     self.goHome(climb = True)
                    self.goHome(climb = True)
                    return

        if 'breeze' in dangers:
            nextSq = self.popFrontier()
            if not nextSq:
                self.goHome(climb = True)
            else:
                self.goToSquare(nextSq)

    # Current Impl does not support this. I cannot go to an arbitrary square yet.
    def killWumpus(self):
        self.goToSquare(self.wumpusFoundFrom)
        self.faceSquare(self.wumpusLocation)
        self.moveBuffer.append(Agent.Action.SHOOT)
        self.haveArrow = False
    
    def faceSquare(self, dest):
        (curX, curY) = self.currentSq
        (destX, destY) = dest

        (dx, dy) = (destX - curX, destY - curY)      
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

    def findWumpusSquare(self):
        x, y = self.currentSq
        # Consult the stench matrix for more information
        wumpusSq = None
        upRight = (x + 1, y + 1)
        downRight = (x + 1, y - 1)
        upLeft = (x - 1, y + 1)
        downLeft = (x - 1, y - 1)
        up = (x, y + 1)
        down = (x, y - 1)
        left = (x - 1, y)
        right = (x + 1, y)
        # Case 1: If there is a stench 2 squares away horizontally or vertically
        # then Wumpus is definitely in between.
        if (x + 2, y) in self.stenchSq:
            wumpusSq = right
        elif (x - 2, y) in self.stenchSq:
            wumpusSq = left
        elif (x, y + 2) in self.stenchSq:
            wumpusSq = up
        elif (x, y - 2) in self.stenchSq:
            wumpusSq = down
        else:
            # Case 2: If an adjacent diagonal has a stench and corresponding
            # adjacent square has been explored 
            if upRight in self.stenchSq:
                if up in self.exploredSquares:
                    wumpusSq = right
                elif right in self.exploredSquares:
                    wumpusSq = up
            elif downRight in self.stenchSq:
                if down in self.exploredSquares:
                    wumpusSq = right
                elif right in self.exploredSquares:
                    wumpusSq = down
            elif upLeft in self.stenchSq:
                if up in self.exploredSquares:
                    wumpusSq = left
                elif left in self.exploredSquares:
                    wumpusSq = up
            elif downLeft in self.stenchSq:
                if down in self.stenchSq:
                    wumpusSq = left
                elif left in self.stenchSq:
                    wumpusSq = down

        return wumpusSq

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


        ## Causing Duplicates?
        if self.currentSq not in self.pathHistory:
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
        (x, y) = self.currentSq

        up = (x, y + 1)
        down = (x, y - 1)
        left = (x - 1, y)
        right = (x + 1, y)
        ### Modify - for now, only add the forward the left neighbors to frontier ###
        if y != self.yDim:
            if up not in self.exploredSquares and up not in self.exploreFrontier:
                self.exploreFrontier.append(up)
                print('Adding %s to frontier' % (up, ))
            if down not in self.exploredSquares and down not in self.exploreFrontier:
                self.exploreFrontier.append(down)
                print('Adding %s to frontier' % (down, ))
        if x != self.xDim:
            if left not in self.exploredSquares and left not in self.exploreFrontier:
                self.exploreFrontier.append(left)
                print('Adding %s to frontier' % (left, ))
            if right not in self.exploredSquares and right not in self.exploreFrontier:
                self.exploreFrontier.append(right)
                print('Adding %s to frontier' % (right, ))
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