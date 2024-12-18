# multi_agents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattan_distance
from game import Directions, Actions
from pacman import GhostRules
import random, util
from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def get_action(self, game_state):
        """
        You do not need to change this method, but you're welcome to.

        get_action chooses among the best options according to the evaluation function.

        Just like in the previous project, get_action takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legal_moves = game_state.get_legal_actions()

        # Choose one of the best actions
        scores = [self.evaluation_function(game_state, action) for action in legal_moves]
        best_score = max(scores)
        best_indices = [index for index in range(len(scores)) if scores[index] == best_score]
        chosen_index = random.choice(best_indices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legal_moves[chosen_index]

    def evaluation_function(self, current_game_state, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (new_food) and Pacman position after moving (new_pos).
        new_scared_times holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successor_game_state = current_game_state.generate_pacman_successor(action)
        last_position = current_game_state.get_pacman_position()
        new_pos = successor_game_state.get_pacman_position()
        new_food = successor_game_state.get_food()
        new_ghost_states = successor_game_state.get_ghost_states()
        new_scared_times = [ghostState.scared_timer for ghostState in new_ghost_states]
        
        "*** YOUR CODE HERE ***"
        # calculate the Manhattan distance to the nearest food
        food_list = new_food.as_list()
        if food_list:
            nearest_food_distance = min(manhattan_distance(new_pos, food) for food in food_list)
        else:
            nearest_food_distance = 0

        # calculate the Manhattan distance to the nearest ghost
        ghost_distances = [manhattan_distance(new_pos, ghost_state.get_position()) for ghost_state in new_ghost_states]
        nearest_ghost_distance = min(ghost_distances) if ghost_distances else float('inf')

        score = successor_game_state.get_score()

        # if ghosts are scared, favor states where Pacman is closer to the ghosts
        scared_ghosts = [ghost_state for ghost_state in new_ghost_states if ghost_state.scared_timer > 0]
        if scared_ghosts:
            # calculate the Manhattan distance to the nearest scared ghost
            nearest_scared_ghost_distance = min(manhattan_distance(new_pos, ghost_state.get_position()) for ghost_state in scared_ghosts)
            score += 200 / (nearest_scared_ghost_distance + 1)

        score += 10 / (nearest_food_distance + 1)
        score -= 10 / (nearest_ghost_distance + 1)

        if last_position == new_pos:
            score -= 100
            
        return score


def score_evaluation_function(current_game_state):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return current_game_state.get_score()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, eval_fn='score_evaluation_function', depth='2'):
        super().__init__()
        self.index = 0 # Pacman is always agent index 0
        self.evaluation_function = util.lookup(eval_fn, globals())
        self.depth = int(depth) 

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """
    
    def get_action(self, game_state):
        """
        Returns the minimax action from the current game_state using self.depth
        and self.evaluation_function.

        Here are some method calls that might be useful when implementing minimax.

        game_state.get_legal_actions(agent_index):
        Returns a list of legal actions for an agent
        agent_index=0 means Pacman, ghosts are >= 1

        game_state.generate_successor(agent_index, action):
        Returns the successor game state after an agent takes an action

        game_state.get_num_agents():
        Returns the total number of agents in the game

        game_state.is_win():
        Returns whether or not the game state is a winning state

        game_state.is_lose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        # pacman's turn (max player)
        best_action = None
        best_value = float('-inf')
        # loop in all legal actions, choose the highest value
        for action in game_state.get_legal_actions(0):
        
            successor_state = game_state.generate_successor(0, action)
            value = self.minimax(1, 0, successor_state) # compute the value of the successor state
            
            # we update the best val and action
            if value > best_value:
                best_value = value
                best_action = action

        return best_action
        
    def minimax(self, agent_index, depth, game_state):
        # check if the game state is a terminal state or if the depth limit has been reached
        if game_state.is_win() or game_state.is_lose() or depth == self.depth:
            return self.evaluation_function(game_state)
        
        # determine who's turn it is
        if agent_index == 0:  # Pacman's turn (maximizing player)
            return self.max_value(agent_index, depth, game_state)
        else:  # Ghosts' turn (minimizing player)
            return self.min_value(agent_index, depth, game_state)


    def max_value(self, agent_index, depth, game_state):
        v = float('-inf')
        # loop in all legal actions, choose the highest value
        for action in game_state.get_legal_actions(agent_index):
            successor_state = game_state.generate_successor(agent_index, action)
            # recursively call minimax for the next agent
            v = max(v, self.minimax(1, depth, successor_state))
        return v

    def min_value(self, agent_index, depth, game_state):
        v = float('inf')
        next_agent = agent_index + 1
        # if all agents have taken their turn, increment the depth
        if next_agent == game_state.get_num_agents():
            next_agent = 0
            depth += 1
            
        # loop in all legal actions, choose the highest value
        for action in game_state.get_legal_actions(agent_index):
            successor_state = game_state.generate_successor(agent_index, action)
            # recursively call minimax for the next agent
            v = min(v, self.minimax(next_agent, depth, successor_state))
        return v
        
    

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def get_action(self, game_state):
        """
        Returns the minimax action using self.depth and self.evaluation_function
        """
        # pacman's turn (max player)
        best_action = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        # loop in all legal actions, choose the highest value
        for action in game_state.get_legal_actions(0):
            successor_state = game_state.generate_successor(0, action)
            value = self.minimax(1, 0, successor_state, alpha, beta)
            # update the best value and action
            if value > best_value:
                best_value = value
                best_action = action
            alpha = max(alpha, best_value)

        return best_action

    def minimax(self, agent_index, depth, game_state, alpha, beta):
        # check if  state is terminal or if depth limit is reached
        if game_state.is_win() or game_state.is_lose() or depth == self.depth:
            return self.evaluation_function(game_state)

        # determine who's turn it is
        if agent_index == 0:  # pacman's turn (max player)
            return self.max_value(agent_index, depth, game_state, alpha, beta)
        else:  # ghosts' turn (min player)
            return self.min_value(agent_index, depth, game_state, alpha, beta)
        
        
    def max_value(self, agent_index, depth, game_state, alpha, beta):
        v = float('-inf')
        # loop in all legal actions, choose the highest value
        for action in game_state.get_legal_actions(agent_index):
            successor_state = game_state.generate_successor(agent_index, action)
            # recursively call minimax 
            v = max(v, self.minimax(1, depth, successor_state, alpha, beta))
            # prune the search tree if v > beta
            if v > beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(self, agent_index, depth, game_state, alpha, beta):
        v = float('inf')
        next_agent = agent_index + 1
        # increment the depth
        if next_agent == game_state.get_num_agents():
            next_agent = 0
            depth += 1
            
        # loop in all legal actions, choose the highest value
        for action in game_state.get_legal_actions(agent_index):
    
            successor_state = game_state.generate_successor(agent_index, action)
            # recursively call minimax 
            v = min(v, self.minimax(next_agent, depth, successor_state, alpha, beta))
            # prune the search tree if  v > beta
            if v < alpha:
                return v
            beta = min(beta, v)
        return v

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def get_action(self, game_state):
        """
        Returns the expectimax action using self.depth and self.evaluation_function

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raise_not_defined()

def better_evaluation_function(current_game_state):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raise_not_defined()
    


# Abbreviation
better = better_evaluation_function
