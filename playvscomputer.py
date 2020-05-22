
import argparse
import chess
import MCTS
import torch
import AlphaZeroNetwork

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
    parser.add_argument( '--rollouts', help='The number of rollouts on computers turn' )
    parser.add_argument( '--verbose', help='Print search statistics', action='store_true' )
    parser.add_argument( '--color', help='Your color' )
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

    num_rollouts = int( parser.rollouts )
    color = parseColor( parser.color )
    verbose = parser.verbose

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
            
            idx = int( input( 'Choose a move ' ) )
            
            board.push( move_list[ idx ] )

        else:
        
            root = MCTS.createRoot( board, alphaZeroNet )
            
            for i in range( num_rollouts ):
                root.parallelRollouts( board.copy(), alphaZeroNet )
       
            if verbose:
                print( root.getStatisticsString() )
     
            edge = root.maxNSelect()
        
            board.push( edge.getMove() )

if __name__=='__main__':
    main()
