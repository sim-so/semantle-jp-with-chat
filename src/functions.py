evaluate_guess = {"name": "evaluate_guess",
                  "description": "Calculate the score of a guess word and get the rank among the 1,000 words.",
                  "parameters": {
                      "type": "object",
                      "properties": {
                          "word": {
                              "type": "string",
                              "description": "A single Japanese word, which is can be a noun, verb, adverb or adjective. e.g. 空, 近い, 行く, etc."
                              },
                          "puzzle": {
                              "type": "object",
                              "description": "A class containing information about the puzzle; a secret word and scores/ranks for other words."
                          }
                      },
                      "required": ["word", "puzzle"]
                  }}

def get_functions():
    functions = [evaluate_guess]
    return functions