import streamlit as st
import mysql.connector
import pandas as pd

st.header("Primeiro titulo")

st.markdown("""
            Primeira **linha** *aqui*
            """)

conn = mysql.connector.connect(host='localhost', user='root', password='aluno', port=3306, db='banco_escola', auth_plugin='mysql_native_password')

cursor = conn.cursor()

cursor.execute("select * from escolas;")
res = cursor.fetchall()
df = pd.DataFrame(res, columns=cursor.column_names)

st.write(df)

st.sidebar.header("Meu Sidebar")
st.sidebar.radio("Meu Radio", df['NO_ENTIDADE'].unique())
