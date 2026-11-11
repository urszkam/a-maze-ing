WIDTH = 3

MENU = (
    "=== A-MAZE-ING ===\n"
    "1. Re-generate a new maze\n"
    "2. Show / Hide the shortest path\n"
    "3. Rotate the wall colors\n"
    "4. Rotate the 42 logo colors\n"
    "5. Change maze generator algorithm (Current algorithm: {algorithm})\n"
    "6. Exit"
)

LOGO42 = [
    [1, 0, 0, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 1],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 1, 1, 1],

]

THEME = {
    "maze.wall": "bold green",
    "maze.start": "bold green",
    "maze.end": "bold red",
    "maze.path": "bold #ffff00",
    "maze.42": "bold bright_blue",
    "maze.entry": "bright_green",
    "maze.exit": "bright_red",
    "txt.error": "red",
    "txt.header": "bold blue",
    "txt.menu": "white",
    "txt.options": "italic green"
}

WALL = {
    # Walls
    "horizontal": "━━━",
    "vertical": "┃",

    # Corners
    "top_left": "┏",
    "top_right": "┓",
    "bottom_left": "┗",
    "bottom_right": "┛",

    # Wall connectors
    "top_join": "┳",
    "bottom_join": "┻",
    "left_join": "┣",
    "right_join": "┫",
    "cross": "╋",

    # Other
    "empty": " ",
    "logo": "▒▒▒",
    "entry": "●",
    "path": "━"
}

COLORS = [
    "red",
    "green",
    "#ff10f0",
    "yellow",
    "magenta",
    "#00ffff",
    "white",
    "black",
    "#ff5f00",
    "hot_pink",
    "bright_blue"
]
