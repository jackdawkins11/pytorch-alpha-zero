
import chess.pgn
import os
import numpy as np

"""
This program reformats the ccrl dataset from how
it was downloaded into a more useable way. To run,
just specify the folder the dataset was downloaded
to using ccrl_root_dir and where the reformated data should
be saved using new_root_dir. new_root_dir must not exist
but its parent directory must exist.
"""

ccrl_root_dir = '/home/jack/Downloads/ccrl-dataset/ccrl'

ccrl_train_dir = os.path.join( ccrl_root_dir, 'train' )

ccrl_test_dir = os.path.join( ccrl_root_dir, 'test' )

train_file_names = os.listdir( ccrl_train_dir )

test_file_names = os.listdir( ccrl_test_dir )

def next_game( dir_name, file_names ):
     global pgn_fh
     game = chess.pgn.read_game( pgn_fh )

     if not game:
         if len( file_names ) == 0:
             game = None
         else:
            pgn_fh = open( os.path.join( dir_name, file_names.pop() ) )
            game = chess.pgn.read_game( pgn_fh )

     return game

#create new directory

new_root_dir = '/home/jack/Downloads/ccrl-dataset/ccrl-reformated'
if os.path.exists( new_root_dir ):
    print( 'Error directory exists' )
    exit()

os.mkdir( new_root_dir )

#create train directory, write train pngs

new_train_dir = os.path.join( new_root_dir, 'train' )

os.mkdir( new_train_dir )

file_name_idx = 0

pgn_fh = open( os.path.join( ccrl_train_dir, train_file_names.pop() ) )
while True:
    game = next_game( ccrl_train_dir, train_file_names )

    if not game:
        break

    file_name = '{}.pgn'.format( file_name_idx )

    file_name_idx += 1

    print( game, file=open( os.path.join( new_train_dir, file_name ), 'w' ), end='\n\n' )

    if file_name_idx % 1000 == 0:
        print( 'Wrote {} train pngs'.format( file_name_idx ) )

#create test directory, write test pngs

new_test_dir = os.path.join( new_root_dir, 'test' )

os.mkdir( new_test_dir )

file_name_idx = 0

pgn_fh = open( os.path.join( ccrl_test_dir, test_file_names.pop() ) )
while True:
    game = next_game( ccrl_test_dir, test_file_names )

    if not game:
        break

    file_name = '{}.pgn'.format( file_name_idx )

    file_name_idx += 1

    print( game, file=open( os.path.join( new_test_dir, file_name ), 'w' ), end='\n\n' )

    if file_name_idx % 1000 == 0:
        print( 'Wrote {} test pngs'.format( file_name_idx ) )

