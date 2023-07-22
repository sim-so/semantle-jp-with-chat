from datetime import date, datetime
from pytz import utc, timezone
import requests

def get_secret(puzzle_num: int):
    request_url = f"https://semantoru.com/yesterday/{puzzle_num+1}"
    response = requests.get(request_url)
    if response.status_code == 200:
        return response.content
    else:
        return "Not found error."

def get_guess(word: str, puzzle_num: int):
    request_url = f"https://semantoru.com/guess/{puzzle_num}/{word}"
    response = requests.get(request_url)
    print(response.status_code)
    if response.status_code == 200:
        return response.json()
    else:
        return {"guess": word, 
                "sim": None,
                "rank": None}
    
def get_puzzle_num():
    FIRST_DAY = date(2023, 4, 2)
    return (utc.localize(datetime.utcnow()).astimezone(timezone('Asia/Tokyo')).date() - FIRST_DAY).days