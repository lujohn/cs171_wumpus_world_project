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
        self.facing = 'right'
        self.currentSq = (1,1)
        self.bumpedWall = False
        self.prevPercept = []

        self.moveBuffer = queue.Queue()
        self.pathHistory = queue.Queue()

        # Matricies are all 10 x 10 grid with entries initialized to False
        self.breezeMat = [[False for x in range(10)] for y in range(10)]
        self.stenchMat = [[False for x in range(10)] for y in range(10)]
        self.safeMat = [[False for x in range(10)] for y in range(10)]

        # Exploration Frontier
        self.exploreQ = []

        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================

    def getAction( self, stench, breeze, glitter, bump, scream ):
        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================

        # Moves in the moveBuffer have top priority
        if not self.moveBuffer.empty():
            return self.moveBuffer.get()

        # Always grab the gold if found
        if glitter:
            self.goHome(True)
            return Agent.Action.GRAB

        (curX, curY) = self.currentSq 
        # If a stench or breeze is perceived, mark the squares.
        # FOR NOW, go back one square.
        if stench:
            self.stenchMat[curX][curY] = True
            self.goHome(climb = False)

            return self.moveBuffer.get()

        if breeze:
            self.breezeMat[curX][curY] = True
            self.goHome(climb = False)

            return self.moveBuffer.get()

        if bump:
            self.goHome(climb = True)
            return self.moveBuffer.get()
        else:
            # keep moving forward until a bump is perceived
            nextSq = None
            if self.facing == 'right': 
                nextSq = (curX + 1, curY)
            elif self.facing == 'left':
                nextSq = (curX - 1, curY)
            elif self.facing == 'up':
                nextSq = (curX, curY + 1)
            elif self.facing == 'down':
                nextSq = (curX, curY - 1)

            # append pathHistory
            self.pathHistory.put(self.currentSq)

            self.currentSq = nextSq
            return Agent.Action.FORWARD


        return Agent.Action.CLIMB
        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================
    
    # ======================================================================
    # YOUR CODE BEGINS
    # ======================================================================
    
    # This function constructs a path from the current square to (1,1)
    def goHome(self, climb):
        # Construct path to go back to (1,1)
        while not self.pathHistory.empty():
            self.moveOneSq(self.pathHistory.get())

        if climb:
            self.moveBuffer.put(Agent.Action.CLIMB)


    # This function makes a move to an adjacent square. It handles orienting
    # the agent in the right direction and moves the agent to the destination 
    # square
    def moveOneSq(self, dest):
        (curX, curY) = self.currentSq
        (destX, destY) = dest

        (dx, dy) = (destX - curX, destY - curY)

        # Want to move horizontally        
        if dx != 0:
            # want to go left
            if dx < 0 and self.facing != 'left':
                if self.facing == 'right':
                    # Make a u-turn
                    self.makeUTurn() 
                elif self.facing == 'up':
                    self.moveBuffer.put(Agent.Action.TURN_LEFT)
                elif self.facing == 'down':
                    self.moveBuffer.put(Agent.Action.TURN_RIGHT)
                self.facing = 'left'
            # want to go right (dx > 0)
            elif dx > 0 and self.facing != 'right':
                if self.facing == 'left':
                    # Make a u-turn
                    self.makeUTurn() 
                elif self.facing == 'up':
                    self.moveBuffer.put(Agent.Action.TURN_RIGHT)
                elif self.facing =='down':
                    self.moveBuffer.put(Agent.Action.TURN_LEFT)
                self.facing = 'right'
        # want to move vertically
        elif dy != 0:
            # want to move up
            if dy > 0 and self.facing != 'up':
                if self.facing == 'down':
                    # Make a u-turn
                    self.makeUTurn() 
                elif self.facing == 'left':
                    self.moveBuffer.put(Agent.Action.TURN_RIGHT)
                elif self.facing == 'right':
                    self.moveBuffer.put(Agent.Action.TURN_LEFT)
                self.facing = 'up'
            # want to move down
            if dy < 0 and self.facing != 'down':
                if self.facing == 'up':
                    # Make a u-turn
                    self.makeUTurn() 
                elif self.facing == 'left':
                    self.moveBuffer.put(Agent.Action.TURN_LEFT)
                elif self.facing =='right':
                    self.moveBuffer.put(Agent.Action.TURN_RIGHT)
                self.facing == 'down'

        # move forward
        self.moveBuffer.put(Agent.Action.FORWARD)

    def makeUTurn(self):
        self.moveBuffer.put(Agent.Action.TURN_LEFT)
        self.moveBuffer.put(Agent.Action.TURN_LEFT)
    
    # ======================================================================
    # YOUR CODE ENDS
    # ======================================================================