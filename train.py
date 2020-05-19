
import os
import torch.optim as optim
from torch.utils.data import DataLoader
from CCRLDataset import CCRLDataset
from AlphaZeroNetwork import AlphaZeroNet

NUM_EPOCHS = 100

def train():

    ccrl_root_dir = '/home/jack/Downloads/ccrl-dataset/ccrl-reformated'

    ccrl_train_dir = os.path.join( ccrl_root_dir, 'train' )
    
    ccrl_test_dir = os.path.join( ccrl_root_dir, 'test' )

    train_ds = CCRLDataset( ccrl_train_dir )

    test_ds = CCRLDataset( ccrl_test_dir )

    train_loader = DataLoader( train_ds, batch_size=64, shuffle=True, num_workers=32 )

    alphaZeroNet = AlphaZeroNet( 20, 256 ).cuda()

    optimizer = optim.Adam( alphaZeroNet.parameters() )

    for epoch in range( NUM_EPOCHS ):

        alphaZeroNet.train()

        for iter_num, data in enumerate( train_loader ):

            optimizer.zero_grad()

            position = data[ 'position' ].cuda()

            valueTarget = data[ 'value' ].cuda()

            policyTarget = data[ 'policy' ].cuda()

            valueLoss, policyLoss = alphaZeroNet( position, valueTarget=valueTarget,
                                 policyTarget=policyTarget )

            loss = valueLoss + policyLoss

            loss.backward()

            optimizer.step()

            if( iter_num % 1000 == 0 ):
                
                print( 'Epoch {} | Step {} / {} | Value loss {} | Policy loss {}'.format(
                        epoch, iter_num, len( train_loader ), float( valueLoss ), float( policyLoss ) ) )

if __name__ == '__main__':

    train()
