
# A chess engine based on the AlphaZero algorithm

This is a pytorch implementation of Google Deep Mind's AlphaZero algorithm for chess.

## Live

[Play against it here](http://ec2-54-175-18-115.compute-1.amazonaws.com/index.html)

## Dependencies

Besides standard python libraries, this program requires pytorch set up to run on cuda.

## Running the chess engine

The entry point to the chess engine is the python file playchess.py. Run that file with the `-h` option to see the different options. Good parameters for playing against the computer as white would be:
```
python3 playchess.py --model weights/AlphaZeroNet_20x256.pt --verbose --rollouts 300 --threads 16 --mode h
```
The current position is displayed with an ascii chess board. Enter your moves in long algebraic notation. Note that running the engine requires a weights file.  

## About the algorithm

The algorithm is based on [this paper](https://arxiv.org/pdf/1712.01815.pdf). One very important difference between the algorithm used here and the one described in that paper is that this implementation used supervised learning instead of reinforcement learning. Doing reienforcement learning is very computationally intensive. As said in that paper, it took thousands of TPUs to generate the self play games. This program, on the other hand, trains on the [CCRL Dataset](https://lczero.org/blog/2018/09/a-standard-dataset/), which contains 2.5 million top notch chess games. Because each game has around 80 unique positions in it, this yields about 200 million data points for training on. 

## Strength

This engine is very weak for chess engine standards. However, its better than all but the top humans. I have only tested it a few times against stockfish running in my browser at [lichess](https://lichess.org/). It was able to beat it, but had to think for about a minute while its opponent only got a few seconds. Compared to most chess engines, like stockfish, which use the Alpha-Beta algorithm and a hand written evaluation function, it evaluates a lot fewer positions every second. Most top programs consider about 45 million chess positions every second, whereas this programs considers about 100, even with GPU and multicore speedups. 

## Video
* [Drawing Chess.com AI](https://youtu.be/zHTBfBq5PXY)
* [Training](https://youtu.be/IMUqCLswa3s)
