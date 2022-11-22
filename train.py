
import os
import torch
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader
from CCRLDataset import CCRLDataset
from AlphaZeroNetwork import AlphaZeroNet

#Training params
num_epochs = 40
num_blocks = 10
num_filters = 128
ccrl_dir = '/home/ubuntu/pytorch-alpha-zero/ccrl/reformated'
logmode=True
cuda=False

def train():
    train_ds = CCRLDataset( ccrl_dir )
    train_loader = DataLoader( train_ds, batch_size=256, shuffle=True, num_workers=48 )

    if cuda:
        alphaZeroNet = AlphaZeroNet( num_blocks, num_filters ).cuda()
    else:
        alphaZeroNet = AlphaZeroNet( num_blocks, num_filters )
    optimizer = optim.Adam( alphaZeroNet.parameters() )
    mseLoss = nn.MSELoss()

    print( 'Starting training' )

    for epoch in range( num_epochs ):
        
        alphaZeroNet.train()
        for iter_num, data in enumerate( train_loader ):

            optimizer.zero_grad()

            if cuda:
                position = data[ 'position' ].cuda()
                valueTarget = data[ 'value' ].cuda()
                policyTarget = data[ 'policy' ].cuda()
            else:
                position = data[ 'position' ]
                valueTarget = data[ 'value' ]
                policyTarget = data[ 'policy' ]

            # You can manually examine some the training data here

            valueLoss, policyLoss = alphaZeroNet( position, valueTarget=valueTarget,
                                 policyTarget=policyTarget )

            loss = valueLoss + policyLoss

            loss.backward()

            optimizer.step()

            message = 'Epoch {:03} | Step {:05} / {:05} | Value loss {:0.5f} | Policy loss {:0.5f}'.format(
                     epoch, iter_num, len( train_loader ), float( valueLoss ), float( policyLoss ) )
            
            if iter_num != 0 and not logmode:
                print( ('\b' * len(message) ), end='' )
            print( message, end='', flush=True )
            if logmode:
                print('')
        
        print( '' )
        
        networkFileName = 'AlphaZeroNet_{}x{}.pt'.format( num_blocks, num_filters ) 

        torch.save( alphaZeroNet.state_dict(), networkFileName )

        print( 'Saved model to {}'.format( networkFileName ) )

if __name__ == '__main__':

    train()
