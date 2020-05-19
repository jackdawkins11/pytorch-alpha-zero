
import argparse
import chess
import torch
import encoder
import numpy as np
import AlphaZeroNetwork
import torch.nn as nn

def toList( move_list_generator ):
    move_list = []
    for move in move_list_generator:
        move_list.append( move )
    return move_list

def main():

    parser = argparse.ArgumentParser(description='View a self play game using the network.')
    parser.add_argument( '--model', help='Path to model (.pt) file.' )
    parser = parser.parse_args()

    alphaZeroNet = AlphaZeroNetwork.AlphaZeroNet( 5, 64 )

    alphaZeroNet.load_state_dict( torch.load( parser.model ) )

    alphaZeroNet = alphaZeroNet.cuda()

    for param in alphaZeroNet.parameters():
        param.requires_grad = False

    alphaZeroNet.eval()

    board = chess.Board( '4k3/8/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq' )

    move_probabilities = np.zeros( (200), dtype=np.float32 )

    softmax = nn.Softmax()

    while True:

        if board.is_game_over():
            print( 'Game over. Winner: {}'.format( board.result() ) )
            board.reset_board()
            c = input( 'Enter any key to continue ' )

        move_list = toList( board.legal_moves )
        whitesTurn = board.turn

        position, mask = encoder.encodePositionForInference( board )

        position = torch.from_numpy( position )[ None, ... ].cuda()
        
        mask = torch.from_numpy( mask )[ None, ... ].cuda()

        value, policy = alphaZeroNet( position, policyMask=mask )

        value = value.cpu().numpy()[ 0 ]

        policy = policy.cpu().numpy()[ 0 ]

        value = encoder.decodeOutput( whitesTurn, move_list, value, policy, move_probabilities )

        print( 'Whites turn: {}'.format( whitesTurn ) )
        print( 'Win probability: {}'.format( value ) )
        print( board )
        total = 0.
        for idx, move in enumerate( move_list ):
            print( '{} {} {}'.format( idx, move, move_probabilities[ idx ] ) )
            total += move_probabilities[ idx ]
        print( total )

        choice = int( input( 'Enter a move ' ) )

        board.push( move_list[ choice ] )

if __name__=='__main__':
    main()
