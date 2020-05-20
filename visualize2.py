
import argparse
import chess
import MCTS
import torch
import AlphaZeroNetwork

def main():

    #prepare neural network
    parser = argparse.ArgumentParser(description='View a self play game using the network.')
    parser.add_argument( '--model', help='Path to model (.pt) file.' )
    parser = parser.parse_args()

    alphaZeroNet = AlphaZeroNetwork.AlphaZeroNet( 5, 64 )

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

        root = MCTS.Node( board, alphaZeroNet )

        for i in range( 10 ):
            root.rollout( board.copy(), alphaZeroNet )
       
        edge = root.maxNSelect()

        board.push( edge.getMove() )

        c = input( 'Enter any key to continue' )

if __name__=='__main__':
    main()
