import streamlit as st
import pandas as pd
import openai
import json
import os

openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]

prompt = """请随机{0}组数据，每组数据描述如下
随机{1}个不重复且小于等于35的前区数字并按从小到大排序，再随机{2}个不重复且小于等于12的后区数字并按从小到大排序

请以json数组格式返回，其中字段前区1代表前区的第一个数字，前区2代表前区的第二个数字，后区1代表后区的第一个数字，后区2代表后区的第二个数字
"""


st.set_page_config(page_title="大乐透AI生成器")
# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """

# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)

def generate():
    if st.session_state.n_requests >= 5:
        if pd.Timestamp.now().day == st.session_state.last_access.day:
            st.session_state.text_error = "今天的次数已经用完了，明天再来吧"
            return
        else:
            st.session_state.n_requests = 0

    with spinner_placeholder:
        with st.spinner("AI生成中..."):
            st.session_state.text_error = ""
            st.session_state.n_requests += 1
            st.session_state.last_access = pd.Timestamp.now()
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt.format(number_of_groups, anterior, posterior),
                temperature=0.5,
                max_tokens=512
            )
            data = response.choices[0].text
            st.session_state.data = data

if "data" not in st.session_state:
    st.session_state.data = ""
if "n_requests" not in st.session_state:
    st.session_state.n_requests = 0
if "text_error" not in st.session_state:
    st.session_state.text_error = ""
if "last_access" not in st.session_state:
    st.session_state.last_access = None




st.write('# 大乐透AI生成器')

anterior = st.selectbox('前区', [5, 6, 7])
posterior = st.selectbox('后区', [2, 3])
number_of_groups = st.selectbox('串数', [1, 3])
submit_btn = st.button('点我暴富', on_click=generate)

# st.write('## prompt')
# st.write(prompt.format(number_of_groups, anterior, posterior))

spinner_placeholder = st.empty()

if st.session_state.text_error:
    st.write(st.session_state.text_error)
else:
    st.write(f"您今天还有{5 - st.session_state.n_requests}次暴富机会")

if st.session_state.data:
    data = st.session_state.data
    df = pd.DataFrame(json.loads(data))
    st.table(df)
