import os
import time
import json
import random

import pandas as pd
import gradio as gr
import openai

from src.semantle import get_puzzle, evaluate_guess
from src.functions import get_functions

GPT_MODEL = "gpt-3.5-turbo"
TITLE = "やりとりSemantle"
puzzle_numbers = [88]
puzzle = get_puzzle(random.choice(puzzle_numbers))
print(puzzle.secret)

guesses = pd.DataFrame.from_dict({"order":[], "guess":[], "sim":[], "rank":[]})

system_content_prefix = """今がら言葉ゲーム始めます。ユーザーが正解を答えるようにチャレンジする間、進行を手伝うのが役割です。

まず、"""
system_content=f"""ユーザーからの話を聞いて、答えるのか、ヒントを欲しがっているのか、やめようといるのかを判断してください。
ユーザーが答えする場合、答えの点数を評価しておく。その後、{guesses}がら今まで答えた結果の流れを見て、状況を一言で話してください。
ユーザーがヒントを欲しがっている場合、正解の「{puzzle.secret}」に関する間接的な情報を提供してください。
ユーザーが正解を聞いたりやめると言いたりする場合、やめてもいいかをもう一度確認してください。

ゲームのルール：
正解は一つの言葉で決めている。ユーザーはどんな言葉が正解か推測して、単語を一つずつ答えする。
正解を出すと成功としてゲームが終わる。推測した言葉がハズレだったら、推測したのが正解とどのぐらい近いかをヒントとしてもらえる。

ゲームと関係ない話は答えないでください。
"""
system_message = [{"role": "system", "content": system_content_prefix+system_content}]
chat_messages = []

def add_guess(guess_result):
    if guess_result["rank"] == " 正解！":
        return "正解です。"
    if guess_result["sim"]:
        guesses.loc[guesses.shape[0]] = [guesses.shape[0]] + [v for v in guess_result.values()]
        print(guesses.head())
        return guesses.to_json()
    else:
        return "1,000以内に入っていないようです。"

def create_chat(user_input, chat_history, api_key):
    openai.api_key = api_key
    user_content = [{"role": "user", "content": user_input}]
    chat_messages.extend(user_content)
    response = openai.ChatCompletion.create(
        model=GPT_MODEL,
        messages=system_message+chat_messages,
        functions=get_functions()
    )
    response_message = response.choices[0].message

    # Step 2: check if CPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "evaluate_guess": evaluate_guess,
        }
        function_name = response_message["function_call"]["name"]
        function_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = function_to_call(
            word=function_args.get("word"),
            puzzle=puzzle
        )
        guess_result = add_guess(function_response)
        # Step 4: send the info on the function call and function response to GPT
        chat_messages.append(response_message.to_dict()) # extend conversation with assistant's reply
        chat_messages.append(
            {"role": "function",
             "name": function_name,
             "content": guess_result}
        )   # extend conversation with function response
        second_response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=system_message+chat_messages,
        )   # get a new response from GPT where it can se the function response
        return second_response["choices"][0]["message"].to_dict()
    
    chat_messages.append(response_message.to_dict())
    return response_message.to_dict()

with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown(
            """
            # やりとりSemantle
            [semantle日本語版](https://semantoru.com/)をchatbotと楽しめるためのspaceです。
            ## ゲームのやり方
            - 正解は一つの単語で、これを答えるとゲームの勝利になります。
            - 推測した単語が正解じゃない場合、類似度スコアと順位が表示されます。それは正解を推測する大事なヒントになります。
            ## chatbotの仕事
            - 単語のスコアとランク以外に他のヒントがもらえます。
            - ゲームに関して困っている時、何か質問してみてください。
            """
        )

    with gr.Row():
        with gr.Column():
            api_key = gr.Textbox(placeholder="sk-...", label="OPENAI_API_KEY", value=None, type="password")
            guesses_table = gr.DataFrame(
                value=guesses,
                headers=["#", "答え", "スコア", "ランク"],
                datatype=["number", "str", "str", "str"],
                elem_id="guesses-table"
            )
        with gr.Column(elem_id="chat_container"):
            msg = gr.Textbox(
                placeholder="ゲームをするため、まずはAPI KEYを入れてください。",
                label="答え",
                interactive=False,
                max_lines=1
            )
            chatbot = gr.Chatbot(elem_id="chatbot")

        def unfreeze():
            return msg.update(interactive=True, placeholder="正解と思う言葉を答えてください。")
        def greet():
            return "", [("[START]", "ゲームを始まります！好きな言葉をひとつだけいってみてください。")]
        
        def respond(user_input, chat_history, api_key):
            reply = create_chat(user_input, chat_history, api_key)
            chat_history.append((user_input, reply["content"]))
            time.sleep(2)
            return "", chat_history
        def update_guesses():
            return guesses_table.update(value=guesses)

        api_key.change(unfreeze, [], [msg]).then(greet, [], [msg, chatbot])
        msg.submit(respond, [msg, chatbot, api_key], [msg, chatbot]).then(update_guesses, [], [guesses_table])
                           

    gr.Examples(
        [
            [puzzle.nearests_words[-1]],
            ["どんなヒントが貰える？"],
            ["正解と「近い」とはどういう意味？"],
            ["何から始めたらいい？"],
            ["今日の正解は何？"],
        ],
        inputs=msg,
        label="こちらから選んで話すこともできます."
    )

if __name__ == "__main__":
    demo.queue(concurrency_count=20).launch()