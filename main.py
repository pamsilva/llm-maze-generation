from openai import OpenAI
from dotenv import load_dotenv, dotenv_values

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

client = OpenAI()

DEFAULT_MODEL = "gpt-4"
BASE_TEMPERATURE = 0.4

BASE_PROMPT = """
Please generate a JSON structure that represents a table with {n_rows} rows and {m_columns}.
The key of the JSON structure composed of the index of the row and the column.
The value is the list of cells that you can jump from that that you can only jump to adjacent cells. Adjacent cells are the ones above (row - 1), left (column - 1), right (column + 1) and down (row +1).
Note that there cannot be a jump to outside the grid, so, the jumps need to be to cells that fall within the specified grid.
Also, if you can jump from cell "1,2" to cell "2,2" you can always jump back from cell "2,2" to cell "1,2".

Consider the cell {start_cell} as the start cell and {end_cell} as the end cell of a path that can be followed through the jumps available in the maze. This means that both start and end cells need to be part of the path that can be travaled in the cells. Make sure that they are part of the keys and that they are connected to other cells, derectly io indirectly.

Just make sure that the previous rules are fulfilled:
- if you can jump from cell "1,2" to cell "2,2" you can also jump from cell "2,2" back to cell "1,2".

This can be generated gradually by adding jumps from a cell to the adjacent cells, starting from the start_cell and until you reach the end cell position.
The jumps should always be reversible, which menas that if you can jump from cell "1,2" to cell "2,2" you can also jump from cell "2,2" back to cell "1,2". While adding a jump, make sure to add the origin cell to the possible jumps of the target cell.

The result grid should NOT be fully connected. This means that some cells will only have some or even None Jumps to adjacent cells.

Generate the JSON data with a random content, do NOT generate the code to generate the JSON structure.

As an additional reuslt, please generate a valid path from the start cell to the end cell, presented as the list of cells that would take to get from the start to end.


The structure should be as the example JSON enclosed by tripple ':
'''
{{
    "maze": {{
        "0,0": ["1,0", "0,1"],
        "1,0": ["1,1"],
        "0,1": ["0,0"],
        "1,1": ["1,0"]
    }},
    "path": ["0,0", "1,0", "1,1"]
}}
'''

The above example would be a valid result if working with a 2 by 2 grid starting at "0,0" and ending at "1,1".

Make SURE that the JSON output is valid JSON.

"""


def ask_question(question, history=None, model=None):
    model = model or DEFAULT_MODEL
    history = history or []

    prompt_object = {
        "role": "user",
        "content": question,
    }

    return client.chat.completions.create(
        model=model,
        messages=history + [prompt_object],
        temperature=BASE_TEMPERATURE
    ), prompt_object


def validate_maze(grid, rows, columns):
    for key, jumps in grid.items():
        x, y = key.split(",")
        for destination in jumps:
            jx, jy = destination.split(",")
            if not (x == jx or y == jy):
                raise AssertionError("Non Adjacent jump")

            ix, iy = map(int, [jx, jy])
            if ix < 0 or ix > rows - 1 or iy < 0 or iy > columns - 1:
                raise AssertionError("Jump outside grid")

            if key not in grid[destination]:
                raise AssertionError("Needs to go both ways")


def validate_start_end(start, end, maze):
    if start not in maze:
        raise AssertionError("start is not included in the path")

    if end not in maze:
        raise ArithmeticError("end is not included in the path")


def validate_path(maze, path, start, end):
    if len(path < 2):
        raise AssertionError("path not big enough")

    if start != path[0]:
        raise AssertionError("start not at the start position")
    
    if end != path[-1]:
        raise AssertionError("end not at the end position")

    pivot = path[0]
    if pivot not in maze:
            raise AssertionError("Invalid Path: step not in cells with jumps")

    for step in path[1:]:
        if step not in maze:
            raise AssertionError("Invalid Path: step not in cells with jumps")

        if step not in maze[pivot]:
            raise AssertionError("Invalid Path: step not connected to previous step")
        
        

def ask_llm(rows, columns, start_cell, end_cell, query):
    model = ChatOpenAI(temperature=0.4)
    parser = JsonOutputParser()

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser

    result = chain.invoke({"query": query})

    return result
    

def generate_grid(rows, columns, start_cell, end_cell):
    # TODO: validate number of rows and columns must be 2 or greater.

    sx, sy = map(int, start_cell.split(","))
    ex, ey = map(int, end_cell.split(","))
    if sx < 0 or sx > rows - 1 or sy < 0 or sy > columns - 1:
        raise AssertionError("invalid start position")
        
    if ex < 0 or ex > rows - 1 or ey < 0 or ey > columns - 1:
        raise AssertionError("invalid end position")

    ready_prompt = BASE_PROMPT.format(
        n_rows=rows,
        m_columns=columns,
        start_cell=start_cell,
        end_cell=end_cell,
    )
    result = ask_llm(rows, columns, start_cell, end_cell, ready_prompt)
    validate_maze(result["maze"], rows, columns)
    validate_start_end(start_cell, end_cell, result["maze"])
    validate_path(result["maze"], result["path"], start_cell, end_cell)

    return result


def main():
    amaze = generate_grid(3, 3, '0,0', '2, 2')
    breakpoint()
    pass


if __name__ == "__main__":
    main()
