import streamlit as st
import mysql.connector
import pandas as pd
import hashlib
import random
import numpy as np

# Configuração da página
st.set_page_config(page_title="Gerenciamento de Aplicação", layout="wide")
st.title("Gerenciamento da Aplicação")

# Conexão com o banco de dados
def create_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        port=3306,
        db='freedb_escola-db',
        auth_plugin='mysql_native_password'
    )

# Função para executar consulta SQL e retornar um DataFrame
def execute_query(query, params=None):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(query, params if params else ())
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=cursor.column_names)
    cursor.close()
    conn.close()
    return df

# Função para executar comandos de escrita no banco
def execute_write(query, params):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close()

# Página de gerenciamento
def gerenciamento():
    st.sidebar.subheader("Menu de Gerenciamento")
    menu = st.sidebar.radio("Escolha uma opção", ["Login", "Registrar Usuário", "Escolas Favoritas", "Exportar Dados"])

    # Login
    if menu == "Login":
        st.subheader("Login de Usuário Gerencial")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            query = "SELECT * FROM usuario WHERE email = %s AND senha = %s"
            result = execute_query(query, (email, senha))
            if not result.empty:
                st.success(f"Bem-vindo(a), {result['nome'][0]}!")
                st.session_state["logged_in"] = True
                st.session_state["id_usuario"] = result['id_usuario'][0]
            else:
                st.error("Credenciais inválidas. Tente novamente.")

    # Registrar Usuário
    elif menu == "Registrar Usuário":
        st.subheader("Registrar Novo Usuário Gerencial")
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        confirm_senha = st.text_input("Confirme a Senha", type="password")
        if st.button("Registrar"):
            if senha == confirm_senha:
                query = "INSERT INTO usuario (nome, email, senha) VALUES (%s, %s, %s)"
                execute_write(query, (nome, email, senha))
                st.success(f"Usuário {nome} registrado com sucesso!")
            else:
                st.error("As senhas não coincidem. Tente novamente.")

    # Escolas Favoritas
    elif menu == "Escolas Favoritas":
        st.subheader("Gerenciamento de Escolas Favoritas")
        if "logged_in" in st.session_state and st.session_state["logged_in"]:
            id_usuario = st.session_state["id_usuario"]

            # Listar escolas disponíveis
            escolas_query = "SELECT CO_ENTIDADE, NO_ENTIDADE FROM escolas"
            df_escolas = execute_query(escolas_query)

            if df_escolas.empty:
                st.info("Nenhuma escola disponível para favoritar.")
            else:
                escola_favorita = st.selectbox("Escolha uma escola para favoritar", df_escolas['NO_ENTIDADE'].tolist())

                if st.button("Adicionar aos Favoritos"):
                    if escola_favorita:
                        # Convertendo para tipo Python nativo
                        codigo_escola = df_escolas.loc[df_escolas['NO_ENTIDADE'] == escola_favorita, 'CO_ENTIDADE'].values[0]
                        codigo_escola = int(codigo_escola)
                        id_usuario = int(id_usuario) if isinstance(id_usuario, (np.integer, int)) else id_usuario
                        insert_bookmark = """
                            INSERT INTO bookmark (id_bookmark, id_usuario, id_escola) 
                            VALUES (%s, %s, %s)
                        """

                        id_bookmark = random.randint(1, 1000000)

                        try:
                            execute_write(insert_bookmark, (id_bookmark, id_usuario, codigo_escola))
                            st.success(f"Escola '{escola_favorita}' adicionada aos favoritos.")
                        except mysql.connector.Error as err:
                            st.error(f"Erro ao adicionar aos favoritos: {err}")
                    else:
                        st.warning("Por favor, selecione uma escola antes de adicionar aos favoritos.")


            # Listar favoritos
            st.subheader("Suas Escolas Favoritas")
            favoritos_query = """
                SELECT e.NO_ENTIDADE AS Nome
                FROM bookmark b
                JOIN escolas e ON b.id_escola = e.CO_ENTIDADE
                WHERE b.id_usuario = %s
            """
            favoritos_df = execute_query(favoritos_query, (int(id_usuario),))
            if favoritos_df.empty:
                st.info("Nenhuma escola favoritada ainda.")
            else:
                st.dataframe(favoritos_df)
        else:
            st.warning("Faça login para acessar esta funcionalidade.")


    # Exportar Dados
    elif menu == "Exportar Dados":
        st.subheader("Exportar Resultados como CSV")
        # Selecionar tabela para exportar
        tabelas = ["escolas", "matriculas", "docentes", "turma", "bookmark"]
        tabela_escolhida = st.selectbox("Escolha uma tabela para exportar", tabelas)

        if st.button("Exportar"):
            export_query = f"SELECT * FROM {tabela_escolhida}"
            df_export = execute_query(export_query)
            if not df_export.empty:
                csv = df_export.to_csv(index=False)
                st.download_button(
                    label="Baixar CSV",
                    data=csv,
                    file_name=f"{tabela_escolhida}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("A tabela selecionada está vazia.")

if __name__ == '__main__':
    gerenciamento()
