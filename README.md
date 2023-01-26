# sliding_puzzle
# setup: A board with 5 rows and 4 columns 
One 2x2 piece.
Five 1x2 pieces. Each 1x2 piece can be horizontal or vertical.
Four 1x1 pieces.

Goal: Move the 2x2 tile to the location [3][1] [3][2] [4][1] [4][2]

example of input file:
^
v: represent a vertical 1x2, 
'<>' represents a horizontal 1x2, 1 represent goal tile (2x2), 
'.' means it is blank, where we can move our tile that fits in
'2' means it is a single 1x1 tile

^^^^
vvvv
22..
11<>
1122

# Use of A_star algo would give you the optimal solution to a solvable configuration.
# Steps are counted by moving 1 piece by only 1 block
# Ex: moving the 1x1 piece down by 2 takes 2 steps to finish
Usage:
    python3 hrd.py --algo astar --inputfile <input file> --outputfile <output file>    
    python3 hrd.py --algo dfs --inputfile <input file> --outputfile <output file>
