import streamlit as st
import pandas as pd
import mysql.connector
import numpy as np

# Configuração da página
st.set_page_config(page_title="Sobre", layout="wide")
st.logo("https://igce.rc.unesp.br/images/unesp.svg")
st.title("📈 Graficos")

# Função de conexão com o banco de dados
def create_connection():
    try:
        return mysql.connector.connect(
            host='mysql-3468e67c-streamlit-lbd.e.aivencloud.com',
            user='avnadmin',
            password='AVNS_qWwT1IkX4yxrSOOfe4t',
            port=15308,
            db='defaultdb',
            auth_plugin='mysql_native_password'
        )
    except mysql.connector.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para carregar os dados das escolas
def load_escolas():
    conn = create_connection()
    if conn is None:
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro na conexão
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM view_escolas_computadores;")
    res = cursor.fetchall()
    df = pd.DataFrame(res, columns=cursor.column_names)
    cursor.close()
    conn.close()
    return df

# Função para carregar os dados das escolas com docentes
def load_escolas_localizacao_dependencia_docentes():
    conn = create_connection()
    if conn is None:
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro na conexão
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM view_escolas_localizacao_dependencia_docentes;")
    res = cursor.fetchall()
    df = pd.DataFrame(res, columns=cursor.column_names)
    cursor.close()
    conn.close()
    return df

# Carrega os dados das escolas
df = load_escolas()

# Carrega os dados das escolas com a quantidade de docentes
df_docentes = load_escolas_localizacao_dependencia_docentes()

# Exibe gráficos com os dados das escolas
if not df.empty:
    # Exibe um gráfico de barras
    # Exibe o título centralizado
    st.markdown(
        """
        <div style="text-align: center;">
            <h4>Grafico de Barras: Escola X Quantidade de Computadores</h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.line_chart(df, x="NO_ENTIDADE", y="NU_COMPUTADOR")
    st.bar_chart(df, x="NO_ENTIDADE", y="NU_COMPUTADOR", x_label="Escola", y_label="Total de computadores")

    # Exibe um gráfico de linhas com os mesmos dados 
    # Exibe o título centralizado
    st.markdown(
        """
        <div style="text-align: center;">
            <h4>Grafico de Linhas: Escola X Quantidade de Computadores</h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.line_chart(df, x="NO_ENTIDADE", y="NU_COMPUTADOR")

    # Exibe um gráfico de dispersão
    # Exibe o título centralizado
    st.markdown(
        """
        <div style="text-align: center;">
            <h4>Grafico de Dispersão: Escola X Quantidade de Computadores</h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.scatter_chart(df, x="NU_SALAS_EXISTENTES", y="NU_COMPUTADOR", x_label="Núm de salas", y_label="Total de computadores")

    # Exibe dados para mapa (gerado aleatoriamente como exemplo)
    df_map = pd.DataFrame(
        np.random.randn(100, 2) / [50, 50] + [-22.4094224, -47.5632023],
        columns=["lat", "lon"]
    )
    st.map(df_map)
else:
    st.warning("Não foi possível carregar os dados das escolas.")

# Exibe gráficos com a quantidade de docentes por escola
if not df_docentes.empty:
    # Cria a tabela pivot com apenas as colunas relevantes (nome da escola e quantidade de docentes)
    df_pivot = df_docentes[['NO_ENTIDADE', 'qt_docentes']]

    # Ordena por quantidade de docentes (opcional)
    df_pivot = df_pivot.sort_values(by='qt_docentes', ascending=False)

    # Exibe o gráfico de barras com o nome da escola e quantidade de docentes
    # Exibe o título centralizado
    st.markdown(
        """
        <div style="text-align: center;">
            <h4>Escola X Quantidade de Docentes</h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.bar_chart(df_pivot.set_index('NO_ENTIDADE')['qt_docentes'])
else:
    st.warning("Não foi possível carregar os dados das escolas com docentes.")
