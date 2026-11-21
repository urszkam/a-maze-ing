*This project has been created as part of the 42 curriculum by urkamins, vijain.*

## # Table of Contents
- [Description](#description)
    - [Maze Generation](#maze-generation)
    - [Output File](#output-file)
- [Instructions](#instructions)
    - [Prerequisites](#prerequisites)
    - [Config](#config)
    - [Usage](#usage)
- [Algorithm](#algorithm)
    - [Maze Generation](#maze-generation)
    - [Path Generation](#path-generation)
- [License](#license)

## Description
TODO


### Maze Generation
TODO

### Output File
The program generates an output file that consists of maze information:
- hexadecimal representation of the maze where the value informs of existing walls of each consecutive cell
- coordinates of entry and exit
- the entry -> exit path in a form of a list of directions

## Instructions
### Prerequisites
- Python 3.10 or newer

### Install the package
TODO

### Usage
TODO



### Config
The program takes one argument with a dictionary of configuration
values as strings.
The config consist of several mandatory and optional fields.
Mandatory fields:
- **width** (int) - number of maze columns, eg. 7
- **height** (int) - number of maze rows, eg. 12
- **entry** (tuple[int, int]) - x, y coordinates of the path start cell, eg. (11,8)
- **exit** (tuple[int, int]) - x, y coordinates of the path end cell, eg. (0,3)
- **output_file** (str) - name of the output file where the final maze data is saved,
  eg. maze.txt

Optional fields:
- **perfect** (bool) - bool whether the maze should be perfect with no loops, eg. True
  (default value is False)
- **seed** (int) - Random seed used for maze generation, eg. 123 (default value is 666)
- **algorithm** (str) - name of the maze generation algorithm, either Prim or Kruskal


## Algorithm
### Maze Generation

We decided to use two maze generation algorithms, 
between which the user can switch while using the application. 
Both algorithms share the same braiding step, 
which removes dead ends after the maze has been generated.

#### Prim's Algorithm

Prim’s algorithm works by starting from an arbitrary vertex, adding the edge 
that connects the tree to a new vertex, and repeating this process 
until all vertices have been included in the tree.

The time complexity of Prims's Algorithm is: O(n log(n)), where n is the number of nodes(cells).

#### Kruskal's Algorithm

The algorithm treats every non-logo cell as a separate group and creates
possible connections between neighbouring cells. 
These connections are shuffled, then checked one by one. 
A connection is opened only when the two cells belong to different groups. 
The groups are then joined together. 
This builds the maze without creating loops.

We chose Kruskal's algorithm because it lets us build the maze by considering
each possible passage separately. 
Shuffling the passages gives every maze a different layout, 
while grouping cells ensures that passages are added without creating cycles.

The time complexity of Kruskal's Algorithm is: O(n log(n))

#### Braiding Algorithm
The braiding algorithm removes dead ends by opening an additional passage from
each dead-end cell to an eligible neighbour with the fewest open passages.
This creates loops and offers multiple possible routes through the maze.
If no suitable neighbour exists (in case of cells neighboring with the logo), the dead end is left unchanged.

### Path Generation
The shortest path from the entry to the exit point is computed using the 
MazeSolver class, which implements Breadth-First Search (BFS).

The class uses a double-ended queue (deque) to explore reachable neighboring 
cells level by level, guaranteeing that the first time the exit cell is popped, 
the shortest path has been found. For each current cell, the solver evaluates the 
cell's wall bitmask (Dir.N, Dir.S, Dir.W, Dir.E) to verify which adjacent 
directions have open passages.

A visited set prevents duplicate visits, and a parent_map dictionary keeps track 
of the predecessor for each node. Once the exit is reached, the algorithm backtracks 
from the exit node to the entry node using the parent_map, reverses the sequence, and 
returns an ordered list of coordinate nodes representing the path (or an empty list 
if unreachable).

## License
TODO