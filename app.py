import streamlit as st
import mysql.connector
import pandas as pd

st.header("Primeiro titulo")

st.markdown("""
            Primeira **linha** *aqui*
            """)

conn = mysql.connector.connect(host='sql.freedb.tech', 
                               user='freedb_freedb-user', 
                               password='*dtvFHJ7hDq%7&G', 
                               port=3306, 
                               db='freedb_escola-db', 
                               auth_plugin='mysql_native_password')

cursor = conn.cursor()

cursor.execute("select * from escolas;")
res = cursor.fetchall()
df = pd.DataFrame(res, columns=cursor.column_names)

st.write(df)

st.sidebar.header("Meu Sidebar")
st.sidebar.radio("Meu Radio", df['NO_ENTIDADE'].unique())
