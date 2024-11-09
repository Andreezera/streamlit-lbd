Configuração e Execução do Ambiente Virtual Python
Preparar o Ambiente Virtual Python
Selecione um diretório para hospedar sua aplicação.
Instale o virtualenv (se ainda não estiver instalado):
bash
Copiar código
pip install virtualenv
Crie o ambiente virtual:
bash
Copiar código
python -m venv lab-not
Ative o ambiente virtual:
No Windows:
bash
Copiar código
.\lab-not\Scripts\activate
No Linux/Mac:
bash
Copiar código
source lab-not/bin/activate
Acesse o diretório do ambiente virtual:
bash
Copiar código
cd lab-not
Instale os pacotes necessários:
bash
Copiar código
pip install streamlit mysql-connector-python plotly.express matplotlib
Clone o repositório na raiz do ambiente virtual:
bash
Copiar código
git clone <URL_DO_REPOSITORIO>
Executar o Projeto
Navegue para a pasta do repositório:
bash
Copiar código
cd <nome_do_repositorio>
Execute o Streamlit:
bash
Copiar código
streamlit run app.py