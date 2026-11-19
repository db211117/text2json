import os
import json
import csv
import sqlite3
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"),base_url=os.getenv("BASE_URL"))
db_path="db/results.db"
conn=sqlite3.connect(db_path)
cursor=conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS results(id INTEGER PRIMARY KEY AUTOINCREMENT,input_text TEXT,sentiment TEXT,urgency TEXT,summary TEXT)''')
conn.commit()
def call_ai(text):
    prompt=f"""
    请分析下面这段文本,并严格按JSON格式输出。
    只能输出JSON,不要输出任何其他解释文字。
    JSON必须包括以下字段:
    -"sentiment":情绪(之恩那个是positiive,neutral,negative三种之一)
    -"topics"提到的主题列表（如["价格","客服"])
    -"urgency":紧急程度(只能是high,medium,low三种之一)
    -"summary":一句话总结
    文本内容:{test_text}
    """
    resp=client.chat.completions.create(model="deepseek-chat",messages=[{"role":"user","content":prompt}],temperature=0)
    ai_reply=resp.choices[0].message.content
    data=json.loads(ai_reply)
    return data
file_path="data/samples.csv"
print(f"开始处理文件{file_path}...\n")
with open(file_path,mode='r',encoding='utf-8')as file:
    reader=csv.DictReader(file)
    for row in reader:
        test_text=row["input_text"]
        print(f"正在处理文本:{test_text}")
        cursor.execute("SELECT id FROM results WHERE input_text=?",(test_text,))
        existing_data=cursor.fetchone()
        if existing_data is not None:
            print("跳过:数据库中已存在该条数据.\n")
            continue
        try:
            data=call_ai(test_text)
            cursor.execute('''INSERT INTO results(input_text,sentiment,urgency,summary)VALUES(?,?,?,?)''',(test_text,data['sentiment'],data['urgency'],data['summary']))
            conn.commit()
            print(f"情绪:{data['sentiment']}|紧急度:{data['urgency']}(已存入数据库)\n")
        except Exception as e:
            print(f"处理失败:{e}\n")
print("所有文本处理完毕") 
sql_query="SELECT sentiment,COUNT(*)FROM results GROUP BY sentiment;"
cursor.execute(sql_query)
results=cursor.fetchall()
print("===情绪分布统计===")
for row in results:
    print(f"情绪类型:{row[0]}|数量:{row[1]}条")
    print("-"*20)
conn.close()