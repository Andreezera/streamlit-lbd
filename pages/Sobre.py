import streamlit as st
import mysql.connector
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Sobre", layout="wide")
st.logo("https://igce.rc.unesp.br/images/unesp.svg")
st.title("📑 Sobre à Aplicação")

# Texto informativo detalhado
st.write("""
Esta aplicação foi desenvolvida como parte do trabalho acadêmico da disciplina **Laboratório de Banco de Dados**,
ministrada pelo Professor **Bruno Elias Penteado**, no segundo semestre de **2024**, no âmbito do curso de **Ciências da Computação**,
da **Universidade Estadual Paulista (UNESP) – Campus de Rio Claro**.

O objetivo principal deste trabalho é fornecer uma ferramenta para a análise e visualização de dados educacionais,
utilizando informações extraídas de um banco de dados relacional, integrando dados sobre escolas, turmas, alunos e professores.
Por meio desta aplicação, é possível explorar o desempenho de escolas, o número de alunos matriculados, os tipos de turmas oferecidas,
bem como informações detalhadas sobre o quadro docente e a distribuição de alunos por nível de ensino.

**Equipe de Desenvolvimento:**
- **André Augusto Costa Dionísio**: Estudante do curso de **Ciências da Computação** da **UNESP – Rio Claro**
- **Thabata Santana Santos**: Estudante do curso de **Ciências da Computação** da **UNESP – Rio Claro**


Este trabalho tem como foco o uso de tecnologias como **Streamlit**, **MySQL** e **Python** para construção de dashboards interativos,
com a finalidade de facilitar a análise de dados educacionais, sempre respeitando as boas práticas de engenharia de software e modelagem de dados.

Para ter acesso total às funcionalidades do projeto, utilize usuario administrador:
usuario: admin@admin.com
senha: admin

""")
