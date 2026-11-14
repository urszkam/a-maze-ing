from src.controller import run_app
from src.service.parse_config import MazeConfig
import argparse
from pydantic import ValidationError


def main() -> None:
    """TODO placeholder.
    """
    parser = argparse.ArgumentParser(description="Parse and validate maze "
                                                 "config file using Pydantic.")
    parser.add_argument("config_file", type=str, help="Path to config file.")
    args = parser.parse_args()

    try:
        maze_config = MazeConfig.from_file(args.config_file)
        run_app(maze_config)
    except FileNotFoundError as err:
        print(f"{err}")
        raise SystemExit(1)
    except ValidationError as err:
        print("Validation Error(s):")
        for e in err.errors():
            field = f"{e['loc'][0]}: " if e['loc'] else ""
            print(f"  - {field}{e['msg']}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
