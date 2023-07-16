import requests

def get_secret(puzzle_num: int):
    request_url = f"https://semantoru.com/yesterday/{puzzle_num+1}"
    response = requests.get(request_url)
    if response.status_code == 200:
        return response.content
    else:
        print("Not found error.")

def get_guess(word: str, puzzle_num: int):
    request_url = f"https://semantoru.com/guess/{puzzle_num}/{word}"
    response = requests.get(request_url)
    print(response.status_code)
    if response.status_code == 200:
        output = response.json()
        return output["guess"], output["sim"], output["rank"]
    else:
        return word, None, None