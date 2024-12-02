import streamlit as st

# Configuração da página
st.set_page_config(page_title="Dashboard Interativo com Tableau", layout="wide")
st.logo("https://igce.rc.unesp.br/images/unesp.svg")

# Título do Aplicativo
st.title("Dashboard Interativo com Tableau")

# Descrição
st.write("""
Este painel interativo foi criado no Tableau Public
""")

# Código do iframe do Tableau Public
tableau_iframe_code = """
<iframe 
    src="https://public.tableau.com/views/BI_17330857834240/BI?:embed=y&:showVizHome=no&:display_count=yes" 
    width="100%" 
    height="800" 
    frameborder="0">
</iframe>
"""

# Renderizar o iframe no Streamlit
st.components.v1.html(tableau_iframe_code, height=800)
