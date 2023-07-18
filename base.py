from typing import List

class Tool:
    description: str = ""
    name: str = ""

    inputs: List[str] = ""
    outputs: List[str] = ""

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        args = [arg for arg in args]
        kwargs = {k: v for k, v in kwargs.items()}

    