import streamlit as st
import mysql.connector
import pandas as pd

# Configuração de cabeçalho da página
st.set_page_config(page_title="Escolas e Dados", layout="wide")
st.title("Análise de Escolas")

# Conexão com o banco de dados
def create_connection():
    return mysql.connector.connect(
        host='sql.freedb.tech',
        user='freedb_freedb-user',
        password='*dtvFHJ7hDq%7&G',
        port=3306,
        db='freedb_escola-db',
        auth_plugin='mysql_native_password'
    )

# Função para executar consulta SQL e retornar um DataFrame
def execute_query(query):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=cursor.column_names)
    cursor.close()
    conn.close()
    return df

# Exibição de escolas
st.subheader("Informações das Escolas")
escolas_query = """
    SELECT 
        e.NO_ENTIDADE, 
        e.TP_SITUACAO_FUNCIONAMENTO, 
        e.CO_MUNICIPIO, 
        e.TP_LOCALIZACAO, 
        e.TP_DEPENDENCIA 
    FROM 
        escolas e
"""
df_escolas = execute_query(escolas_query)
st.dataframe(df_escolas, use_container_width=True)

# Totais de matrículas, professores e turmas
st.subheader("Totais de Matrículas, Professores e Turmas por Escola")
totais_query = """
    SELECT 
        e.NO_ENTIDADE, 
        COUNT(DISTINCT m.ID_MATRICULA) AS Total_Alunos, 
        COUNT(DISTINCT d.CO_PESSOA_FISICA) AS Total_Professores
    FROM 
        escolas e
    LEFT JOIN 
        matriculas m ON e.CO_ENTIDADE = m.CO_ENTIDADE
    LEFT JOIN 
        docentes d ON e.CO_ENTIDADE = d.CO_ENTIDADE
    GROUP BY 
        e.NO_ENTIDADE, e.CO_ENTIDADE
    ORDER BY 
        e.NO_ENTIDADE ASC;
"""
df_totais = execute_query(totais_query)
st.dataframe(df_totais, use_container_width=True)
