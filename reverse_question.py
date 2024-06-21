# 以下を「app.py」に書き込み
import streamlit as st
import openai

import os
# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
os.environ["OPENAI_API_KEY"] = st.secrets.OpenAIAPI.openai_api_key

def generate_response(prompt):
    response = openai.Completion.create(
        engine="gpt-4",
        prompt=prompt,
        max_tokens=512
    )
    return response.choices[0].text.strip()

def ask_reverse_questions(question):
    # 逆質問を生成するためのプロンプト
    reverse_prompt = f"ユーザからの質問: {question}\nこの質問の詳細を理解するために逆質問を2つ作成してください。"
    reverse_response = generate_response(reverse_prompt)
    reverse_questions = reverse_response.split("\n")
    return reverse_questions


st.title("プラスチックQAシステム")

# ユーザからの質問を入力
user_question = st.text_input("質問を入力してください:")

if user_question:
    # 逆質問を生成
    reverse_questions = ask_reverse_questions(user_question)

    if len(reverse_questions) >= 2:
        # 逆質問を表示し、ユーザの回答を取得
        reverse_answer1 = st.text_input(f"逆質問1: {reverse_questions[0]}")
        reverse_answer2 = st.text_input(f"逆質問2: {reverse_questions[1]}")

        if reverse_answer1 and reverse_answer2:
            # ユーザの回答を踏まえた最終回答を生成
            final_prompt = f"ユーザからの質問: {user_question}\n逆質問1: {reverse_questions[0]}\n逆質問2: {reverse_questions[1]}\n逆質問1へのユーザの回答: {reverse_answer1}\n逆質問2へのユーザの回答: {reverse_answer2}\nこれらの情報を基にユーザの質問に答えてください。"
            final_answer = generate_response(final_prompt)
            st.write("回答:")
            st.write(final_answer)
    else:
        st.write("逆質問を生成できませんでした。もう一度試してください。")


