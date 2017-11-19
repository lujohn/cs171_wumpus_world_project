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

class MyAI ( Agent ):

    def __init__ ( self ):
        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================
        
        # Environment State
        self.firstTurn = True
        self.wumpusKilled = False
        self.grid = [[]]
        
        # Agent State
        self.stepHistory = []
        self.atStartNode = True
        self.headingHome = False
        self.facing = 'Right'
        self.moveBuffer = []


        pass
        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================

    def getAction( self, stench, breeze, glitter, bump, scream ):
        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================
        # Moves in the moveBuffer should have top priority
        if len(self.moveBuffer) != 0:
            return self.moveBuffer.pop()

        # Always grab the gold if found
        if glitter:
            self.headingHome = True
            self.moveBuffer.extend([Agent.Action.TURN_LEFT, Agent.Action.TURN_LEFT])
            return Agent.Action.GRAB

        # If a stench or breeze is perceived, we like to turn around 
        # and go back to start node.
        if stench or breeze:
            if self.atStartNode:
                return Agent.Action.CLIMB
            else:
                # Turn around and head home
                self.headingHome = True
                self.moveBuffer.extend([Agent.Action.FORWARD, Agent.Action.TURN_LEFT])
                return Agent.Action.TURN_LEFT

        if bump:
            if self.headingHome:
                return Agent.Action.CLIMB
            else:
                # Turn Around and Head Home
                self.headingHome = True
                self.moveBuffer.extend([Agent.Action.FORWARD, Agent.Action.TURN_LEFT])
                return Agent.Action.TURN_LEFT
        else:
            # keep moving forward until a bump is perceived
            self.atStartNode = False
            return Agent.Action.FORWARD


        return Agent.Action.CLIMB
        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================
    
    # ======================================================================
    # YOUR CODE BEGINS
    # ======================================================================

    
    # ======================================================================
    # YOUR CODE ENDS
    # ======================================================================