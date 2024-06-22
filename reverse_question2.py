import streamlit as st
from openai import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

import os
# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
os.environ["OPENAI_API_KEY"] = st.secrets.OpenAIAPI.openai_api_key

# LLMの初期化
llm = ChatOpenAI(model="gpt-4o")

def generate_reverse_questions_chain(user_question):
    # 逆質問生成のためのプロンプトテンプレート
    reverse_question_template = PromptTemplate(
        input_variables=["question"],
        template="ユーザからの質問: {question}\nこの質問の詳細を理解するために逆質問を2つ作成してください。" +
                 "逆質問は必ず2つ作成してください。" + "逆質問以外のテキストは出力しないでください。"
    )

    reverse_chain = LLMChain(llm=llm, prompt=reverse_question_template)
    return reverse_chain.run({"question": user_question})

def generate_final_answer_chain(user_question, reverse_questions, answers):
    # 最終回答生成のためのプロンプトテンプレート
    final_answer_template = PromptTemplate(
        input_variables=["user_question", "reverse_question1", "reverse_question2", "answer1", "answer2"],
        template=(
            "ユーザからの質問: {user_question}\n"
            "逆質問1: {reverse_question1}\n"
            "逆質問2: {reverse_question2}\n"
            "逆質問1へのユーザの回答: {answer1}\n"
            "逆質問2へのユーザの回答: {answer2}\n"
            "これらの情報を基にユーザの質問に答えてください。"
        )
    )

    final_answer_chain = LLMChain(llm=llm, prompt=final_answer_template)
    return final_answer_chain.run({
        "user_question": user_question,
        "reverse_question1": reverse_questions[0],
        "reverse_question2": reverse_questions[1],
        "answer1": answers[0],
        "answer2": answers[1]
    })


st.title("プラスチック Ｑ＆Ａ")
st.write("gpt-4oを使ったチャットボット　―質問返し―")

if "user_question" not in st.session_state:
    st.session_state.user_question = ""
if "reverse_questions" not in st.session_state:
    st.session_state.reverse_questions = []
if "reverse_answer1" not in st.session_state:
    st.session_state.reverse_answer1 = ""
if "reverse_answer2" not in st.session_state:
    st.session_state.reverse_answer2 = ""

# ユーザからの質問を入力
user_question = st.text_input("質問を入力してください:", key="user_question")

if user_question and user_question != st.session_state.user_question:
    # 新しい質問が入力された場合
    st.session_state.user_question = user_question
    st.session_state.reverse_questions = generate_reverse_questions_chain(user_question).split("\n")
    st.session_state.reverse_answer1 = ""
    st.session_state.reverse_answer2 = ""

if len(st.session_state.reverse_questions) >= 2:
    # 逆質問を表示し、ユーザの回答を取得
    reverse_answer1 = st.text_input(f"逆質問 {st.session_state.reverse_questions[0]}", key="reverse_answer1")
    reverse_answer2 = st.text_input(f"逆質問 {st.session_state.reverse_questions[1]}", key="reverse_answer2")

    if reverse_answer1 and reverse_answer2:
        st.session_state.reverse_answer1 = reverse_answer1
        st.session_state.reverse_answer2 = reverse_answer2
        # ユーザの回答を踏まえた最終回答を生成
        final_answer = generate_final_answer_chain(
                st.session_state.user_question, 
                st.session_state.reverse_questions, 
                [st.session_state.reverse_answer1, st.session_state.reverse_answer2])
        st.write("回答:")
        st.write(final_answer)

        # セッションステートの変数をリセット
        st.session_state.user_question = ""
        st.session_state.reverse_questions = []
        st.session_state.reverse_answer1 = ""
        st.session_state.reverse_answer2 = ""
        
    else:
        st.write("逆質問を生成できませんでした。もう一度試してください。")
