
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

def main( modelFile, mode, color, num_rollouts, num_threads, fen, verbose ):
    #prepare neural network
    alphaZeroNet = AlphaZeroNetwork.AlphaZeroNet( 20, 256 )

    alphaZeroNet.load_state_dict( torch.load( modelFile ) )

    alphaZeroNet = alphaZeroNet.cuda()

    for param in alphaZeroNet.parameters():
        param.requires_grad = False

    alphaZeroNet.eval()
    
    if fen:
        board = chess.Board( fen )
    else:
        board = chess.Board()

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

        if mode == 'h' and board.turn == color:
            move_list = tolist( board.legal_moves )

            idx = -1

            while not (0 <= idx and idx < len( move_list ) ):
            
                string = input( 'Choose a move ' )

                for i, move in enumerate( move_list ):
                    if str( move ) == string:
                        idx = i
                        break
            
            board.push( move_list[ idx ] )

        else:
                
            starttime = time.perf_counter()

            with torch.no_grad():

                root = MCTS.Root( board, alphaZeroNet )
            
                for i in range( num_rollouts ):
                    root.parallelRollouts( board.copy(), alphaZeroNet, num_threads )

            endtime = time.perf_counter()

            elapsed = endtime - starttime

            Q = root.getQ()

            N = root.getN()

            nps = N / elapsed

            same_paths = root.same_paths
       
            if verbose:
                print( root.getStatisticsString() )
                print( 'total rollouts {} Q {:0.3f} duplicate paths {} elapsed {:0.2f} nps {:0.2f}'.format( int( N ), Q, same_paths, elapsed, nps ) )
     
            edge = root.maxNSelect()

            bestmove = edge.getMove()

            print( 'best move {}'.format( str( bestmove ) ) )
        
            board.push( bestmove )

        if mode == 'p':
            break

def parseColor( colorString ):

    if colorString == 'w' or colorString == 'W':
        return True
    elif colorString == 'b' or colorString == 'B':
        return False
    else:
        print( 'Unrecognized argument for color' )
        exit()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Play versus the computer.')
    parser.add_argument( '--model', help='Path to model (.pt) file.' )
    parser.add_argument( '--mode', help='Operation mode: \'s\' self play, \'p\' profile, \'h\' human' )
    parser.add_argument( '--color', help='Your color w or b' )
    parser.add_argument( '--rollouts', type=int, help='The number of rollouts on computers turn' )
    parser.add_argument( '--threads', type=int, help='Number of threads used per rollout' )
    parser.add_argument( '--verbose', help='Print search statistics', action='store_true' )
    parser.add_argument( '--fen', help='Starting fen' )
    parser.set_defaults( verbose=False, mode='p', color='w', rollouts=10, threads=1 )
    parser = parser.parse_args()

    main( parser.model, parser.mode, parseColor( parser.color ), parser.rollouts, parser.threads, parser.fen, parser.verbose )

