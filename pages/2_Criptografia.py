# ===================================================================
# app.py
"""
Interface Streamlit para sistema de criptografia RSA
"""
import streamlit as st
from crypto_utils import RSACrypto  # Importar quando separar os arquivos

st.set_page_config(page_title="Criptografia RSA", page_icon="🔐")

# Interface principal
st.title("🔐 Sistema de Criptografia RSA")
st.markdown("---")

# Menu lateral
menu = st.sidebar.selectbox(
    "Escolha uma opção:",
    ["Criptografar Arquivo", "Descriptografar Arquivo"]
)

if menu == "Criptografar Arquivo":
    st.header("📤 Criptografar Arquivo")
    
    # Gerar chaves
    st.subheader("1️⃣ Gerar Chaves")
    
    if st.button("🔑 Gerar Novas Chaves", type="primary"):
        private_key, public_key = RSACrypto.generate_keys()
        st.session_state.private_key = private_key
        st.session_state.public_key = public_key
        st.success("✅ Chaves geradas com sucesso!")
    
    # Mostrar chaves se já foram geradas
    if 'public_key' in st.session_state:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔓 Chave Pública")
            st.text_area("Copie esta chave:", st.session_state.public_key, height=150, key="pub_key")
        
        with col2:
            st.subheader("🔒 Chave Privada")
            st.text_area("⚠️ GUARDE COM SEGURANÇA!", st.session_state.private_key, height=150, key="priv_key")
            st.warning("⚠️ Você precisará desta chave para descriptografar!")
        
        st.markdown("---")
        
        # Upload e criptografia
        st.subheader("2️⃣ Enviar e Criptografar Arquivo")
        uploaded_file = st.file_uploader("Escolha um arquivo .txt", type=['txt'])
        
        if uploaded_file is not None:
            content = uploaded_file.read()
            
            if st.button("🔐 Criptografar e Baixar", type="primary"):
                try:
                    encrypted_content = RSACrypto.encrypt_file(content, st.session_state.public_key)
                    
                    st.success("✅ Arquivo criptografado com sucesso!")
                    
                    # Botão de download
                    st.download_button(
                        label="📥 Baixar Arquivo Criptografado",
                        data=encrypted_content,
                        file_name="arquivo_criptografado.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"❌ Erro ao criptografar: {str(e)}")

elif menu == "Descriptografar Arquivo":
    st.header("📥 Descriptografar Arquivo")
    
    st.subheader("1️⃣ Cole sua Chave Privada")
    private_key_input = st.text_area(
        "Chave Privada:",
        height=150,
        placeholder="Cole aqui a chave privada..."
    )
    
    st.subheader("2️⃣ Enviar Arquivo Criptografado")
    encrypted_file = st.file_uploader("Escolha o arquivo criptografado", type=['txt'])
    
    if encrypted_file is not None and private_key_input:
        if st.button("🔓 Descriptografar", type="primary"):
            try:
                encrypted_content = encrypted_file.read().decode('utf-8')
                decrypted_content = RSACrypto.decrypt_file(encrypted_content, private_key_input)
                
                st.success("✅ Arquivo descriptografado com sucesso!")
                
                # Mostrar conteúdo
                st.subheader("📄 Conteúdo Descriptografado:")
                st.text_area("Texto:", decrypted_content.decode('utf-8'), height=200, key="decrypted")
                
                # Botão de download
                st.download_button(
                    label="📥 Baixar Arquivo Descriptografado",
                    data=decrypted_content,
                    file_name="arquivo_descriptografado.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"❌ Erro ao descriptografar: {str(e)}")
                st.info("Verifique se a chave privada está correta.")

# Informações no rodapé
st.sidebar.markdown("---")
st.sidebar.info("""
**ℹ️ Como usar:**

**Criptografar:**
1. Gere as chaves
2. Copie e guarde a chave privada
3. Envie o arquivo .txt
4. Baixe o arquivo criptografado

**Descriptografar:**
1. Cole a chave privada
2. Envie o arquivo criptografado
3. Baixe o arquivo descriptografado
""")