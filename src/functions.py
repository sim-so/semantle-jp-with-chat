guess_word = {"name": "guess_word",
                  "description": "Use this function to check if a guessed word is the correct answer or not, and if incorrect, calculate a score and a rank of the guess word.",
                  "parameters": {
                      "type": "object",
                      "properties": {
                          "word": {
                              "type": "string",
                              "description": "A single Japanese word to guess, which is can be a noun, verb, adverb or adjective. e.g. 空, 近い, 行く, etc."
                              },
                          "puzzle_num": {
                              "type": "integer",
                              "description": "An index indicating today's puzzle."
                          }
                      },
                      "required": ["word", "puzzle_num"]
                  }}

prepare_hint = {"name": "prepare_hint",
                "description": "Use this function to retrieve information for hint.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "puzzle_num": {
                            "type": "interger",
                            "description": "An index for today's puzzle set."
                        }
                    },
                    "required": ["puzzle_num"]
                }}

get_secret = {"name": "get_secret",
                "description": "You can check what the correct answer of today's puzzle is by this function.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "puzzle_num": {
                            "type": "integer",
                            "description": "An index indicating today's puzzle."
                        }
                    },
                    "required": ["puzzle_num"]
                }}

get_puzzle_num = {"name": "get_puzzle_num",
                  "description": "Use this function to check today's puzzle number.",
                  "parameters": {
                      "type": "object",
                      "properties": {}
                  },
                  }

update_history = {"name": "update_history",
                  "description": "Use this function to add current guess to a table for a user's guess history.",
                  "parameters": {
                      "type": "object",
                      "properties": {
                          "current_guess": {
                              "type": "json",
                              "description": "A currently guessed word and its score and rank."
                          },
                          "guess_history": {
                              "type": "object",
                              "description": "A dataframe containing the guessed words and its xore and rank in a row."
                          }
                      },
                      "required": ["current_guess", "guess_history"]
                  }}


def get_functions():
    functions = [guess_word]
    return functions