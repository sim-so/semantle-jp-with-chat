def add_guess(guess_result, play):
    word, sim, rank = guess_result
    if sim:
        if word not in play.guessed:
            sim = round(sim, 2)
            rank = "情報なし" if rank == 1001 else rank
            play.guesses.loc[len(play.guessed)] = ([len(play.guessed), word, sim, rank])
            play.guessed.add(word)
        cur_result = format_result(word, sim, rank)
    else:
        cur_result =  "不正解: 正しくない単語"
    return "\n".join([cur_result, "最高スコア:", format_table(play.guesses)])

def format_result(word, sim, rank):
    return f"{word}: スコア {sim}, ランク {rank}"

def format_table(table, n_rows=10):
    top_results = table.sort_values(by="スコア", ascending=False).head(n_rows)
    return top_results.to_markdown(index=False)