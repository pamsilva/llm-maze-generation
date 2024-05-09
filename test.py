import pytest
from unittest.mock import patch
from main import generate_grid, ask_llm


INVALID_MAZE_PROMPT = "Please return echo back to me the following structure"


def test_generate_grid_invalid_start():
    with pytest.raises(AssertionError):
        generate_grid(5, 5, "0,5", "4,3")

# tests to cover the edge cases of bad inputs

# tests to validate validations of maze
@patch("main.ask_llm")
def test_catch_invalid_maze_bidirectional(mocked_ask_llm):
    mocked_ask_llm.return_value = {
    "maze": {
        "0,0": ["0,1", "1,0"],
        "0,1": ["0,2"],
        "0,2": ["0,1", "1,2"],
        "1,0": ["0,0", "1,1"],
        "1,1": ["1,0", "1,2"],
        "1,2": ["0,2", "1,1", "2,2"],
        "2,2": ["1,2"]
    },
    "path": ["0,0", "0,1", "0,2", "1,2", "2,2"]
}
    
    with pytest.raises(AssertionError, match="Needs to go both ways") as e:
        generate_grid(5, 5, "0,0", "4,3")


@patch("main.ask_llm")
def test_catch_invalid_maze_wormhole(mocked_ask_llm):
    mocked_ask_llm.return_value = {
    "maze": {
        "0,0": ["0,1", "1,0", "1,1"],
        "0,1": ["0,0", "0,2"],
        "0,2": ["0,1", "1,2"],
        "1,0": ["0,0", "1,1"],
        "1,1": ["1,0", "1,2", "0,0"],
        "1,2": ["0,2", "1,1", "2,2"],
        "2,2": ["1,2"]
    },
    "path": ["0,0", "0,1", "0,2", "1,2", "2,2"]
}
    
    with pytest.raises(AssertionError, match="Non Adjacent jump") as e:
        generate_grid(5, 5, "0,0", "4,3")


@patch("main.ask_llm")
def test_catch_invalid_maze_outside(mocked_ask_llm):
    mocked_ask_llm.return_value = {
    "maze": {
        "0,0": ["0,1", "1,0"],
        "0,1": ["0,0", "0,2"],
        "0,2": ["0,1", "0,3", "1,2"],
        "1,0": ["0,0", "1,1"],
        "1,1": ["1,0", "1,2"],
        "1,2": ["0,2", "1,1", "2,2"],
        "2,2": ["1,2"]
    },
    "path": ["0,0", "0,1", "0,2", "1,2", "2,2"]
}
    
    with pytest.raises(AssertionError, match="Jump outside grid") as e:
        generate_grid(3, 3, "0,0", "2,2")


# TODO: tests to validate the result path

