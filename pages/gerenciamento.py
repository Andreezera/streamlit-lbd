import streamlit as st
import mysql.connector
import pandas as pd
import hashlib
import os
import random
import numpy as np

# Configuração da página
st.set_page_config(page_title="Acesso à Aplicação", layout="wide")
st.logo("https://igce.rc.unesp.br/images/unesp.svg")
st.title("Acesso à Aplicação")

# Conexão com o banco de dados
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

# Função para executar consulta SQL e retornar um DataFrame
def execute_query(query, params=None):
    conn = create_connection()
    if conn is None:
        return pd.DataFrame()
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
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close()

# Função para gerar o hash da senha
def hash_password(password):
    # Gera o salt e o hash da senha com SHA256
    salt = os.urandom(32)  # Gera um salt aleatório de 32 bytes
    hashed = hashlib.sha256(salt + password.encode('utf-8')).hexdigest()  # Criptografa com SHA256 e concatena o salt
    return salt.hex() + hashed  # Retorna o salt + hash como uma string concatenada

# Função para verificar a senha
def check_password(stored_password, input_password):
    salt = bytes.fromhex(stored_password[:64])  # Recupera o salt armazenado
    stored_hash = stored_password[64:]  # Recupera o hash armazenado
    input_hash = hashlib.sha256(salt + input_password.encode('utf-8')).hexdigest()  # Gera o hash da senha inserida
    return stored_hash == input_hash  # Compara os hashes

# Verificação de autenticação
def is_logged_in():
    return st.session_state.get("logged_in", False)

# Página de gerenciamento
def gerenciamento():
    st.sidebar.subheader("☰ Menu de Gerenciamento")
    menu = st.sidebar.radio("Escolha uma opção", [
        "Login",
        "Cadastrar",
        "Registrar Usuário",
        "Excluir Usuário",
        "Escolas Favoritas",
        "Exportar Dados"
    ])

    # Login
    if menu == "Login":
        st.subheader("🔑 Login")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            progress = st.progress(0)
            progress.progress(25)

            query = "SELECT id_usuario, nome, role, senha FROM usuario WHERE email = %s"
            result = execute_query(query, (email,))
            progress.progress(75)

            if not result.empty:
                stored_password = result['senha'][0]  # Senha armazenada no banco (salt + hash)
                
                if check_password(stored_password, senha):  # Comparando o hash armazenado com a senha fornecida
                    nome = result['nome'][0]
                    role = result['role'][0]
                    st.success(f"Bem-vindo(a), {nome}! Você está logado como {role}.")
                    st.session_state["logged_in"] = True
                    st.session_state["id_usuario"] = result['id_usuario'][0]
                    st.session_state["role"] = role
                    progress.progress(100)
                else:
                    progress.progress(100)
                    st.error("Credenciais inválidas. Tente novamente.")
            else:
                progress.progress(100)
                st.error("Credenciais inválidas. Tente novamente.")

    # Cadastro de usuário com hash da senha
    elif menu == "Cadastrar":
        st.subheader("📝 Cadastrar Novo Usuário (Público)")
        with st.form("cadastro"):
            nome = st.text_input('Nome:')
            email = st.text_input('Email:')
            senha = st.text_input('Senha:', type="password")
            submit = st.form_submit_button("Enviar")

        if submit:
            if not nome or not email or not senha:
                st.warning("Todos os campos devem ser preenchidos.")
            else:
                hashed_password = hash_password(senha)  # Criptografa a senha
                query = "INSERT INTO usuario (nome, email, senha, role) VALUES (%s, %s, %s, 'aberto')"
                execute_write(query, (nome, email, hashed_password))
                st.success("Cadastro realizado com sucesso!")
                st.balloons()


    # Registrar Usuário
    elif menu == "Registrar Usuário":
        if st.session_state.get("role") == "gerencial":
            st.subheader("➕ Registrar Novo Usuário")
            nome = st.text_input("Nome")
            email = st.text_input("Email")
            senha = st.text_input("Senha", type="password")
            confirm_senha = st.text_input("Confirme a Senha", type="password")
            role = st.selectbox("Tipo de Usuário", ["gerencial", "aberto"])
            if st.button("Registrar"):
                if senha == confirm_senha:
                    hashed_password = hash_password(senha)  # Criptografa a senha
                    query = "INSERT INTO usuario (nome, email, senha, role) VALUES (%s, %s, %s, %s)"
                    execute_write(query, (nome, email, hashed_password, role))
                    st.success(f"Usuário {nome} registrado com sucesso!")
                else:
                    st.error("As senhas não coincidem. Tente novamente.")
        else:
            st.warning("Acesso restrito a usuários gerenciais.")

    # Exclusão de Usuário
    elif menu == "Excluir Usuário":
        if st.session_state.get("role") == "gerencial":
            st.subheader("❌ Excluir Usuário")
            usuarios = execute_query("SELECT id_usuario, nome, email FROM usuario")
            if not usuarios.empty:
                st.write("Selecione o usuário para exclusão:")
                usuario_selecionado = st.selectbox(
                    "Usuários cadastrados",
                    usuarios.apply(lambda x: f"{x['id_usuario']} - {x['nome']} ({x['email']})", axis=1)
                )
                
                id_usuario_selecionado = int(usuario_selecionado.split(" - ")[0])

                if st.button("Excluir"):
                    try:
                        execute_write("DELETE FROM usuario WHERE id_usuario = %s", (id_usuario_selecionado,))
                        st.success(f"Usuário com ID {id_usuario_selecionado} excluído com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao excluir usuário: {e}")
            else:
                st.warning("Nenhum usuário encontrado para exclusão.")
        else:
            st.warning("Acesso restrito a usuários gerenciais.")

# Escolas Favoritas
    elif menu == "Escolas Favoritas":
        if is_logged_in():
            st.subheader("⭐ Gerenciamento de Escolas Favoritas")
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
        st.subheader("📥 Exportar Resultados como CSV")
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