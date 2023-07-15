import pickle
from typing import Tuple, List, Dict

class Puzzle:
    secret: str = ""
    nearests: Dict = dict()
    nearests_words: List = list()

def get_puzzle(puzzle_num: int):
    puzzle = Puzzle()
    with open(f'example/{puzzle_num}.dat', 'rb') as f:
        puzzle.nearests, _ = pickle.load(f)
    puzzle.nearests_words = [word for word in puzzle.nearests.keys()]
    puzzle.secret = puzzle.nearests_words[0]
    return puzzle

def evaluate_guess(word: str, puzzle):
    rtn = {"guess": word, "sim": None, "rank": None}
    # check most similar
    if word in puzzle.nearests:
        rtn["sim"] = puzzle.nearests[word][1]
        rtn["rank"] = puzzle.nearests[word][0]
    return rtn