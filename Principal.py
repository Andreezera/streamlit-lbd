import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# Configuração de cabeçalho da página
st.set_page_config(page_title="Dados Escolas", layout="wide")
st.logo("https://igce.rc.unesp.br/images/unesp.svg")
st.title("🏫 Análise de Escolas")

# Conexão com o banco de dados
def create_connection():
    return mysql.connector.connect(
        host='mysql-3468e67c-streamlit-lbd.e.aivencloud.com',
        user='avnadmin',
        password='AVNS_qWwT1IkX4yxrSOOfe4t',
        port=15308,
        db='defaultdb',
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
            END AS Dependencia_Administrativa
        FROM matriculas m
        WHERE m.CO_ENTIDADE = {selected_school_id}
        ORDER BY m.NU_IDADE_REFERENCIA;
    """
    df_alunos = execute_query(alunos_query)
    st.dataframe(df_alunos, use_container_width=True)

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

# Função para exibir as matrículas de alunos com deficiência intelectual ou autismo
def display_autistic_or_intellectual_disability_students(df_escolas):
    st.subheader("Escolas com Alunos Autistas ou com Deficiência Intelectual")

    # Consulta SQL para identificar as escolas com alunos autistas ou com deficiência intelectual
    query = """
        SELECT 
            e.NO_ENTIDADE AS Nome_Escola,
            e.CO_ENTIDADE AS Codigo_Escola,
            COUNT(m.ID_MATRICULA) AS Total_Alunos
        FROM 
            matriculas m
        INNER JOIN 
            escolas e ON m.CO_ENTIDADE = e.CO_ENTIDADE
        WHERE 
            m.IN_AUTISMO = 1 OR m.IN_DEF_INTELECTUAL = 1
        GROUP BY 
            e.CO_ENTIDADE
        ORDER BY 
            Total_Alunos DESC
    """
    df_matriculas =execute_query(query)

    # Exibir a tabela no Streamlit
    if df_matriculas.empty:
        st.warning("Nenhuma matrícula encontrada para alunos autistas ou com deficiência intelectual.")
    else:
        st.dataframe(df_matriculas, use_container_width=True)

    # Gráfico de barras das 10 escolas com mais alunos com autismo ou deficiência intelectual
    st.subheader("Gráfico: Top 10 Escolas com Alunos Autistas ou com Deficiência Intelectual")
    if not df_matriculas.empty:
        # Selecionar as 10 escolas com mais alunos
        top_10_escolas = df_matriculas.nlargest(10, 'Total_Alunos')
        
        # Criar o gráfico
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(top_10_escolas['Nome_Escola'], 
                top_10_escolas['Total_Alunos'], 
                color='coral')
        ax.set_xlabel("Quantidade de Alunos")
        ax.set_ylabel("Escolas")
        ax.set_title("Top 10 Escolas com Alunos Autistas ou com Deficiência Intelectual")
        ax.invert_yaxis()  # Inverter o eixo Y para a escola com mais alunos aparecer no topo
        st.pyplot(fig)

# Função para exibir as escolas com as respectivas contagens de matrículas
def display_school_enrollments(df_escolas):
    st.subheader("Contagem de Matrículas por Escola")

    # Filtro para selecionar a escola
    school_names = df_escolas['Nome'].tolist()
    selected_school_name = st.selectbox("Escolha uma escola", school_names)

    # Obtendo o ID da escola selecionada
    selected_school_id = df_escolas[df_escolas['Nome'] == selected_school_name]['Codigo'].values[0]

    # Consulta SQL para selecionar as matrículas da escola específica
    escolas_query = f"""
        SELECT 
            escolas.NO_ENTIDADE AS Nome,
            escolas.CO_ENTIDADE AS Codigo,
            COUNT(matriculas.ID_MATRICULA) AS Contagem
        FROM escolas
        LEFT JOIN matriculas ON matriculas.CO_ENTIDADE = escolas.CO_ENTIDADE
        WHERE escolas.CO_ENTIDADE = {selected_school_id}
        GROUP BY escolas.CO_ENTIDADE;
    """
    
    # Executar a consulta
    df_escolas_selecionada = execute_query(escolas_query)

    # Exibir a tabela no Streamlit
    st.dataframe(df_escolas_selecionada, use_container_width=True)

# Função para o ranqueamento de escolas por matrícula
def display_rank_enrollments(df_escolas):
    
    query = """
    WITH RankedSchools AS (
    SELECT 
        e.NO_ENTIDADE AS Nome_Escola,
        e.CO_ENTIDADE AS Codigo_Escola,
        COUNT(m.ID_MATRICULA) AS Contagem,
        RANK() OVER (ORDER BY COUNT(m.ID_MATRICULA) DESC) AS `Rank`
    FROM 
        escolas e
    LEFT JOIN 
        matriculas m ON e.CO_ENTIDADE = m.CO_ENTIDADE
    GROUP BY 
        e.CO_ENTIDADE
)
SELECT 
    Nome_Escola,
    Codigo_Escola,
    Contagem,
    `Rank`
FROM RankedSchools
ORDER BY `Rank`;
        """

    # Obter os dados da consulta
    df_escolas = execute_query(query)

    # Exibir os dados em uma tabela
    st.subheader("Tabela de Ranqueamento de Escolas por Matriculas")
    st.dataframe(df_escolas, use_container_width=True)

    # Filtrar apenas as 10 primeiras escolas
    df_top_10 = df_escolas.head(10)

    # Gráfico de barras das 10 escolas com maior contagem de matrículas
    st.subheader("Gráfico: Top 10 Escolas por Contagem de Matrículas")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(df_top_10['Nome_Escola'], df_top_10['Contagem'], color='skyblue')
    ax.set_xlabel("Quantidade de Matrículas")
    ax.set_ylabel("Escolas")
    ax.set_title("Top 10 Escolas por Contagem de Matrículas")
    ax.invert_yaxis()  # Inverte o eixo para a maior contagem aparecer no topo
    st.pyplot(fig)

# Função principal para exibir as abas
def app():
    # Seleção da aba
    page = st.sidebar.radio("🏫 Análise de Escolas", ["Escolas", "Turmas por Escola", "Alunos e Professores por Escola", "Alunos por Nível de Ensino", "Escolas com Alunos Autistas ou com Deficiência Intelectual", "Contagem de Matrículas por Escola", "Ranqueamento de Escolas (Por Número de Matriculas)"])

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

    # Definir a lógica para exibição das diferentes abas
    #if page == "Escolas":
        #df_escolas = display_schools()
    if page == "Turmas por Escola":
        display_school_classes(df_escolas)
    elif page == "Alunos e Professores por Escola":
        display_students_and_teachers(df_escolas)
    elif page == "Alunos por Nível de Ensino":
        display_students_by_level(df_escolas)
    elif page == "Escolas com Alunos Autistas ou com Deficiência Intelectual":
        display_autistic_or_intellectual_disability_students(df_escolas)
    elif page == "Contagem de Matrículas por Escola":
        display_school_enrollments(df_escolas)
    elif page == "Ranqueamento de Escolas (Por Número de Matriculas)":
        display_rank_enrollments(df_escolas)

if __name__ == '__main__':
    app()
