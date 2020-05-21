
import os
import torch
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader
from CCRLDataset import CCRLDataset
from AlphaZeroNetwork import AlphaZeroNet

num_epochs = 500
num_blocks = 20
num_filters = 256

def train():

    ccrl_root_dir = '/home/jack/Downloads/ccrl-dataset/ccrl-reformated'

    ccrl_train_dir = os.path.join( ccrl_root_dir, 'train' )
    
    ccrl_test_dir = os.path.join( ccrl_root_dir, 'test' )

    train_ds = CCRLDataset( ccrl_train_dir )

    test_ds = CCRLDataset( ccrl_test_dir )

    train_batch_size = 512

    test_batch_size = 512

    train_loader = DataLoader( train_ds, batch_size=train_batch_size, shuffle=True, num_workers=32 )
   
    test_loader = DataLoader( test_ds, batch_size=test_batch_size, num_workers=32 )

    alphaZeroNet = AlphaZeroNet( num_blocks, num_filters ).cuda()

    optimizer = optim.Adam( alphaZeroNet.parameters() )

    mseLoss = nn.MSELoss()

    for epoch in range( num_epochs ):
 
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

            message = 'Epoch {:03} | Step {:05} / {:05} | Value loss {:0.5f} | Policy loss {:0.5f}'.format(
                     epoch, iter_num, len( train_loader ), float( valueLoss ), float( policyLoss ) )
 
            if iter_num != 0:
                print( ('\b' * len(message) ), end='' )
                                    
            print( message, end='', flush=True )
        
        print( '' )
 
        alphaZeroNet.eval()

        num_test_batch = len( test_loader )

        test_value_loss = 0.

        test_policy_loss = 0.

        total_correct_predictions = 0

        with torch.no_grad():

            for iter_num, data in enumerate( test_loader ):

                position = data[ 'position' ].cuda()

                valueTarget = data[ 'value' ].cuda()

                policyTarget = data[ 'policy' ].cuda()
            
                policyMask = data[ 'mask' ].cuda()

                value, policy = alphaZeroNet( position, policyMask=policyMask )

                valueLoss = mseLoss( value, valueTarget )
            
                test_value_loss += float( valueLoss ) / num_test_batch

                policyTarget = policyTarget.view( policyTarget.shape[0] )

                policy = torch.clamp( policy, min=1e-5 )

                policyLoss = torch.log( policy[ torch.arange( policyTarget.shape[0] ), policyTarget ] ).mean()
            
                test_policy_loss += float( policyLoss ) / num_test_batch

                correct_predictions = torch.eq( torch.argmax( policy, dim=1 ), policyTarget )

                total_correct_predictions += float( correct_predictions.sum() )

                message = 'Evaluating {:05} / {:05}'.format( iter_num, num_test_batch )
 
                if iter_num != 0:
                    print( ('\b' * len( message ) ), end='' )
                               
                print( message, end='', flush=True )

            print( '' )

        accuracy = 100 * total_correct_predictions / ( test_batch_size * num_test_batch )

        print( 'Evaluation results: value loss {:0.5f} | policy loss {:0.5f} | policy accuracy {:0.5f}%'.format(
                  test_value_loss, test_policy_loss, accuracy ) )

        networkFileName = 'AlphaZeroNet_{}x{}_{}.pt'.format( num_blocks, num_filters, epoch ) 

        torch.save( alphaZeroNet.state_dict(), networkFileName )

        print( 'Saved model to {}'.format( networkFileName ) )

if __name__ == '__main__':

    train()
