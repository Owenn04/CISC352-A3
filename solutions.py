# solutions.py
# ------------
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

'''Implement the methods from the classes in inference.py here'''

import util
from util import raiseNotDefined
from util import manhattanDistance # had to add this to solutions
import random
import busters

def normalize(self):
    """
    Normalize the distribution such that the total value of all keys sums
    to 1. The ratio of values for all keys will remain the same. In the case
    where the total value of the distribution is 0, do nothing.

    >>> dist = DiscreteDistribution()
    >>> dist['a'] = 1
    >>> dist['b'] = 2
    >>> dist['c'] = 2
    >>> dist['d'] = 0
    >>> dist.normalize()
    >>> list(sorted(dist.items()))
    [('a', 0.2), ('b', 0.4), ('c', 0.4), ('d', 0.0)]
    >>> dist['e'] = 4
    >>> list(sorted(dist.items()))
    [('a', 0.2), ('b', 0.4), ('c', 0.4), ('d', 0.0), ('e', 4)]
    >>> empty = DiscreteDistribution()
    >>> empty.normalize()
    >>> empty
    {}
    """
    total = self.total() # calculate the sum of all values in the distribution. this represents the total 'weight' of the distribution before normalization

    if total == 0: # if the total is 0, it means the distribution is either empty or all values are zero, so do nothing as normalization isnt possible
        return
    
    for key in self.keys(): # if the total isnt 0, iterate through each key-value pair in the distribution and for each value divide it by its total effectively scaling all values so they sum to 1 / normalizing it. 
        self[key] = self[key] / total

    # raiseNotDefined()
def sample(self):
    """
    Draw a random sample from the distribution and return the key, weighted
    by the values associated with each key.

    >>> dist = DiscreteDistribution()
    >>> dist['a'] = 1
    >>> dist['b'] = 2
    >>> dist['c'] = 2
    >>> dist['d'] = 0
    >>> N = 100000.0
    >>> samples = [dist.sample() for _ in range(int(N))]
    >>> round(samples.count('a') * 1.0/N, 1)  # proportion of 'a'
    0.2
    >>> round(samples.count('b') * 1.0/N, 1)
    0.4
    >>> round(samples.count('c') * 1.0/N, 1)
    0.4
    >>> round(samples.count('d') * 1.0/N, 1)
    0.0
    """
    "*** YOUR CODE HERE ***"
    # if the distribution is empty, return None as there is nothing to sample. 
    if not self:
        return None
    
    total = self.total()

    # if all values are 0, return None as sampling is useless.
    if total == 0:
        return None
    
    rand_num = random.random() * total # generate a random fpoint number between 0 and total sum. this number will be used to select a key

    cumulative = 0.0
    for key, value in self.items(): # iterate through each key-value pair in the distribution and add the currentvalue to the culmatative probability.
        cumulative += value
        if rand_num <= cumulative: # if the random number is less than or equal to the cumulative probability, return the current key
            return key # this ensures that keys with higher probabilities have a higher chance of being sampled. 
    
    # raiseNotDefined()
def getObservationProb(self, noisyDistance, pacmanPosition, ghostPosition, jailPosition):
    """
    Return the probability P(noisyDistance | pacmanPosition, ghostPosition).
    """
    "*** YOUR CODE HERE ***"
    # Special Case 1: The ghost is in jail :(
    if ghostPosition == jailPosition:
        return 1.0 if noisyDistance is None else 0.0
    
    # Special Case 2: The noisy distance is None (meaning the ghost is also in jail)
    if noisyDistance is None: # if we recieve None but ghost is not in jail, then the probability is 0.0
        return 0.0

    # calculate the true manhattan distance between pacman and ghost
    trueDistance = manhattanDistance(pacmanPosition, ghostPosition)

    # get the probability of seeing noisyDistance given the true distance. this is the true distance pacman gets from his sensor but +- some error. 
    return busters.getObservationProbability(noisyDistance, trueDistance)
    # raiseNotDefined()



def observeUpdate(self, observation, gameState):
    """
    Update beliefs based on the distance observation and Pacman's position.

    The observation is the noisy Manhattan distance to the ghost you are
    tracking.

    self.allPositions is a list of the possible ghost positions, including
    the jail position. You should only consider positions that are in
    self.allPositions.

    The update model is not entirely stationary: it may depend on Pacman's
    current position. However, this is not a problem, as Pacman's current
    position is known.
    ------------------------------------------------------------------
    The equation of the inference problem we are trying to solve is:
    P(ghostPos | observation) ∝ P(observation | ghostPos) * P(ghostPos)
    Where:
    - P(ghostPos | observation) is our updated belief about the ghost position
    - P(observation | ghostPos) is the probability of observing the given a ghost position
    - P(ghostPos) is our prior belief about the ghost position
    """
    "*** YOUR CODE HERE ***"
    pacmanPosition = gameState.getPacmanPosition()
    jailPosition = self.getJailPosition()

    # Case when observation is None, we know the ghost is in jail with probabilty 1 and the belief at all other positions to be 0.
    if observation is None:
        for position in self.allPositions:
            self.beliefs[position] = 1.0 if position == jailPosition else 0.0
        return  
    
    # Regular Case where we update beliefs based on observation probabilities. For each possible ghost position, calculate the probability of getting the current observation given
    # the ghost is in that position. Then update the belief at that position using the equation of the inference problem.
    for ghostPosition in self.allPositions:
        observationProb = self.getObservationProb(observation, pacmanPosition, ghostPosition, jailPosition)
        self.beliefs[ghostPosition] = observationProb * self.beliefs[ghostPosition]

    # Only normalize when there are non-zero beliefs
    if self.beliefs.total() > 0:
        self.beliefs.normalize()
    else:
        # If all beliefs become zero (happens in 1 case at move 8 (1,1)) we set the jail posisiton to probability 1.0 as a fallback so that the beliefs remain valid
        if observation is None:
            self.beliefs[jailPosition] = 1.0
    
    self.beliefs.normalize()
    # raiseNotDefined()

def elapseTime(self, gameState):
    """
    Predict beliefs in response to a time step passing from the current
    state.

    The transition model is not entirely stationary: it may depend on
    Pacman's current position. However, this is not a problem, as Pacman's
    current position is known.

    """
    "*** YOUR CODE HERE ***"
    #raiseNotDefined()
    
    pacmanPos = gameState.getPacmanPosition()
    newDict = {}

    # check pos distribution for every position
    for belief in self.beliefs:
        # new position distribution given old position
        newPosDist = self.getPositionDistribution(gameState, belief)

        # calculate + sum possibilities
        for pos in newPosDist:
            posProb = newPosDist[pos] * self.beliefs[belief]

            if pos in newDict.keys():
                newDict[pos] += posProb
            else:
                newDict[pos] = posProb
    
    # update beliefs
    for belief in self.beliefs:
        self.beliefs[belief] = 0.0
    
    for pos in newDict:
        self.beliefs[pos] += newDict[pos]
