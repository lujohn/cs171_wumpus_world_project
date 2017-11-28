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

## IMPORTANT NOTES / To Dos:
# To Do: Break ties when popping next frontier node by direction agent is facing
# To Do: Once Wumpus location is deteremined, update the reachable/safe matrix
# Also update the frontier - add the reachable nodes into frontier. Must first determine
# if node is reachable.


# Call inferPitSquares every time agent explores a new square!

# Shoot arrow if stench is in (1,1) and no breeze. Not much to lose.
# Kill Wumpus if Wumpus found in first n moves.
# Gamble with pits

# One More PIT inference. 
# Using both "no breeze" spots and known breeze spots. See bigWorld2.txt
# Also look at bigWorld3.txt
# KEEP PITS DETECTED VS BREEZES FOUND VS SAFE SQUARES SEPARATE!
    # For each square visited...be sure to not only mark it as "safe" but also
    # that it has no breeze!!!!!

# Use your prob skills.

# pit detection when user is on border needs fixing


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
        self.breezeMat = [['unknown' for x in range(12)] for y in range(12)]
        self.pitMat = [['unknown' for x in range(12)] for y in range(12)]
        # self.stenchMat = [[False for x in range(10)] for y in range(10)]
        self.stenchSq = []
        self.safeSq = []

        # Exploration Frontier (LIFO structure)
        self.exploreFrontier = []
        # self.exploredFrontierPQ = queue.PriorityQueue()

        # Tracks the squares that have been visited (stores (x,y) tuples)
        self.exploredSquares = [(1,1)]
        self.safeSquares = [ [False  for j in range(12)] for i in range(12)]

        ###  -------- Debugging --------- ###
        self.pitsFound = []
        self.headingToSquare = ()

        # WumpusMode decreases score by ~25
        self.wumpusMode = True
        self.pitMode = True

        self.prevAction = ''

        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================

    def getAction( self, stench, breeze, glitter, bump, scream ):
        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================
        #print('Explored: (beg. of turn: %s' % self.exploredSquares)
        #print('Path History: (beg. of turn: %s' % self.pathHistory)
        print('Explore Frontier (beg. of turn: %s' % self.exploreFrontier)
        #print('Wumpus at: %s found from: %s' % (self.wumpusLocation, self.wumpusFoundFrom) )
        print("World Dim: %d x %d" % (self.xDim, self.yDim))
        # Moves in the moveBuffer have top priority
        print('pits found: %s' % self.pitsFound)

        (curX, curY) = self.currentSq 
        self.safeSquares[curX][curY] = True
        # ---------------------------- Special Cases -------------------------------
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

        # If there is a stench at the start square and no breeze, just shoot the arrow
        # (On Avg, decreasing score by 5 to 10 points)
        if stench and not breeze and self.currentSq == (1,1) and self.haveArrow:
            self.stenchSq.append((1,1))
            self.haveArrow = False
            self.prevAction = 'shoot'
            return Agent.Action.SHOOT

        if self.prevAction == 'shoot':
            self.prevAction = ''
            if scream:
                self.wumpusDead = True
                print('Wumpus is Dead!')
                # Append the square that wumpus was on to frontier
            else:
                # You know that the block right in front is NOT a wumpus
                if self.facing == 'up':
                    self.safeSquares[curX][curY+1] = True
                if self.facing == 'down':
                    self.safeSquares[curX][curY-1] = True
                if self.facing == 'left':
                    self.safeSquares[curX-1][curY] = True
                if self.facing == 'right':
                    self.safeSquares[curX+1][curY] = True
                self.addNeighborsToFrontier()
                self.nextMove()
            self.addNeighborsToFrontier()
            self.nextMove()
            return self.moveBuffer.pop(0)

        # -------------------------- End Special Cases -----------------------------
        if bump:
            # revert currentSq pointer to previous square
            print('bumped')
            print('facing %s' % self.facing)
            self.currentSq = self.prevSq
            if self.facing == 'right':
                self.xDim = self.currentSq[0]
                print('xDim Found!: %d' % self.xDim)

                # update which squares are reachable
                for i in range(len(self.safeSquares)):
                    self.safeSquares[self.xDim+1][i] = False

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
                for j in range(len(self.safeSquares[0])):
                    self.safeSquares[j][self.yDim+1] = False

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
        # -------------- Stench or Breeze Perceived -------------
        else:
            dangers = []
            # If a stench or breeze is perceived, mark the squares.
            if stench and not self.wumpusDead:
                #self.stenchMat[curX-1][curY-1] = True
                if self.currentSq not in self.stenchSq:
                    self.stenchSq.append(self.currentSq)
                dangers.append('stench')
            
            if breeze:
                dangers.append('breeze')
                self.breezeMat[curX][curY] = True
            else:
                self.breezeMat[curX][curY] = False
            print('breezeMat[%d][%d] has breeze: %s ' % (curX, curY, self.breezeMat[curX][curY]))

            if len(dangers) != 0:
                self.handleDanger(dangers)
                return self.moveBuffer.pop(0)
            
            # ----------------- No Dangers Perceived ---------------------
            # self.inferPitSquares()

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
    # This function determines the actions to take when a stench and/or 
    # breeze is perceive.
    def handleDanger(self, dangers):

        curX, curY = self.currentSq
        noDanger = []
        # If both breeze and stench perceived...be careful
        if 'breeze' in dangers and 'stench' in dangers:
            noWumpusNeighbors = self.getNoWumpusNeighbors(self.currentSq)
            if len(noWumpusNeighbors) != 0:
                noPitNeighbors = self.getNoPitNeighbors(self.currentSq)
                if len(noPitNeighbors) != 0:
                    noDanger.extend(list(set(noPitNeighbors).intersection(set(noWumpusNeighbors))))
                    print('Stench and Wumpus!...but these are safe! %s' % noDanger)

        elif 'breeze' in dangers and self.pitMode:
            # If a next breeze square is found, run algorithm to determine pit
            # locations.
            noPitNeighbors = self.getNoPitNeighbors(self.currentSq)
            noDanger.extend(noPitNeighbors)

            print('noDanger (after processing breeze): %s' % noDanger)

        elif 'stench' in dangers and not self.wumpusDead and self.wumpusMode:
            noWumpusNeighbors = self.getNoWumpusNeighbors(self.currentSq)
            noDanger.extend(noWumpusNeighbors)

        print('noDanger (after processing breeze and wumpus): %s' % noDanger)
        dangerousNeighbors = list(set(self.getAllNeighbors(self.currentSq, exclude = noDanger)))
        print("dangerousNeighbors: %s" %  list(set(self.getAllNeighbors(self.currentSq, exclude = noDanger))))
        
        self.addNeighborsToFrontier(exclude = dangerousNeighbors)
        self.nextMove()
        return
  
        ### Logic to Kill Wumpus. For now, ONLY avoid wumpus. Do NOT kill ###

    def getNoWumpusNeighbors(self, sq):
        self.updateWumpusInformation()

        ret = []
        if self.wumpusLocation != None:
            allNeighbors = self.getAllNeighbors(sq)
            for n in allNeighbors:
                if n != self.wumpusLocation:
                    ret.append(n)

        return ret

    def updateWumpusInformation(self):
        # if wumpus location already known, don't do anything
        if self.wumpusLocation != None:
            return
        else:
            self.wumpusLocation = self.findWumpusSquare()

    def getNoPitNeighbors(self, sq):
        # For good measure, call updatePitInformation
        self.updatePitInformation(sq)
        ret = []

        allNeighbors = self.getAllNeighbors(sq)
        for n in allNeighbors:
            x, y = n
            if self.pitMat[x][y] == False:
                ret.append(n)

        print('These neighbors of %s have no pit: %s' % (ret, sq))
        return ret


    # Updates safety information related to pits. 'Sq' here is a sq that is
    # newly discovered to be safe (either from exploring it or from inference)
    def updatePitInformation(self, sq):
        allNeighbors = self.getAllNeighbors(sq)
        safeNeighbors = self.generateSafeNeighbors(sq)

        # Do not process neighbors that are already known to be safe.
        unsafeNeighbors = list(set(allNeighbors) - set(safeNeighbors))

        # Process each unsafe neighbor
        for neighbor in unsafeNeighbors:
            x, y = neighbor
            if self.isPit(neighbor):
                print('pit found at: %s' % (neighbor, ))
                self.pitMat[x][y] = True
                self.safeSquares[x][y] = False

                # Debugging
                self.pitsFound.append(neighbor)

            elif self.isNotPit(neighbor):
                self.pitMat[x][y] = False
                self.safeSquares[x][y] = True  ## To Impl: Note that this could propogate forward.

                print("Added an square adj to breeze! --- %s" % ((x,y),))

    # This function returns all neighbors of 'sq' that are not breezy. 'Unknown'
    # neighbors are not returned.
    def getNoBreezeNeighbors(self, sq):
        allNeighbors = self.getAllNeighbors(sq)
        ret = []

        for n in allNeighbors:
            if self.breezeMat[n[0]][n[1]] == False:
                ret.append(n)

        return ret

    # This function takes as input a square (unexplored) and determines if it IS a pit
    # Assumptions: 
    #   1) currentSq has a breeze
    #   2) sq is a neighbor of currentSq   
    def isPit(self, sq):
        # Check: Can deduce if sq IS a pit if all but one neighbor is marked safe.
        x, y = sq

        print('Asserting that sq is not explored')
        assert (x, y) not in self.exploredSquares
        print('Assertion Passed')

        allNeighbors = self.getAllNeighbors(self.currentSq)
        for neighbor in allNeighbors:
            if neighbor != sq:
                nx, ny = neighbor
                if not self.safeSquares[nx][ny]:
                    return False
        return True

    # This function takes as input a square (unexplored) and determines if it is NOT a pit
    def isNotPit(self, sq):
        x, y = sq

        print('Asserting that sq is not explored (isNotPit)')
        assert (x, y) not in self.exploredSquares
        print('Assertion Passed')

        allNeighbors = self.getAllNeighbors(sq)

        # Check1: all neighbors of sq are breezy
        for (x,y) in allNeighbors:
            if self.breezeMat[x][y] == False:
                # one of the bordering squares is not breezy => not a pit.
                return True
        
        return False

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
            reachableNeighbors = self.generateSafeNeighbors(u)
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

    def addNeighborsToFrontier(self, exclude = []):
        (x, y) = self.currentSq

        up = (x, y + 1)
        down = (x, y - 1)
        left = (x - 1, y)
        right = (x + 1, y)
        
        if y != self.yDim:
            if up not in exclude:
                if up not in self.exploredSquares and up not in self.exploreFrontier:
                    self.exploreFrontier.append(up)
                    print('Adding %s to frontier' % (up, ))
                self.safeSquares[x][y+1] = True
        if y > 1: 
            if down not in exclude:
                if down not in self.exploredSquares and down not in self.exploreFrontier:
                    self.exploreFrontier.append(down)
                    print('Adding %s to frontier' % (down, ))
                self.safeSquares[x][y-1] = True
        if x != self.xDim:
            if right not in exclude:
                if right not in self.exploredSquares and right not in self.exploreFrontier:
                    self.exploreFrontier.append(right)
                    print('Adding %s to frontier' % (right, ))
                self.safeSquares[x+1][y] = True
        if x > 1:
            if left not in exclude:
                if left not in self.exploredSquares and left not in self.exploreFrontier:
                    self.exploreFrontier.append(left)
                    print('Adding %s to frontier' % (left, ))
                self.safeSquares[x-1][y] = True
        print('Frontier: %s\n' % self.exploreFrontier)

      
    # This function takes a square and generates returns the list of squares
    # that border it and are reachable
    def generateSafeNeighbors(self, sq):
        x, y = sq
        S = []
        up = (x, y + 1)
        down = (x, y - 1)
        left = (x - 1, y)
        right = (x + 1, y)

        if self.safeSquares[x][y+1]:
            S.append(up)
        if self.safeSquares[x][y-1]:
            S.append(down)
        if self.safeSquares[x-1][y]:
            S.append(left)
        if self.safeSquares[x+1][y]:
            S.append(right)

        return S

    def getAllNeighbors(self, sq, exclude = []):
        x, y = sq
        up = (x, y + 1)
        down = (x, y - 1)
        left = (x - 1, y)
        right = (x + 1, y)

        return list(set([up, down, left, right]) - set(exclude))

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
    # from the current node. Note: cost heuristic should take into account
    # the direction agent is facing.
    # Assumptions: frontier is nonempty
    # def minCostode(self):
    #     minCost = self.manhattanDist(self.currentSq, self.exploreFrontier[0])
    #     minNode = 0
    #     i = 1
    #     while i < len(self.exploreFrontier):
    #         t = self.manhattanDist(self.currentSq, self.exploreFrontier[i])
    #         if t < minCost:
    #             minCost = t
    #             minNode = i
    #         i = i + 1

    #     return self.exploreFrontier.pop(minNode)

    def minCostode(self):
        print('hi')
        minCost = self.costHeuristic(self.exploreFrontier[0])
        minNode = 0
        i = 1
        while i < len(self.exploreFrontier):
            t = self.costHeuristic(self.exploreFrontier[i])
            if t < minCost:
                minCost = t
                minNode = i
            i = i + 1

        return self.exploreFrontier.pop(minNode)

    def costHeuristic(self, sq):
        dx, dy = (sq[0] - self.currentSq[0], sq[1] - self.currentSq[1])
        cost = 0
        if dx < 0:
            if self.facing == 'right':
                cost += 2
            elif self.facing == 'up' or self.facing == 'down':
                cost += 1
        if dx > 0:
            if self.facing == 'left':
                cost += 2
            elif self.facing == 'up' or self.facing == 'down':
                cost += 1 
        if dy < 0:
            if self.facing == 'up':
                cost += 2
            elif self.facing == 'left' or self.facing == 'right':
                cost += 1
        if dy > 0:
            if self.facing == 'down':
                cost += 2
            elif self.facing == 'left' or self.facing == 'right':
                cost += 1

        cost += self.manhattanDist(self.currentSq, sq)
        return cost

    # This function calculates the manhattan distance between two squares.
    def manhattanDist(self, sq1, sq2):
        return (abs(sq1[0] - sq2[0]) + abs(sq1[1] - sq2[1]))

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