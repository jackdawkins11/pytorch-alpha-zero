
import encoder
import numpy as np

class Node:

    def __init__( self, board, neuralNetwork, isOpponent=False ):

        value, move_probabilities = encoder.callNeuralNetwork( board, neuralNetwork )

        if isOpponent:
            value *= -1.

        self.sum_Q = value / 2. + 0.5
        
        self.N = 1.

        self.edges = []

        for idx, move in enumerate( board.legal_moves ):
            edge = Edge( move, move_probabilities[ idx ] )
            self.edges.append( edge )

    def UCTSelect( self ):

        max_uct = -1.
        max_edge = None

        for edge in self.edges:

            Q = edge.getQ()

            N_c = edge.getN()

            P = edge.getP()

            C = 1.5

            val = Q + P * C * np.sqrt( self.N ) / ( 1 + N_c )

            if max_uct < val:
                max_uct = val
                max_edge = edge

        return max_edge

    def rollout( self, board, neuralNetwork ):

        orig_turn = board.turn

        rollout_path = [ self ]

        edge = self.UCTSelect()

        board.push( edge.getMove() )

        while edge.has_child():

            node = edge.getChild()

            rollout_path.append( node )

            edge = node.UCTSelect()

            if edge != None:

                board.push( edge.getMove() )

            else:

                break

        if edge != None:
            new_Q = edge.expand( board, neuralNetwork, orig_turn != board.turn )
        else:
            new_Q = 0.5

        for node in rollout_path:

            node.N += 1

            node.sum_Q += new_Q

    def maxNSelect( self ):

        max_N = -1
        max_edge = None

        for edge in self.edges:

            N = edge.getN()

            if max_N < N:
                max_N = N
                max_edge = edge

        return max_edge

class Edge:

    def __init__( self, move, move_probability ):

        self.move = move

        self.P = move_probability

        self.child = None

    def has_child( self ):

        return self.child != None

    def getN( self ):

        if self.has_child():
            return self.child.N
        else:
            return 0.

    def getQ( self ):

        if self.has_child():
            return self.child.sum_Q / self.child.N
        else:
            return 0.

    def getP( self ):

        return self.P

    def expand( self, board, neuralNetwork, isOpponent ):

        self.child = Node( board, neuralNetwork, isOpponent )

        return self.child.sum_Q

    def getChild( self ):

        return self.child

    def getMove( self ):

        return self.move
