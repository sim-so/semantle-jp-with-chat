import time
import json
from datetime import date, datetime
from pytz import utc, timezone

import pandas as pd
import gradio as gr
import openai

from src.semantle import get_guess, get_secret
from src.functions import get_functions
from src.utils import add_guess

GPT_MODEL = "gpt-3.5-turbo"
TITLE = "やりとりSemantle"

task_background = f"""今から言葉をします。ユーザがゲームすることを手伝ってください。

"""
task_description=f"""まず、ユーザーからの話を聞いて、答えるのか、ヒントを欲しがっているのか、やめようといるのかを判断してください。
ユーザーが答えする場合、答えの点数を評価してください。そのあと結果を一言に要約してください。
ユーザーがヒントを欲しがっている場合、正解に関する間接的な情報を提供してください。
ユーザーが正解を聞いたりやめると言いたりする場合、やめてもいいかをもう一度確認してください。
そのほか話は答えないでください。

ゲームのルール：
正解は一つの言葉である。ユーザーはどんな言葉が正解か推測して、単語を一つずつ答えする。答えた単語のスコアが100点で、正解と一致すると成功としてゲームが終わる。
"""

# guessed = set()
# guesses = pd.DataFrame(columns=["#", "答え", "スコア", "ランク"])

system_content = task_background+task_description
system_message = [{"role": "system", "content": system_content}]
chat_history = []
n_history = 8

def update_guess(guess_result, guessed_words, guesses_df):
    result, guessed, guesses = add_guess(guess_result, guessed_words, guesses_df)
    return result

def create_chat(user_input, chat_history, api_key):
    openai.api_key = api_key
    chat_messages = [{"role": "user", "content": user_input}]
    response = openai.ChatCompletion.create(
        model=GPT_MODEL,
        messages=system_message+chat_history+chat_messages,
        functions=get_functions()
    )
    response_message = response.choices[0].message

    # Step 2: check if CPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "evaluate_guess": get_guess,
        }
        function_name = response_message["function_call"]["name"]
        function_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = function_to_call(
            word=function_args.get("word"),
            puzzle_num=puzzle_num
        )
        guess_result = update_guess(function_response, guessed, guesses)
        print(guess_result)
        # Step 4: send the info on the function call and function response to GPT
        chat_messages.append(response_message.to_dict()) # extend conversation with assistant's reply
        chat_messages.append(
            {"role": "function",
             "name": function_name,
             "content": guess_result}
        )   # extend conversation with function response
        second_response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=system_message+chat_history+chat_messages,
        )   # get a new response from GPT where it can se the function response
        chat_messages.append(second_response["choices"][0]["message"].to_dict())
        chat_history = chat_history[-8:] + chat_messages
        return chat_messages[-1]
    
    chat_messages.append(response_message.to_dict())
    chat_history = chat_history[-8:] + chat_messages
    return chat_messages[-1]

with gr.Blocks() as demo:
    
    FIRST_DAY = date(2023, 4, 2)
    puzzle_num = (utc.localize(datetime.utcnow()).astimezone(timezone('Asia/Tokyo')).date() - FIRST_DAY).days
    secret = get_secret(puzzle_num)

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
            idx = gr.State(value=1)
            guessed = gr.State(value=set())
            guesses = gr.State(value=list())
            cur_guess_table = gr.DataFrame(
                value=[],
                elem_id="cur-guesses-table"
            )
            guesses_table = gr.DataFrame(
                value=[],
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
        
        def respond(user_input, chatbot, api_key):
            reply = create_chat(user_input, chat_history, api_key)
            chatbot.append((user_input, reply["content"]))
            time.sleep(2)
            return "", chatbot
        def update_guesses(i, guessed_words, guess_history):
            i += 1
            guessed_words.add()
            return guesses_table.update(value=guess_history)

        api_key.change(unfreeze, [], [msg]).then(greet, [], [msg, chatbot])
        msg.submit(respond, [msg, chatbot, api_key], [msg, chatbot]
                   ).then(update_guesses, [idx, guessed, guesses], [idx, guessed, guesses, cur_guess_table])
            
    gr.Examples(
        [
            ["猫"],
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