# app.py

import streamlit as st

st.set_page_config(
    page_title="Sistema Unificado: Contratos & Crypto",
    page_icon="🤖",
    layout="wide"
)

st.title("Sistema Unificado de Segurança Digital")
st.markdown("""
    ## 🛡️ Bem-vindo!
    
    Este aplicativo combina dois sistemas de segurança:
    
    1. **Contratos:** Registro e Verificação de Integridade (Simulação Blockchain).
    2. **Criptografia:** Criptografia de Arquivos usando RSA.
    
    Use o menu lateral (`Pages`) para navegar entre os sistemas.
""")
# Nota: O Streamlit irá gerar a navegação na sidebar
# automaticamente a partir dos arquivos na pasta 'pages/'.