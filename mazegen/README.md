*This project has been created as part of the 42 curriculum by urkamins, vijain.*

## Table of Contents
- [Description](#description)
    - [Maze Generation](#maze-generation)
    - [Output File](#output-file)
- [Instructions](#instructions)
    - [Prerequisites](#prerequisites)
    - [Config](#config)
    - [Usage](#usage)
- [Core Classes & Functions](#core-classes--functions)
    - [MazeConfig](#mazeconfig-maze_configpy)
    - [MazeGenerator](#mazegenerator-generatorpy)
    - [MazeSolver](#mazesolver-maze_solverpy)
    - [Maze](#maze-mazepy)
- [Algorithm](#algorithm)
    - [Maze Generation](#maze-generation)
    - [Path Generation](#path-generation)
- [License](#license)

## Description
This package provides the logic for generating, validating, and solving customizable mazes with a 42 logo embedded in the middle. It handles configuration validation, two maze generation algorithms, frame yielding, and calculation of shortest-path between the entry and exit points. 

### Maze Generation
The maze is generated using one of the two available algorithms creating a perfect maze and then optionally removing dead ends for braided mazes. The generation process of passage openings between neighbouring cells can be stepped through programmatically using generate_maze_frames function in MazeGenerator. 

### Output File
The program generates an output file that consists of maze information:
- hexadecimal representation of the maze where the value informs of existing walls of each consecutive cell
- coordinates of entry and exit
- the shortest entry -> exit path in a form of a list of directions

## Instructions
### Prerequisites
- Python 3.10 or newer
- pip

### Install the package
Navigate to the project directory and run
```bash
pip install mazegen-0.1.0-py3-none-any.whl
```

### Usage
```Python
from mazegen.generator import MazeGenerator, Mazegen

config = {
    "width": "15",
    "height": "10",
    "entry": "0,0",
    "exit": "14,9",
    "output_file": "maze_output.txt",
    "perfect": "True",
    "algorithm": "Prim"
}

generator = MazeGenerator(config)
completed_maze: Maze = generator.generate_maze()
print("Solution path:", completed_maze.path)
```

### Config
The config consist of several mandatory and optional fields 
that needs to be provided as strings.
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

## Core Classes & Functions

### MazeGenerator
Manages the lifecycle of the maze, configuration settings and algorithm execution
- attributes: **entry, exit, algorithm_name**
- **generate_maze_frames():** Yields incremental np.ndarray snapshots of the grid as walls are carved out, allowing step-by-step progress tracking.   
- **generate_maze():** Runs all generation frames to completion and returns the final Maze object.   
- **store_maze():** Computes the solution path, builds the Maze instance, and triggers output file writing.   
- **next_algorithm():** Switches between available generation algorithms dynamically.   


### Maze
Data container holding the completed maze state and analytical helper methods.
- attributes: **entry, exit, path, logo_coords, walls**
- **is_logo() / is_entry() / is_exit() / is_path():** Boolean utility checkers 
that identify specific cell roles within the grid.   
- **get_wall():** Returns the integer bitmask representing walls for a specific cell.   
- **get_full_path_bitmask():** Compiles cell direction bitmasks sequentially along the solution path. 


## Algorithm
### Maze Generation

Two maze generation algorithms are available for the user to generate the maze. Both algorithms share the same braiding step, which removes dead ends after the maze has been generated.

#### Prim's Algorithm

Prim’s algorithm works by starting from an arbitrary vertex, adding the edge that connects the tree to a new vertex, and repeating this process until all vertices have been included in the tree.

The time complexity of Prims's Algorithm is: O(n log(n)), where n is the number of nodes(cells).

#### Kruskal's Algorithm

The algorithm treats every non-logo cell as a separate group and creates possible connections between neighbouring cells. These connections are shuffled, then checked one by one. A connection is opened only when the two cells belong to different groups. The groups are then joined together. 
This builds the maze without creating loops.

We chose Kruskal's algorithm because it lets us build the maze by considering each possible passage separately. 
Shuffling the passages gives every maze a different layout, 
while grouping cells ensures that passages are added without creating cycles.

The time complexity of Kruskal's Algorithm is: O(n log(n))

#### Braiding Algorithm
The braiding algorithm removes dead ends by opening an additional passage from each dead-end cell to an eligible neighbour with the fewest open passages. This creates loops and offers multiple possible routes through the maze.

If no suitable neighbour exists (in case of cells neighboring with the logo), the dead end is left unchanged.

### Path Generation
The shortest path from the entry to the exit point is computed using the MazeSolver class, which implements Breadth-First Search (BFS).

The class uses a double-ended queue (deque) to explore reachable neighboring cells level by level, guaranteeing that the first time the exit cell is popped, 
the shortest path has been found. For each current cell, the solver evaluates the cell's wall bitmask (Dir.N, Dir.S, Dir.W, Dir.E) to verify which adjacent directions have open passages.

A visited set prevents duplicate visits, and a parent_map dictionary keeps track of the predecessor for each node. Once the exit is reached, the algorithm backtracks 
from the exit node to the entry node using the parent_map, reverses the sequence, and returns an ordered list of coordinate nodes representing the path (or an empty list 
if unreachable).

## License
This project is licensed under the MIT License - see the LICENSE file for details. The MIT License is a short, highly permissive open-source software license that allows anyone to freely use, copy, modify, merge, publish, distribute, and sell  code. Additionally, it protects creators by providing a complete disclaimer of warranty and liability.