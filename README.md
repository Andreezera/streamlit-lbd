# Configuração e Execução do Ambiente Virtual Python

## Preparar o Ambiente Virtual Python

1. **Selecione um diretório** para hospedar sua aplicação.
2. **Instale o `virtualenv`**:
   ```bash
   pip install virtualenv
   ```
3. **Crie o ambiente virtual**:
   ```bash
   python -m venv lab-not
   ```
4. **Ative o ambiente virtual**:
   - **No Windows**:
     ```bash
     .\lab-not\Scripts\activate
     ```
   - **No Linux/Mac**:
     ```bash
     source lab-not/bin/activate
     ```
5. **Acesse o diretório do ambiente virtual**:
   ```bash
   cd lab-not
   ```
6. **Instale os pacotes necessários**:
   ```bash
   pip install streamlit mysql-connector-python plotly.express matplotlib
   ```
7. **Clone o repositório** na raiz do ambiente virtual:
   ```bash
   git clone https://github.com/Andreezera/streamlit-lbd.git
   ```

## Executar o Projeto

1. **Navegue para a pasta do repositório**:
   ```bash
   cd lab-not/streamlit-lbd/streamlit-lbd
   ```
2. **Execute o Streamlit**:
   ```bash
   streamlit run app.py
   ```
