
import argparse
import chess
import MCTS
import torch
import AlphaZeroNetwork

def tolist( mainline_moves ):
    moves = []
    for move in mainline_moves:
        moves.append( move )
    return moves


def main():

    #prepare neural network
    parser = argparse.ArgumentParser(description='View a self play game using the network.')
    parser.add_argument( '--model', help='Path to model (.pt) file.' )
    parser = parser.parse_args()

    alphaZeroNet = AlphaZeroNetwork.AlphaZeroNet( 20, 256 )

    alphaZeroNet.load_state_dict( torch.load( parser.model ) )

    alphaZeroNet = alphaZeroNet.cuda()

    for param in alphaZeroNet.parameters():
        param.requires_grad = False

    alphaZeroNet.eval()

    #self play
    board = chess.Board()

    while True:

        if board.is_game_over():
            print( 'Game over. Winner: {}'.format( board.result() ) )
            board.reset_board()
            c = input( 'Enter any key to continue ' )

        print( 'Whites turn: {}'.format( board.turn ) )
        print( board )


        if board.turn:
            move_list = tolist( board.legal_moves )

            for idx, move in enumerate( move_list ):
                print( '{} {}'.format( idx, move ) )
            
            idx = int( input( 'Choose a move ' ) )
            
            board.push( move_list[ idx ] )

        else:
        
            root = MCTS.createRoot( board, alphaZeroNet )
            
            for i in range( 100 ):
                root.parallelRollouts( board.copy(), alphaZeroNet )
        
            print( root.getStatisticsString() )
     
            edge = root.maxNSelect()
        
            board.push( edge.getMove() )


if __name__=='__main__':
    main()
