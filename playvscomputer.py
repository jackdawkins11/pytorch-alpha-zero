
import argparse
import chess
import MCTS
import torch
import AlphaZeroNetwork
import time

def tolist( move_generator ):
    moves = []
    for move in move_generator:
        moves.append( move )
    return moves

def parseColor( colorString ):

    if colorString == 'w' or colorString == 'W':
        return True
    elif colorString == 'b' or colorString == 'B':
        return False
    else:
        print( 'Unrecognized argument for color' )
        exit()

def main():

    parser = argparse.ArgumentParser(description='Play versus the computer.')
    parser.add_argument( '--model', help='Path to model (.pt) file.' )
    parser.add_argument( '--rollouts', type=int, help='The number of rollouts on computers turn' )
    parser.add_argument( '--verbose', help='Print search statistics', action='store_true' )
    parser.add_argument( '--color', help='Your color w or b' )
    parser.add_argument( '--threads', type=int, help='Number of threads used per rollout' )
    parser.set_defaults( verbose=False, color='w', rollouts=10 )
    parser = parser.parse_args()

    #prepare neural network
    alphaZeroNet = AlphaZeroNetwork.AlphaZeroNet( 20, 256 )

    alphaZeroNet.load_state_dict( torch.load( parser.model ) )

    alphaZeroNet = alphaZeroNet.cuda()

    for param in alphaZeroNet.parameters():
        param.requires_grad = False

    alphaZeroNet.eval()

    #self play
    board = chess.Board()

    num_rollouts = parser.rollouts
    color = parseColor( parser.color )
    verbose = parser.verbose
    num_threads = parser.threads
    
    while True:

        if board.is_game_over():
            print( 'Game over. Winner: {}'.format( board.result() ) )
            board.reset_board()
            c = input( 'Enter any key to continue ' )

        if board.turn:
            print( 'White\'s turn' )
        else:
            print( 'Black\'s turn' )
        print( board )

        if board.turn == color:
            move_list = tolist( board.legal_moves )

            for idx, move in enumerate( move_list ):
                print( '{} {}'.format( idx, move ) )

            idx = -1

            while not (0 <= idx and idx < len( move_list ) ):
            
                string = input( 'Choose a move ' )

                try:
                    idx = int( string )
                except:
                    continue
            
            board.push( move_list[ idx ] )

        else:
        
            root = MCTS.Root( board, alphaZeroNet )
            
            starttime = time.perf_counter()

            for i in range( num_rollouts ):
                root.parallelRollouts( board.copy(), alphaZeroNet, num_threads )

            endtime = time.perf_counter()

            elapsed = endtime - starttime

            N = root.getN()

            nps = N / elapsed

            same_paths = root.same_paths
       
            if verbose:
                print( root.getStatisticsString() )
                print( 'total rollouts {} duplicate paths {} elapsed {:0.2f} nps {:0.2f}'.format( int( N ), same_paths, elapsed, nps ) )
     
            edge = root.maxNSelect()
        
            board.push( edge.getMove() )

if __name__=='__main__':
    main()
