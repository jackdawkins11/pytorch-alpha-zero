
import chess.pgn
import numpy as np
import os
import torch
from torch.utils.data import Dataset
import encoder

def tolist( mainline_moves ):
    """
    Change an iterable object of moves to a list of moves.
    
    Args:
        mainline_moves (Mainline object) iterable list of moves

    Returns:
        moves (list of chess.Move) list version of the input moves
    """
    moves = []
    for move in mainline_moves:
        moves.append( move )
    return moves

class CCRLDataset( Dataset ):
    """
    Subclass of torch.utils.data.Dataset for the ccrl dataset.
    """

    def __init__( self, ccrl_dir ):
        """
        Args:
            ccrl_dir (string) Path to directory containing
                pgn files with names 0.pgn, 1.pgn, 2.pgn, etc.
        """
        self.ccrl_dir = ccrl_dir
        self.pgn_file_names = os.listdir( ccrl_dir )

    def __len__( self ):
        """
        Get length of dataset
        """
        return len( self.pgn_file_names )

    def __getitem__( self, idx ):
        """
        Load the game in idx.pgn
        Get a random position, the move made from it, and the winner
        Encode these as numpy arrays
        
        Args:
            idx (int) the index into the dataset.
        
        Returns:
           position (torch.Tensor (16, 8, 8) float32) the encoded position
           policy (torch.Tensor (1) long) the target move's index
           value (torch.Tensor (1) float) the encoded winner of the game
           mask (torch.Tensor (72, 8, 8) int) the legal move mask
        """
        pgn_file_name = self.pgn_file_names[ idx ]
        pgn_file_name = os.path.join( self.ccrl_dir, pgn_file_name )
        pgn_fh = open( pgn_file_name )
        game = chess.pgn.read_game( pgn_fh )

        moves = tolist( game.mainline_moves() )

        randIdx = int( np.random.random() * ( len( moves ) - 1 ) )

        board = game.board()

        for idx, move in enumerate( moves ):
            board.push( move )
            if( randIdx == idx ):
                next_move = moves[ idx + 1 ]
                break

        winner = encoder.parseResult( game.headers[ 'Result' ] )

        position, policy, value, mask = encoder.encodeTrainingPoint( board, next_move, winner )
            
        return { 'position': torch.from_numpy( position ),
                 'policy': torch.Tensor( [policy] ).type( dtype=torch.long ),
                 'value': torch.Tensor( [value] ),
                 'mask': torch.from_numpy( mask ) }
