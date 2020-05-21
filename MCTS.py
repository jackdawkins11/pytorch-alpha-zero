
import encoder
import math
from threading import Thread

num_parallel_rollouts = 30

def createRoot( board, neuralNetwork ):
    
    value, move_probabilities = encoder.callNeuralNetwork( board, neuralNetwork )

    Q = value / 2. + 0.5

    return Node( board, Q, move_probabilities )

def calcUCT( edge, N_p ):
    """
    Calculate the UCT formula.
    Args:
        edge (Edge) the edge which the UCT formula is for
        N_p (float) the parents visit count
    """

    Q = edge.getQ()

    N_c = edge.getN()

    P = edge.getP()

    C = 1.5

    UCT = Q + P * C * math.sqrt( N_p ) / ( 1 + N_c )

    return UCT

class Node:

    def __init__( self, board, new_Q, move_probabilities ):
        """
        Args:
            board (chess.Board) the chess board
            new_Q (float) the probability of winning according to neural network
            move_probabilities (numpy.array (200) float) probability distribution across move list
        """

        self.sum_Q = new_Q
        
        self.N = 1.

        self.edges = []

        for idx, move in enumerate( board.legal_moves ):
            edge = Edge( move, move_probabilities[ idx ] )
            self.edges.append( edge )

        self.virtualLosses = 0.

    def UCTSelect( self ):
        """
        Get the edge that maximizes the UCT formula.
        Returns:
            max_edge (Edge) the edge maximizing the UCT formula.
        """

        max_uct = -1.
        max_edge = None

        for edge in self.edges:

            uct = calcUCT( edge, self.N )

            if max_uct < uct:
                max_uct = uct
                max_edge = edge

        return max_edge

    def addVirtualLoss( self ):

        self.virtualLosses += 100.

    def clearVirtualLoss( self ):

        self.virtualLosses = 0.
    
    def selectTask( self, board, rollout_path, final_edge ):
        """
        Do the selection stage of MCTS.

        Args/Returns:
            board (chess.Board) the root position on input,
                the position of the last node on return.
            rollout_path (list of Node) ordered list of nodes traversed
            final_edge (list of Edge) used to return the final edge selected
                if this edge is None, the last node is terminal
        """

        rollout_path.append( self )

        edge = self.UCTSelect()

        board.push( edge.getMove() )

        while edge.has_child():

            node = edge.getChild()

            node.addVirtualLoss()

            rollout_path.append( node )

            edge = node.UCTSelect()

            if edge != None:

                board.push( edge.getMove() )

            else:

                break

        final_edge.append( edge )

    def rollout( self, board, neuralNetwork ):
        """
        Each rollout traverses the tree until
        it reaches an un-expanded edge, or no
        edge in the case we visit a terminal node.
        This edge is then expanded and its
        win estimate is propagated to all the
        nodes between the root and the edge.
        If the edge does not exist, we use the
        terminal nodes win status.

        Args:
            board (chess.Board) the chess position
            neuralNetwork (torch.nn.Module) the neural network
        """
        
        rollout_path = []
        final_edge = []

        self.selectTask( board, rollout_path, final_edge )

        edge = final_edge[ 0 ]

        if edge != None:
            value, move_probabilities = encoder.callNeuralNetwork( board, neuralNetwork )

            new_Q = value / 2. + 0.5

            edge.expand( board, new_Q, move_probabilities )

            turn_modulo = 1

        else:
            winner = encoder.parseResult( board.result() )

            if not board.turn:
                winner *= -1

            new_Q = float( winner ) / 2. + 0.5
            
            turn_modulo = 0
            
        rollout_path.reverse()

        for idx, node in enumerate( rollout_path ):

            node.N += 1

            if idx % 2 == turn_modulo:

                node.sum_Q += new_Q

            else:
                
                node.sum_Q += 1. - new_Q


    def parallelRollouts( self, board, neuralNetwork ):
        """
        Same as rollout, except done in parallel.

        Args:
            board (chess.Board) the chess position
            neuralNetwork (torch.nn.Module) the neural network
        """

        boards = []
        rollout_paths = []
        final_edges = []
        threads = []

        for i in range( num_parallel_rollouts ):
            boards.append( board.copy() )
            rollout_paths.append( [] )
            final_edges.append( [] )
            threads.append( Thread( target=self.selectTask,
                    args=( boards[ i ], rollout_paths[ i ], final_edges[ i ] ) ) )
            threads[ i ].start()

        for i in range( num_parallel_rollouts ):
            threads[ i ].join()

        values, move_probabilities = encoder.callNeuralNetworkBatched( boards, neuralNetwork )

        for i in range( num_parallel_rollouts ):
            edge = final_edges[ i ][ 0 ]
            board = boards[ i ]
            value = values[ i ]
            board = boards[ i ]
            if edge != None:
                
                new_Q = value / 2. + 0.5
                
                edge.expand( board, new_Q,
                        move_probabilities[ i ] )
                
                
                turn_modulo = 1
            else:
                winner = encoder.parseResult( board.result() )

                if not board.turn:
                    winner *= -1

                new_Q = float( winner ) / 2. + 0.5

                turn_modulo = 0

            rollout_paths[ i ].reverse()
            
            for idx, node in enumerate( rollout_paths[ i ] ):
                
                node.N += 1.

                if idx % 2 == turn_modulo:

                    node.sum_Q += new_Q

                else:
                    
                    node.sum_Q += 1. - new_Q

                node.clearVirtualLoss()
    
    def maxNSelect( self ):
        """
        Returns:
            max_edge (Edge) the edge with maximum N.
        """

        max_N = -1
        max_edge = None

        for edge in self.edges:

            N = edge.getN()

            if max_N < N:
                max_N = N
                max_edge = edge

        return max_edge

    def getStatisticsString( self ):
        """
        Get a string containing the current search statistics.
        Returns:
            string (string) a string describing all the moves from this node
        """

        string = '|{: ^10}|{: ^10}|{: ^10}|{: ^10}|{: ^10}|\n'.format(
                'move', 'P', 'N', 'Q', 'UCT' )

        edges = self.edges.copy()

        edges.sort( key=lambda edge: edge.getN() )

        edges.reverse()

        for edge in edges:

            move = edge.getMove()

            P = edge.getP()

            N = edge.getN()

            Q = edge.getQ()

            UCT = calcUCT( edge, self.N )

            string += '|{: ^10}|{:10.4f}|{:10.4f}|{:10.4f}|{:10.4f}|\n'.format(
                str( move ), P, N, Q, UCT )

        return string

class Edge:

    def __init__( self, move, move_probability ):
        """
        Args:
            move (chess.Move) the move this edge represents
            move_probability (float) this move's probability from the neural network
        """

        self.move = move

        self.P = move_probability

        self.child = None

    def has_child( self ):
        """
        Returns:
            (bool) whether this edge has a child
        """

        return self.child != None

    def getN( self ):
        """
        Returns:
            (int) the child's N
        """

        if self.has_child():
            return self.child.N
        else:
            return 0.

    def getQ( self ):
        """
        Returns:
            (int) the child's Q
        """

        if self.has_child():
            return 1. - ( self.child.sum_Q / (self.child.N + self.child.virtualLosses) )
        else:
            return 0.

    def getP( self ):
        """
        Returns:
            (int) this move's probability (P)
        """

        return self.P

    def expand( self, board, new_Q, move_probabilities ):
        """
        Create the child node with the given board position.
        Args:
            board (chess.Board) the chess position
            new_Q (float) the probability of winning according to the neural network
            move_probabilities (numpy.array (200) float) the move probabilities according to the neural network
        """

        self.child = Node( board, new_Q, move_probabilities )

    def getChild( self ):
        """
        Returns:
            (Node) this edge's child node
        """

        return self.child

    def getMove( self ):
        """
        Returns:
            (chess.Move) this edge's move
        """

        return self.move
