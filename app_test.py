import time

import pandas as pd
import gradio as gr
import openai


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
            idx = gr.State(value=0)
            guessed = gr.State(value=set())
            guesses = gr.State(value=list())
            cur_guess = gr.State()
            cur_guess_view = gr.Textbox(
                interactive=False,
                elem_id="cur-guess-view",
                show_label=False,
            )
            guesses_table = gr.DataFrame(
                value=pd.DataFrame(columns=["#", "答え", "スコア", "ランク"]),
                headers=["#", "答え", "スコア", "ランク"],
                datatype=["number", "str", "number", "str"],
                elem_id="guesses-table",
                interactive=False
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
        
        def respond(key, user_input, chat_history, cur):
            reply = {"content": ["tesT", 0.9, 1]}
            # reply = {"content": "hint"}
            if isinstance(reply["content"], list):
                cur = reply["content"]
                cur_view = " | ".join([str(_) for _ in cur])
                reply = {"content": "updated"}
            chat_history.append((user_input, reply["content"]))
            time.sleep(2)
            return "", chat_history, cur, cur_view
        
        def update_guesses(cur, i, guessed_words, guesses_df):
            print(cur)
            if cur[2] not in guessed_words:
                guessed_words.add(cur[0])
                guesses_df.loc[i] = [i] + cur
                i += 1
                print(guesses_df)
                guesses_df = guesses_df.sort_values(by=["スコア"], ascending=False)
            return i, guessed_words, guesses_df

        api_key.change(unfreeze, [], [msg]).then(greet, [], [msg, chatbot])
        msg.submit(respond, [api_key, msg, chatbot, cur_guess], [msg, chatbot, cur_guess, cur_guess_view])
        cur_guess_view.change(update_guesses, [cur_guess, idx, guessed, guesses_table], [idx, guessed, guesses_table])
            
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