*This project has been created as part of the 42 curriculum by urkamins, vijain.*

## # Table of Contents
- [Description](#description)
    - [Maze Generation](#maze-generation)
    - [Visualization](#visualization)
    - [Output File](#output-file)
    - [Bonus Features](#bonus-features)
- [Instructions](#instructions)
    - [Prerequisites](#prerequisites)
    - [Clone the Repository](#clone-the-repository)
    - [Config](#config)
    - [Usage](#usage)
    - [Linting](#linting)
    - [Cleanup](#cleanup)
- [Algorithm](#algorithm)
    - [Maze Generation](#maze-generation)
    - [Path Generation](#path-generation)
- [Package](#package)
    - [Usage](#usage)
    - [License](#license)
- [Resources](#resources)
    - [Maze Algorithms](#maze-algorithms)
    - [Python Libraries](#python-libraries)
    - [Reusable Modules](#reusable-modules)
    - [AI usage](#ai-usage)
- [Project Management](#project-management)

## Description

This project is a terminal application that generates and displays a maze with
a 42 logo. The user can interact with the generated maze through a simple numbered menu.

### Maze Generation
The maze is generated using one of two availabl algorithms creating a perfect maze 
and then optionally removing dead ends for braided mazes. 
The generation process of passage openings between neighbouring cells is animated in the terminal.

### Visualization
The text representation of a maze is displayed in the terminal with an interactive interface.
The application shows the current maze-generation algorithm and lets the user regenerate the
maze, change its colors, show or hide the path or switch to the other algorithm.

<table>
  <tr>
    <td align="center">
      <strong>Placeholder for program visualization</strong><br><br>
      <img src="https://placeholder" alt="placeholder"><br>
      Source: <a href="placeholder">Wikipedia</a>
    </td>
  </tr>
</table>


### Output File
The program generates an output file that consists of maze information:
- hexadecimal representation of the maze where the value informs of existing walls of each consecutive cell
- coordinates of entry and exit
- the entry -> exit path in a form of a list of directions

### Bonus Features
The project also includes the following additional features:

- Additional menu option for changing the 42 logo colors.
- Two implemented maze generation algorithms.
- Animation of the maze generation process.
- A maze without dead ends when PERFECT=False.

## Instructions
### Prerequisites
- Python 3.10 or newer
- pip installed.

### Clone the Repository
```bash
git clone git@github.com:urszkam/a-maze-ing.git
cd a-maze-ing
```

### Usage
Install the uv project manager and the project dependencies:

```bash
make install
```

This command installs the *uv* version pinned in *requirements.txt* and runs
*uv sync --locked*. It creates the virtual environment and installs dependencies
from *uv.lock*, checking that it is consistent with *pyproject.toml*.

The application can then be started with:

```bash
make run
```

The command executes 
```bash
    uv run python3 a_maze_ing.py config.txt`
```
uv run uses the project's virtual environment automatically. 
- a_maze_ing.py argument is the Python script, 
- context.txt argument is the configuration file used to create the maze.

After the maze is generated, use the displayed keys to choose an action.

#### Menu and Interactions
The application displays a numbered menu and waits for a number from **1** to
**6**. Each option performs the following action:

1. **Re-generate a new maze** - creates and displays a new maze using the
   currently selected algorithm.
2. **Show / Hide the shortest path** - toggles the visibility of the path.
3. **Rotate the wall colors** - changes the color of the maze walls.
4. **Rotate the 42 logo colors** - changes the color of the 42 logo.
5. **Change maze generator algorithm** - switches to the next available
   generation algorithm and generates a new maze.
6. **Exit** - closes the application.


### Config
The program takes the name of the config file from the project root directory.
The config consist of several mandatory and optional fields.
Mandatory fields:
- **WIDTH** (int) - number of maze rows, eg. 7
- **HEIGHT** (int) - number of maze columns, eg. 12
- **ENTRY** (tuple[int, int]) - x, y coordinates of the path start cell, eg. (11,8)
- **EXIT** (tuple[int, int]) - x, y coordinates of the path end cell, eg. (0,3)
- **OUTPUT_NAME** (str) - name of the output file where the final maze data is saved,
  eg. maze.txt

Optional fields:
- **PERFECT** (bool) - bool whether the maze should be perfect with no loops, eg. True
  (default value is False)
- **SEED** (int) - Random seed used for maze generation, eg. 123 (default value is 666)
- **ALGORITHM** (str) - name of the maze generation algorithm, either Prim or Kruskal

### Linting
Run the following command to check code style and types:

```bash
make lint
```

For stricter checks, use:

```bash
make lint-strict
```

### Cleanup
Run the following command to remove Python temporary files:

```bash
make clean
```

It removes **.mypy_cache and __pycache__** directories.

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


<table>
  <tr>
    <td align="center">
      <strong>Prim Algorithm Visualization</strong><br><br>
      <img src="https://upload.wikimedia.org/wikipedia/commons/9/9b/PrimAlgDemo.gif?utm_source=en.wikipedia.org&utm_campaign=index&utm_content=original" alt="Prim algorithm animation"><br>
      Source: <a href="https://en.wikipedia.org/wiki/File:PrimAlgDemo.gif">Wikipedia</a>
    </td>
  </tr>
</table>

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

<table>
  <tr>
    <td align="center">
      <strong>Kruskal's Algorithm Visualization</strong><br><br>
      <img src="https://upload.wikimedia.org/wikipedia/commons/b/bb/KruskalDemo.gif?utm_source=en.wikipedia.org&utm_campaign=index&utm_content=original" alt="Kruskal's algorithm animation"><br>
      Source: <a href="https://en.wikipedia.org/wiki/File:KruskalDemo.gif">Wikipedia</a>
    </td>
  </tr>
</table>

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

## Package
• What part of your code is reusable, and how
### Usage
### License

## Resources

### Maze Algorithms:
- [Maze generation algotirhms](https://www.maze-generator.net/algorithms)
- [Prim's algorithm](https://www.freecodecamp.org/news/prims-algorithm-explained-with-pseudocode/)
- [Kruskal's algorithm](https://www.programiz.com/dsa/kruskal-algorithm)
- [Kruskal's algorithm visualization](https://www.youtube.com/watch?v=8HeLu8wuLqo)
- [Braiding a maze](https://mazeprintables.com/blog/perfect-vs-braid-mazes?utm_source=chatgpt.com#braid-a-copy-without-losing-track)

### Python Libraries:
- [uv PyPI documentation](https://pypi.org/project/uv/)
- [uv configuration](https://docs.astral.sh/uv/concepts/projects/config/)
- [rich library documentation for TUI creation](https://rich.readthedocs.io/en/latest/introduction.html)
- [readchar library](https://pypi.org/project/readchar/)
- [NumPy user guide](https://numpy.org/doc/2.2/user/index.html#user)
- [Pydantic validation](https://pydantic.dev/docs/validation/latest/get-started/)

### Reusable Modules
- [Packaging Python projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Choosing a license](https://choosealicense.com/)
- [Python wheel](https://www.geeksforgeeks.org/python/what-is-a-python-wheel/)

### AI usage:
- generate list of unicode characters for maze representation

## Project Management
The project was relatively simple and short, so extensive planning was not necessary, and there was little opportunity for the initial plan to change.

At the beginning, we defined the project scope by listing all functional and non-functional requirements. We then divided the tasks from the backlog into short iterations lasting a few days each, followed by a review of the completed work.

The table below presents how the tasks were distributed between team members across the three iterations.

| Iteration | Vineet | Ula |
|---|---|---|
| **I Iteration** | Input parsing, configuration loading and validation | Basic application flow with visualization, without implementing advanced features |
| **II Iteration** | Implementation of Algorithm X for maze generation and a shortest-path finding algorithm | Implementation of Kruskal's algorithm for maze generation, a dead-end removal algorithm and animation improvements |
| **III Iteration** | Improve config loading and creation of a maze generation package | Path visualization, documentation, output generation, unit tests |
