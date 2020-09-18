
# A chess engine based on the AlphaZero algorithm

This is a pytorch implementation of Google Deep Mind's AlphaZero algorithm for chess.

## Dependencies

Besides standard python libraries, this program requires pytorch set up to run on cuda.

## Running the chess engine

The entry point to the chess engine is the python file playchess.py. Run that file with the `-h` option to see the different options. Good parameters for playing against the computer as white would be
```python3 playchess.py --model weights/AlphaZeroNet_20x256.pt --verbose --rollouts 300 --threads 16 --mode h```
Note that running the engine requires a weights file.  
