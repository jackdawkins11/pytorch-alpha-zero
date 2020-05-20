
import encoder
import math

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

    def __init__( self, board, neuralNetwork, isOpponent=False ):
        """
        Args:
            board (chess.Board) the chess board
            neuralNetwork (torch.nn.Module) the neural network
            isOpponent (bool) whether this node's player is the same as the root's
        """

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
            return self.child.sum_Q / self.child.N
        else:
            return 0.

    def getP( self ):
        """
        Returns:
            (int) this move's probability (P)
        """

        return self.P

    def expand( self, board, neuralNetwork, isOpponent ):
        """
        Create the child node with the given board position.
        Args:
            board (chess.Board) the chess position
            neuralNetwork (torch.nn.Module) the neural network
            isOpponent (bool) whether the child's player is the same as the root's
        Returns:
            (float) the child's Q value
        """

        self.child = Node( board, neuralNetwork, isOpponent )

        return self.child.sum_Q

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
