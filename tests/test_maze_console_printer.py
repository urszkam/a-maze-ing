import numpy as np
import pytest

from src.constants import COLORS, Dir, WALL
from src.controller.console_printer import ConsolePrinter, MazeText


@pytest.mark.parametrize(
    "direction, expected",
    [
        (Dir.N, "┏━━━┓"),
        (Dir.S, "┗━━━┛"),
        (Dir.W, "┃"),
        (Dir.E, "┃"),
    ],
)
def test_closed_cell_walls(direction: Dir, expected: str) -> None:
    maze = np.array([[15]])

    assert MazeText.get_wall_text(direction, 0, 0, maze) == expected


@pytest.mark.parametrize("direction", [Dir.W, Dir.E])
def test_open_cell_no_walls(direction: Dir) -> None:
    maze = np.array([[0]])

    assert MazeText.get_wall_text(direction, 0, 0, maze) == " "


@pytest.mark.parametrize(
    "direction, row, col, expected",
    [
        (Dir.N, 0, 0, "┏━━━"),
        (Dir.N, 0, 2, "┳━━━┓"),
        (Dir.N, 0, 1, "━━━━"),
        (Dir.S, 1, 2,  "┻━━━┛"),
        (Dir.S, 1, 0,  "┗━━━"),
        (Dir.S, 0, 0,  "┣━━━"),
        (Dir.W, 1, 0, "┃"),
        (Dir.E, 1, 1, "┃"),
        (Dir.E, 0, 0, " "),
    ],
)
def test_get_wall_text(
    direction: Dir, row: int, col: int, expected: str,
) -> None:
    maze = np.array([[13, 3, 15], [13, 6, 15]])

    assert MazeText.get_wall_text(direction, row, col, maze) == expected


@pytest.mark.parametrize(
    "bitmask, expected",
    [
        (None, (" ", " ", " ")),
        (Dir.E | Dir.W, ("━", "━", "━")),
        (Dir.N | Dir.S, (" ", "┃", " ")),
        (Dir.N | Dir.E, (" ", "┗", "━")),
        (Dir.S | Dir.W, ("━", "┓", " ")),
    ],
)
def test_path_characters(
    bitmask: int | None, expected: tuple[str, str, str],
) -> None:
    assert MazeText.get_path_text(bitmask) == expected


def test_append_wall() -> None:
    text = MazeText()

    text.append_wall("┏━━━┓")

    assert text.plain == "┏━━━┓"
    assert text.spans[0].style == "maze.wall"


def test_appended_path() -> None:
    text = MazeText()
    text.append_path(WALL["path"])

    assert text.plain == WALL["path"]
    assert text.spans[0].style == "maze.path"


def test_append_empty() -> None:
    text = MazeText()
    text.append_empty(3)

    assert text.plain == WALL["empty"] * 3


def test_append_newline() -> None:
    text = MazeText()
    text.append_nl()

    assert text.plain == "\n"


@pytest.fixture
def printer(monkeypatch: pytest.MonkeyPatch) -> ConsolePrinter:
    monkeypatch.setattr(ConsolePrinter, "_instance", None)
    return ConsolePrinter()


def test_error_message(printer: ConsolePrinter) -> None:
    with printer.capture() as output:
        printer.error("Error message")

    assert output.get() == "Error message\n"


def test_update_wall_color(printer: ConsolePrinter) -> None:
    color = printer._theme.styles["maze.wall"].color
    printer.update_wall_color()

    updated_color = printer._theme.styles["maze.wall"].color

    assert color != updated_color
    assert color is not None and color.name in COLORS
    assert updated_color is not None and updated_color.name in COLORS


def test_update_logo_color(printer: ConsolePrinter) -> None:
    color = printer._theme.styles["maze.42"].color
    printer.update_42_color()

    updated_color = printer._theme.styles["maze.42"].color

    assert color != updated_color
    assert color is not None and color.name in COLORS
    assert updated_color is not None and updated_color.name in COLORS


def test_toggle_path_visibility(printer: ConsolePrinter) -> None:
    assert printer.show_hide_path() is True
    assert printer._theme.styles["maze.path"].conceal is True

    assert printer.show_hide_path() is False
    assert printer._theme.styles["maze.path"].conceal is False


def test_set_path_visibility(printer: ConsolePrinter) -> None:
    printer.show_hide_path(visible=False)
    printer.show_hide_path(visible=False)
    assert printer._theme.styles["maze.path"].conceal is True

    printer.show_hide_path(visible=True)
    assert printer._theme.styles["maze.path"].conceal is False
