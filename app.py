import streamlit as st
import mysql.connector
import pandas as pd

# Configuração de cabeçalho da página
st.set_page_config(page_title="Dados Escolas", layout="wide")
st.title("Análise de Escolas")

# Conexão com o banco de dados
def create_connection():
    return mysql.connector.connect(
        host='pro.freedb.tech',
        user='admin',
        password='7#X?PyVGmEh4Xbu',
        port=3306,
        db='escoladb',
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

# Função para exibir a aba "Informações das Escolas"
def display_schools():
    st.subheader("Informações das Escolas")

    escolas_query = """
        WITH Alunos AS (
            SELECT CO_ENTIDADE, COUNT(DISTINCT ID_MATRICULA) AS Total_Alunos
            FROM matriculas
            GROUP BY CO_ENTIDADE
        ),
        Professores AS (
            SELECT CO_ENTIDADE, COUNT(DISTINCT CO_PESSOA_FISICA) AS Total_Professores
            FROM docentes
            GROUP BY CO_ENTIDADE
        ),
        Turmas AS (
            SELECT CO_ENTIDADE, COUNT(DISTINCT ID_TURMA) AS Total_Turmas
            FROM turma
            GROUP BY CO_ENTIDADE
        )
        SELECT 
            e.NO_ENTIDADE AS Nome,
            e.CO_ENTIDADE AS Codigo,
            CASE
                WHEN e.TP_SITUACAO_FUNCIONAMENTO = 1 THEN 'Em atividade'
                WHEN e.TP_SITUACAO_FUNCIONAMENTO = 2 THEN 'Paralisada'
                WHEN e.TP_SITUACAO_FUNCIONAMENTO = 3 THEN 'Extinta'
                ELSE 'Desconhecido'
            END AS Status_Funcionamento,
            e.CO_MUNICIPIO AS Municipio,
            CASE
                WHEN e.TP_LOCALIZACAO = 1 THEN 'Urbana'
                WHEN e.TP_LOCALIZACAO = 2 THEN 'Rural'
                ELSE 'Desconhecido'
            END AS Localizacao,
            CASE
                WHEN e.TP_DEPENDENCIA = 1 THEN 'Federal'
                WHEN e.TP_DEPENDENCIA = 2 THEN 'Estadual'
                WHEN e.TP_DEPENDENCIA = 3 THEN 'Municipal'
                WHEN e.TP_DEPENDENCIA = 4 THEN 'Privada'
                ELSE 'Desconhecido'
            END AS Dependencia_Administrativa,
            TRIM(TRAILING ', ' FROM 
                CONCAT(
                    CASE WHEN e.IN_COMUM_CRECHE = 1 THEN 'EI, ' ELSE '' END,
                    CASE WHEN e.IN_COMUM_FUND_AI = 1 THEN 'EF1, ' ELSE '' END,
                    CASE WHEN e.IN_COMUM_FUND_AF = 1 THEN 'EF2, ' ELSE '' END,
                    CASE WHEN e.IN_COMUM_MEDIO_MEDIO = 1 THEN 'EM, ' ELSE '' END,
                    CASE WHEN e.IN_COMUM_EJA_FUND = 1 OR e.IN_COMUM_EJA_MEDIO = 1 THEN 'EJA, ' ELSE '' END,
                    CASE WHEN e.IN_COMUM_PROF = 1 THEN 'EP, ' ELSE '' END,
                    CASE WHEN e.IN_ESPECIAL_EXCLUSIVA = 1 THEN 'EE, ' ELSE '' END
                )
            ) AS Niveis_Atendidos,
            COALESCE(a.Total_Alunos, 0) AS Total_Alunos,
            COALESCE(p.Total_Professores, 0) AS Total_Professores,
            COALESCE(t.Total_Turmas, 0) AS Total_Turmas
        FROM 
            escolas e
        LEFT JOIN 
            Alunos a ON e.CO_ENTIDADE = a.CO_ENTIDADE
        LEFT JOIN 
            Professores p ON e.CO_ENTIDADE = p.CO_ENTIDADE
        LEFT JOIN 
            Turmas t ON e.CO_ENTIDADE = t.CO_ENTIDADE
        ORDER BY 
            Total_Alunos DESC;
    """
    df_summary = execute_query(escolas_query)
    st.dataframe(df_summary, use_container_width=True)

    return df_summary

# Função para exibir as turmas da escola selecionada
def display_school_classes(df_escolas):
    # Seletor de escola
    school_names = df_escolas['Nome'].tolist()
    selected_school_name = st.selectbox("Escolha uma escola", school_names)

    # Obtendo o ID da escola selecionada
    selected_school_id = df_escolas[df_escolas['Nome'] == selected_school_name]['Codigo'].values[0]

    # Exibir as turmas dessa escola
    st.subheader(f"Turmas da Escola: {selected_school_name}")

    # Consulta para listar as turmas da escola selecionada
    turmas_query = f"""
        SELECT
            t.ID_TURMA AS Codigo_Turma,
            t.NO_TURMA AS Nome_Turma,
            CASE 
                WHEN t.TP_TIPO_TURMA = 0 THEN 'Não se aplica'
                WHEN t.TP_TIPO_TURMA = 1 THEN 'Classe hospitalar'
                WHEN t.TP_TIPO_TURMA = 2 THEN 'Unidade de atendimento socioeducativo'
                WHEN t.TP_TIPO_TURMA = 3 THEN 'Unidade prisional'
                WHEN t.TP_TIPO_TURMA = 4 THEN 'Atividade complementar'
                WHEN t.TP_TIPO_TURMA = 5 THEN 'Atendimento Educacional Especializado (AEE)'
                ELSE 'Desconhecido'
            END AS Tipo_Turma,
            CASE
                WHEN t.TP_MEDIACAO_DIDATICO_PEDAGO = 1 THEN 'Presencial'
                WHEN t.TP_MEDIACAO_DIDATICO_PEDAGO = 2 THEN 'Semipresencial'
                WHEN t.TP_MEDIACAO_DIDATICO_PEDAGO = 3 THEN 'EAD'
                ELSE 'Não Informado'
            END AS Mediacao,
            TRIM(TRAILING ', ' FROM 
                CONCAT(
                    CASE WHEN t.IN_DISC_LINGUA_PORTUGUESA = 10 THEN 'Portugues, ' ELSE '' END,
                    CASE WHEN t.IN_DISC_MATEMATICA = 10 THEN 'Matemática, ' ELSE '' END,
                    CASE WHEN t.IN_DISC_CIENCIAS = 10 THEN 'Ciências, ' ELSE '' END,
                    CASE WHEN t.IN_DISC_HISTORIA = 10 THEN 'História, ' ELSE '' END,
                    CASE WHEN t.IN_DISC_GEOGRAFIA = 10 THEN 'Geografia, ' ELSE '' END,
                    CASE WHEN t.IN_DISC_ARTES = 10 THEN 'Artes, ' ELSE '' END,
                    CASE WHEN t.IN_DISC_EDUCACAO_FISICA = 10 THEN 'Educação Física, ' ELSE '' END,
                    CASE WHEN t.IN_DISC_LINGUA_INGLES = 10 THEN 'Inglês, ' ELSE '' END,
                    CASE WHEN t.IN_DISC_LINGUA_ESPANHOL = 10 THEN 'Espanhol, ' ELSE '' END,
                    CASE WHEN t.IN_DISC_INFORMATICA_COMPUTACAO = 10 THEN 'Informática, ' ELSE '' END,
                    CASE WHEN t.IN_DISC_LIBRAS = 10 THEN 'Libras, ' ELSE '' END,
                    CASE WHEN t.IN_DISC_FILOSOFIA = 10 THEN 'Filosofia, ' ELSE '' END,
                    CASE WHEN t.IN_DISC_SOCIOLOGIA = 10 THEN 'Sociologia, ' ELSE '' END
                )
            ) AS Disciplinas_Ministradas
        FROM
            turma t
        WHERE
            t.CO_ENTIDADE = {selected_school_id}
        ORDER BY
            t.ID_TURMA;
    """
    df_turmas = execute_query(turmas_query)

    # Exibir as turmas
    st.dataframe(df_turmas, use_container_width=True)

# Função para exibir os professores e alunos de uma escola
def display_students_and_teachers(df_escolas):
    # Seletor de escola
    school_names = df_escolas['Nome'].tolist()
    selected_school_name = st.selectbox("Escolha uma escola", school_names)

    # Obtendo o ID da escola selecionada
    selected_school_id = df_escolas[df_escolas['Nome'] == selected_school_name]['Codigo'].values[0]

    # Exibir os alunos dessa escola
    st.subheader(f"Alunos da Escola: {selected_school_name}")
    alunos_query = f"""        
        SELECT
            m.CO_PESSOA_FISICA AS Cod_Pessoa,   
            m.NU_IDADE_REFERENCIA AS Idade, 
            CASE 
                WHEN m.TP_SEXO = 1 THEN 'Masculino'
                WHEN m.TP_SEXO = 2 THEN 'Feminino'
                ELSE 'Não Informado'
            END AS Sexo,
            CASE
                WHEN m.TP_LOCALIZACAO = 1 THEN 'Urbana'
                WHEN m.TP_LOCALIZACAO = 2 THEN 'Rural'
                ELSE 'Desconhecido'
            END AS Localizacao,
            CASE
                WHEN m.TP_DEPENDENCIA = 1 THEN 'Federal'
                WHEN m.TP_DEPENDENCIA = 2 THEN 'Estadual'
                WHEN m.TP_DEPENDENCIA = 3 THEN 'Municipal'
                WHEN m.TP_DEPENDENCIA = 4 THEN 'Privada'
                ELSE 'Desconhecido'
            END AS Dependencia_Administrativa,
            TRIM(TRAILING ', ' FROM 
                CONCAT(
                    CASE WHEN m.IN_REGULAR = 1 THEN 'Ensino Regular, ' ELSE '' END,
                    CASE WHEN m.IN_EJA = 1 THEN 'Educação de Jovens e Adultos (EJA), ' ELSE '' END,
                    CASE WHEN m.IN_PROFISSIONALIZANTE = 1 THEN 'Ensino Profissionalizante, ' ELSE '' END,
                    CASE WHEN m.IN_ESPECIAL_EXCLUSIVA = 1 THEN 'Educação Especial, ' ELSE '' END
                )
            ) AS Niveis_Atendidos
        FROM
            matriculas m
        WHERE 
            m.CO_ENTIDADE = {selected_school_id}
    """
    df_alunos = execute_query(alunos_query)
    if df_alunos.empty:
        st.warning("Nenhum aluno encontrado para essa escola.")
    else:
        st.dataframe(df_alunos, use_container_width=True)

    # Exibir os professores dessa escola
    st.subheader(f"Professores da Escola: {selected_school_name}")
    professores_query = f"""
        SELECT DISTINCT 
            CO_PESSOA_FISICA AS Cod_Pessoa,
            NU_ANO_CENSO AS Ano_Censo,
            CASE 
                WHEN TP_SEXO = 1 THEN 'Masculino'
                WHEN TP_SEXO = 2 THEN 'Feminino'
                ELSE 'Não Informado'
            END AS Sexo,
            CASE 
                WHEN TP_COR_RACA = 1 THEN 'Branca'
                WHEN TP_COR_RACA = 2 THEN 'Preta'
                WHEN TP_COR_RACA = 3 THEN 'Parda'
                WHEN TP_COR_RACA = 4 THEN 'Amarela'
                WHEN TP_COR_RACA = 5 THEN 'Indígena'
                ELSE 'Não Declarado'
            END AS Cor_Raca,
            CASE 
                WHEN TP_NACIONALIDADE = 1 THEN 'Brasileiro'
                WHEN TP_NACIONALIDADE = 2 THEN 'Estrangeiro'
                WHEN TP_NACIONALIDADE = 3 THEN 'Naturalizado'
                ELSE 'Não Declarado'
            END AS Nacionalidade,
            CO_MUNICIPIO_END AS Municipio_Residencia,
            TP_ESCOLARIDADE AS Escolaridade,
            TP_TIPO_DOCENTE AS Tipo_Docente
        FROM 
            docentes
        WHERE 
            CO_ENTIDADE = {selected_school_id}
    """
    df_professores = execute_query(professores_query)
    if df_professores.empty:
        st.warning("Nenhum professor encontrado para essa escola.")
    else:
        st.dataframe(df_professores, use_container_width=True)

# Função para exibir o número de alunos agrupados por nível de ensino
def display_students_by_level(df_escolas):
    # Seletor de escola
    school_names = df_escolas['Nome'].tolist()
    selected_school_name = st.selectbox("Escolha uma escola", school_names)

    # Obtendo o ID da escola selecionada
    selected_school_id = df_escolas[df_escolas['Nome'] == selected_school_name]['Codigo'].values[0]

    # Agrupar os alunos por nível de ensino
    st.subheader(f"Total de Alunos por Nível de Ensino - Escola: {selected_school_name}")
    alunos_by_level_query = f"""
        SELECT
            CASE
                WHEN m.TP_ETAPA_ENSINO IN (1, 2, 3, 56) THEN 'Educação Infantil (EI)'
                WHEN m.TP_ETAPA_ENSINO IN (4, 5, 6, 7, 8, 14, 15, 16, 17, 18, 69, 72) THEN 'Ensino Fundamental I (EFI)'
                WHEN m.TP_ETAPA_ENSINO IN (9, 10, 11, 12, 19, 20, 21, 22, 23, 24, 70, 72) THEN 'Ensino Fundamental II (EFII)'
                WHEN m.TP_ETAPA_ENSINO IN (25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38) THEN 'Ensino Médio (EM)'
                WHEN m.TP_ETAPA_ENSINO IN (65, 67, 69, 70, 71, 72, 73) THEN 'Educação de Jovens e Adultos (EJA)'
                WHEN m.TP_ETAPA_ENSINO IN (39, 40, 64, 68, 74) THEN 'Ensino Profissionalizante (EP)'
                ELSE 'Não Informado'
            END AS Nivel_Ensino,
            COUNT(DISTINCT m.CO_PESSOA_FISICA) AS Total_Alunos
        FROM
            matriculas m
        WHERE
            m.CO_ENTIDADE = {selected_school_id}
        GROUP BY
            Nivel_Ensino
        ORDER BY
            Total_Alunos DESC;
    """
    df_alunos_by_level = execute_query(alunos_by_level_query)
    if df_alunos_by_level.empty:
        st.warning("Nenhum aluno encontrado para essa escola.")
    else:
        st.dataframe(df_alunos_by_level, use_container_width=True)

# Função principal para exibir as abas
def app():
    # Seleção da aba
    page = st.sidebar.radio("Análise de Escolas", ["Escolas", "Turmas por Escola", "Alunos e Professores por Escola", "Alunos por Nível de Ensino"])
    
    # Inicializa apenas na aba "Escolas"
    df_escolas = None
    if page == "Escolas":
        df_escolas = display_schools()
    else:
        # Carregar "df_escolas" apenas para consultas subsequentes
        df_escolas = execute_query("""
            WITH Alunos AS (
                SELECT CO_ENTIDADE, COUNT(DISTINCT ID_MATRICULA) AS Total_Alunos
                FROM matriculas
                GROUP BY CO_ENTIDADE
            )
            SELECT 
                e.NO_ENTIDADE AS Nome,
                e.CO_ENTIDADE AS Codigo,
                COALESCE(a.Total_Alunos, 0) AS Total_Alunos
            FROM 
                escolas e
            LEFT JOIN 
                Alunos a ON e.CO_ENTIDADE = a.CO_ENTIDADE
            ORDER BY Total_Alunos DESC
        """)
    
    if page == "Turmas por Escola":
        display_school_classes(df_escolas)
    elif page == "Alunos e Professores por Escola":
        display_students_and_teachers(df_escolas)
    elif page == "Alunos por Nível de Ensino":
        display_students_by_level(df_escolas)

if __name__ == '__main__':
    app()