
import argparse
import chess
import MCTS
import torch
import AlphaZeroNetwork

def main():

    parser = argparse.ArgumentParser(description='View a self play game.')
    parser.add_argument( '--model', help='Path to model (.pt) file.' )
    parser.add_argument( '--wrollouts', help='The number of rollouts on white\'s turn' )
    parser.add_argument( '--brollouts', help='The number of rollouts on white\'s turn' )
    parser.add_argument( '--verbose', help='Print search statistics', action='store_true' )
    parser.set_defaults( verbose=False )
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

    wrollouts = int( parser.wrollouts )
    brollouts = int( parser.brollouts )

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

        root = MCTS.createRoot( board, alphaZeroNet )

        num_rollouts = wrollouts if board.turn else brollouts

        for i in range( num_rollouts ):
            root.parallelRollouts( board.copy(), alphaZeroNet )
       
        if parser.verbose:
            print( root.getStatisticsString() )

        edge = root.maxNSelect()

        board.push( edge.getMove() )

if __name__=='__main__':
    main()
