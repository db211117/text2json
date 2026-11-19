import streamlit as st
import os
import sqlite3
import json
from dotenv import load_dotenv
from openai import OpenAI
st.title("文本智能提取工具")
st.write("输入一段文本,AI将自动提取情绪、紧急度和总结。")
load_dotenv()
client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"),base_url=os.getenv("BASE_URL"))
user_input=st.text_area("请输入要分析的文本:",height=150)
st.write(f"当前输入了{len(user_input)}个字")
if st.button("开始分析"):
    if user_input=="":
        st.warning("请先输入文本哦！")
    else:
        with st.spinner("AI正在思考中..."):
            prompt=f"""
            请分析下面这段文本,并严格按JSON格式输出。
            只能输出JSON,不要输出任何其他解释文字。
            JSON必须包括以下字段:
            -"sentiment":情绪(之恩那个是positiive,neutral,negative三种之一)
            -"topics"提到的主题列表（如["价格","客服"])
            -"urgency":紧急程度(只能是high,medium,low三种之一)
            -"summary":一句话总结
            文本内容:{user_input}
            """
            resp=client.chat.completions.create(model="deepseek-chat",messages=[{"role":"user","content":prompt}],temperature=0)
            ai_reply=resp.choices[0].message.content
            data=json.loads(ai_reply)
            st.success("分析完成！")
            col1,col2=st.columns(2)
            col1.metric("情绪",data['sentiment'])
            col2.metric("紧急度",data['urgency'])
            st.write("**总结:**",data['summary'])
            st.write("**主题:**",",".join(data['topics']))
            with st.expander("查看原始 JSON数据"):
                st.json(data)
st.sidebar.header("历史分析记录")
conn=sqlite3.connect("db/results.db")
import pandas as pd
df=pd.read_sql_query("SELECT*FROM results",conn)
conn.close()
st.sidebar.dataframe(df)