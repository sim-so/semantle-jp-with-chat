evaluate_guess = {"name": "evaluate_guess",
                  "description": "Calculate the score of a guess word and get the rank among the 1,000 words.",
                  "parameters": {
                      "type": "object",
                      "properties": {
                          "word": {
                              "type": "string",
                              "description": "A word, noun, verb, adverb or adjective. e.g. 空, 近い, 行く, etc."
                              },
                          "puzzle": {
                              "type": "object",
                              "description": "A puzzle data containing scores and ranks of words."
                          }
                      },
                      "required": ["word", "puzzle"]
                  }}

def get_functions():
    functions = [evaluate_guess]
    return functions