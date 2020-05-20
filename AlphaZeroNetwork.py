
import torch
import torch.nn as nn

class ConvBlock( nn.Module ):
    """
    The block consists of a conv layer, batch normalization layer
    and relu activation.
    """
    
    def __init__( self, input_channels, num_filters ):
        """
        Args:
            input_channels (int) the number of input channels
            num_filters (int) the number of filters in the conv layer
        """
        super().__init__()
        self.conv1 = nn.Conv2d( input_channels, num_filters, 3, padding=1 )
        self.bn1 = nn.BatchNorm2d( num_filters )
        self.relu1 = nn.ReLU()

    def __call__( self, x ):
        """
        Args:
            x (torch.Tensor) the tensor to apply the layers to.
        """
        x = self.conv1( x )
        x = self.bn1( x )
        x = self.relu1( x )

        return x

class ResidualBlock( nn.Module ):
    """
    A residual block.
    """

    def __init__( self, num_filters ):
        """
        Args:
            num_filters (int) the number of filters in the conv layers. Assumes this is the
            same as the number of input channels
        """
        super().__init__()
        self.conv1 = nn.Conv2d( num_filters, num_filters, 3,
                padding=1 )
        self.bn1 = nn.BatchNorm2d( num_filters )
        self.relu1 = nn.ReLU()
        self.conv2 = nn.Conv2d( num_filters, num_filters, 3,
                padding=1 )
        self.bn2 = nn.BatchNorm2d( num_filters )
        self.relu2 = nn.ReLU()

    def __call__( self, x ):
        """
        Args:
            x (torch.Tensor) the tensor to apply the layers to.
        """
        residual = x

        x = self.conv1( x )
        x = self.bn1( x )
        x = self.relu1( x )
        
        x = self.conv2( x )
        x = self.bn2( x )
        x += residual
        x = self.relu2( x )

        return x

class ValueHead( nn.Module ):
    """
    nn.Module for the value head
    """

    def __init__( self, input_channels ):
        """
        Args:
            input_channels (int) the number of input channels
        """
        super().__init__()
        self.conv1 = nn.Conv2d( input_channels, 1, 1 )
        self.bn1 = nn.BatchNorm2d( 1 )
        self.relu1 = nn.ReLU()
        self.fc1 = nn.Linear( 64, 256 )
        self.relu2 = nn.ReLU()
        self.fc2 = nn.Linear( 256, 1 )
        self.tanh1 = nn.Tanh()

    def __call__( self, x ):
        """
        Args:
            x (torch.Tensor) the tensor to apply the layers to.
        """

        x = self.conv1( x )
        x = self.bn1( x )
        x = self.relu1( x )
        x = x.view( x.shape[0], 64 )
        x = self.fc1( x )
        x = self.relu2( x )
        x = self.fc2( x )
        x = self.tanh1( x )

        return x

class PolicyHead( nn.Module ):
    """
    nn.Module for the policy head
    """

    def __init__( self, input_channels ):
        """
        Args:
            input_channels (int) the number of input channels
        """
        super().__init__()
        self.conv1 = nn.Conv2d( input_channels, 2, 1 )
        self.bn1 = nn.BatchNorm2d( 2 )
        self.relu1 = nn.ReLU()
        self.fc1 = nn.Linear( 128, 4608 )
    
    def __call__( self, x ):
        """
        Args:
            x (torch.Tensor) the tensor to apply the layers to.
        """

        x = self.conv1( x )
        x = self.bn1( x )
        x = self.relu1( x )
        x = x.view( x.shape[0], 128 )
        x = self.fc1( x )

        return x

class AlphaZeroNet( nn.Module ):
    """
    Neural network with AlphaZero architecture.
    """

    def __init__(self, num_blocks, num_filters ):
        """
        Args:
            num_blocks (int) the number of residual blocks
            filters_per_conv (int) the number of filters in each conv layer
        """
        super().__init__()
        #The number of input planes is fixed at 16
        self.convBlock1 = ConvBlock( 16, num_filters )

        residualBlocks = [ ResidualBlock( num_filters ) for i in range( num_blocks ) ]

        self.residualBlocks = nn.ModuleList( residualBlocks )

        self.valueHead = ValueHead( num_filters )

        self.policyHead = PolicyHead( num_filters )

        self.softmax1 = nn.Softmax( dim=1 )

        self.mseLoss = nn.MSELoss()
        
        self.crossEntropyLoss = nn.CrossEntropyLoss()

    def __call__( self, x, valueTarget=None, policyTarget=None, policyMask=None ):
        """
        Args:
            x (torch.Tensor) the input tensor.
            valueTarget (torch.Tensor) the value target.
            policyTarget (torch.Tensor) the policy target.
            policyMask (torch.Tensor) the legal move mask
        """

        x = self.convBlock1( x )

        for block in self.residualBlocks:
            x = block( x )

        value = self.valueHead( x )

        policy = self.policyHead( x )

        if self.training:
            
            valueLoss = self.mseLoss( value, valueTarget )

            policyTarget = policyTarget.view( policyTarget.shape[0] )

            policyLoss = self.crossEntropyLoss( policy, policyTarget )
            
            return valueLoss, policyLoss

        else:

            policyMask = policyMask.view( policyMask.shape[0], -1 )

            policy_exp = torch.exp( policy )

            policy_exp *= policyMask.type( torch.float32 )

            policy_exp_sum = torch.sum( policy_exp, dim=1, keepdim=True )
            
            policy_softmax = policy_exp / policy_exp_sum

            return value, policy_softmax

