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

## IMPORTANT NOTES:
# - for pathTo, store nodes explicity and then do one move at a time
#   This allows for adjusting for bump while on a path (so you won't go out of bounds)
# - pop Frontier according to nodes that are closest manhattan
# Nodes are added to frontier multiple times.
# 

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
        self.prevSq = None

        # Matricies are all 10 x 10 grid with entries initialized to False
        # self.breezeMat = [[False for x in range(10)] for y in range(10)]
        # self.stenchMat = [[False for x in range(10)] for y in range(10)]
        # self.safeMat = [[False for x in range(10)] for y in range(10)]
        self.breezeSq = []
        self.stenchSq = []
        self.safeSq = []

        # Exploration Frontier (LIFO structure)
        self.exploreFrontier = []
        # self.exploredFrontierPQ = queue.PriorityQueue()

        # Tracks the squares that have been visited (stores (x,y) tuples)
        self.exploredSquares = []
        self.reachable = [ [False  for j in range(12)] for i in range(12)]

        ###  -------- Debugging --------- ###
        self.headingToSquare = ()

        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================

    def getAction( self, stench, breeze, glitter, bump, scream ):
        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================
        #print('Explored: (beg. of turn: %s' % self.exploredSquares)
        #print('Path History: (beg. of turn: %s' % self.pathHistory)
        print('Frontier (beg. of turn: %s' % self.exploreFrontier)
        #print('Wumpus at: %s found from: %s' % (self.wumpusLocation, self.wumpusFoundFrom) )
        print("World Dim: %d x %d" % (self.xDim, self.yDim))
        # Moves in the moveBuffer have top priority
        if len(self.moveBuffer) != 0:
            # If bump is perceived clear moveBuffer and go to next node in frontier.
            # This could occur, for instance, when a path is calculated but the dimensions
            # of the world is still yet unknown.
            if bump:
                self.moveBuffer.clear()
                self.nextMove()

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


        (curX, curY) = self.currentSq 
        if bump:
            # revert currentSq pointer to previous square
            print('bumped')
            print('facing %s' % self.facing)
            self.currentSq = self.prevSq
            if self.facing == 'right':
                self.xDim = self.currentSq[0]
                print('xDim Found!: %d' % self.xDim)

                # update which squares are reachable
                for i in range(len(self.reachable)):
                    self.reachable[self.xDim+1][i] = False

                # remove squares in frontier that have x > x dimension
                i = 0
                while i != len(self.exploreFrontier):
                    x, _ = self.exploreFrontier[i]
                    if x > self.xDim:
                        print("removed from frontier: %s" % (self.exploreFrontier.pop(i),))
                    else:
                        i = i + 1
            # Bump top border
            elif self.facing == 'up':
                self.atTopEdge = True
                self.yDim = self.currentSq[1]
                print('yDim Found!: %d' % self.yDim)

                # update which squares are reachable.
                for j in range(len(self.reachable[0])):
                    self.reachable[j][self.yDim+1] = False

                # remove squares in frontier that have y > y dimension
                i = 0
                while i != len(self.exploreFrontier):
                    _, y = self.exploreFrontier[i]
                    if y > self.yDim:
                        print("removed from frontier: %s" % (self.exploreFrontier.pop(i),))
                    else:
                        i = i + 1

            self.nextMove()

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
            self.reachable[curX][curY] = True

            # Mark current square as explored and reachable
            # if self.currentSq not in self.exploredSquares:
            #     self.exploredSquares.append(self.currentSq)

            # append current square to pathHistory
            self.pathHistory.append(self.currentSq)

            ###### update frontier ######
            self.addNeighborsToFrontier()

            # Go to next destination
            self.nextMove()
            
            return self.moveBuffer.pop(0)


        # ##### should never reach here ####
        return Agent.Action.CLIMB
        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================
    
    # ======================================================================
    # YOUR CODE BEGINS
    # ======================================================================
    
    # This function takes pops the next node from the frontier and moves the
    # agent to that node.
    def nextMove(self):
        nextSq = self.popFrontier()
        if not nextSq:
            self.goHome(climb = True)
        else:
            self.goToSquare(nextSq)

    def goToSquare(self, dest):
        print("go to %s" % (dest, ))

        if self.currentSq == dest:
            return 

        if self.isAdjacent(dest):
            self.moveOneSq(dest)
        else:
            # If dest is not safely reachable, do nothing.
            path = self.pathTo(dest)

            # If destination is reachable, go there.
            for p in path[1:]:
                self.moveOneSq(p)

    # This function makes a move to an adjacent square. It handles orienting
    # the agent in the right direction and moves the agent to the destination 
    # square
    def moveOneSq(self, dest):
        
        # If agent is already at the destination, do nothing.
        if dest == self.currentSq:
            return

        x, y = self.currentSq
        
        # Face the destination
        self.faceSquare(dest)

        # move forward
        self.moveBuffer.append(Agent.Action.FORWARD)

        # update current square to destination square
        self.prevSq = self.currentSq
        self.currentSq = dest

    def pathTo(self, dest):
        print("inside pathTo()")

        Q = [self.currentSq]
        parents = {self.currentSq : None}

        u = None
        pathFound = False
        while len(Q) != 0 and not pathFound:
            u = Q.pop(0)
            print("u is: %s" % (u, ))
            reachableNeighbors = self.generateReachableNeighbors(u)
            print("reachable (safe) neighbors: %s" % reachableNeighbors)
            for v in reachableNeighbors:
                if v not in parents:
                    parents[v] = u
                    Q.append(v)
                if v == dest:
                    print("v == dest (shortest path found)")
                    pathFound = True
                    break

        # Construct path
        if not pathFound:
            print("No path found!")
            return None
        else:
            w = dest
            path = []
            while w != self.currentSq:
                path.insert(0, w)
                w = parents[w]
            path.insert(0, self.currentSq)

            print('returning path: %s' % path)
            return path

    def addNeighborsToFrontier(self):
        (x, y) = self.currentSq

        up = (x, y + 1)
        down = (x, y - 1)
        left = (x - 1, y)
        right = (x + 1, y)
        
        if y != self.yDim:
            if up not in self.exploredSquares and up not in self.exploreFrontier:
                self.exploreFrontier.append(up)
                print('Adding %s to frontier' % (up, ))
            self.reachable[x][y+1] = True
        if y > 1:    
            if down not in self.exploredSquares and down not in self.exploreFrontier:
                self.exploreFrontier.append(down)
                print('Adding %s to frontier' % (down, ))
            self.reachable[x][y-1] = True
        if x != self.xDim:
            if right not in self.exploredSquares and right not in self.exploreFrontier:
                self.exploreFrontier.append(right)
                print('Adding %s to frontier' % (right, ))
            self.reachable[x+1][y] = True
        if x > 1:
            if left not in self.exploredSquares and left not in self.exploreFrontier:
                self.exploreFrontier.append(left)
                print('Adding %s to frontier' % (left, ))
            self.reachable[x-1][y] = True
        print('Frontier: %s\n' % self.exploreFrontier)

      
    # This function takes a square and generates returns the list of squares
    # that border it and are reachable
    def generateReachableNeighbors(self, sq):
        x, y = sq
        S = []
        up = (x, y + 1)
        down = (x, y - 1)
        left = (x - 1, y)
        right = (x + 1, y)

        if self.reachable[x][y+1]:
            S.append(up)
        if self.reachable[x][y-1]:
            S.append(down)
        if self.reachable[x-1][y]:
            S.append(left)
        if self.reachable[x+1][y]:
            S.append(right)

        return S


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
            print('Frontier is empty')
            return None


        nextSq = self.minCostode()
        print('Popped %s from frontier\n' % (nextSq, ))

        if nextSq not in self.exploredSquares:
            self.exploredSquares.append(nextSq)
            print('Added %s to explored list!\n' % (nextSq, ))

        return nextSq

    # find the node in the frontier wth the smallest manhattan distance
    # from the current node.
    # Assumptions: frontier is nonempty
    def minCostode(self):
        minCost = self.manhattanDist(self.currentSq, self.exploreFrontier[0])
        minNode = 0
        i = 1
        while i < len(self.exploreFrontier):
            t = self.manhattanDist(self.currentSq, self.exploreFrontier[i])
            if t < minCost:
                minCost = t
                minNode = i
            i = i + 1

        return self.exploreFrontier.pop(minNode)


    def manhattanDist(self, sq1, sq2):
        return (abs(sq1[0] - sq2[0]) + abs(sq1[1] - sq1[1]))

    # Check that dest is adjacent to current square 
    def isAdjacent(self, dest):
        (curX, curY) = self.currentSq
        (destX, destY) = dest
        return (abs(destX - curX) + abs(destY - curY)) == 1


    # This function constructs a path from the current square to (1,1)
    def goHome(self, climb):
        self.goToSquare((1,1))

        if climb:
            self.moveBuffer.append(Agent.Action.CLIMB)

    def makeUTurn(self):
        self.moveBuffer.append(Agent.Action.TURN_LEFT)
        self.moveBuffer.append(Agent.Action.TURN_LEFT)
    
    # ======================================================================
    # YOUR CODE ENDS
    # ======================================================================