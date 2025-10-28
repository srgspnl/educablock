import streamlit as st
import io 
from contract_manager import ContractManager

# --- Configuração Inicial e Estado da Sessão ---

st.set_page_config(layout="wide", page_title="Registro de Contratos Imutáveis")

# Inicializa o ContractManager na sessão do Streamlit
if 'contract_manager' not in st.session_state:
    st.session_state.contract_manager = ContractManager()
    
manager = st.session_state.contract_manager

st.title("🛡️ Sistema de Verificação de Contratos (Simulação Blockchain)")
st.caption(f"Contratos Registrados: {manager.total_contracts}")

# --- Menu Principal (Sidebar) ---

st.sidebar.title("🛠️ Opções do Sistema")
menu_selection = st.sidebar.radio(
    "Selecione a Ação",
    ["1. Enviar Novo Contrato (Upload)", 
     "2. Consultar Contrato por Número", 
     "3. Consultar Contrato por Hash", 
     "4. Verificar Texto e Integridade (Upload)",
     "5. Baixar Contrato por Hash (Download)"] # NOVA OPÇÃO
)

# --- Opção 1: Upload de Contrato ---
if menu_selection == "1. Enviar Novo Contrato (Upload)":
    st.header("1. Registrar Novo Contrato")
    st.info("O hash (assinatura digital) do contrato será gerado e armazenado com o texto.")

    uploaded_file = st.file_uploader("Selecione um arquivo .txt para o contrato:", type="txt", key="upload_new")

    if uploaded_file is not None:
        try:
            # Lendo o conteúdo do arquivo
            string_io = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            contract_text = string_io.read()
            
            # Adiciona o contrato
            contract_number = manager.add_contract(contract_text)
            contract_hash = manager.hash_text(contract_text)

            st.success(f"✅ Contrato Registrado com Sucesso!")
            st.markdown(f"**Número do Contrato:** **`{contract_number}`**")
            st.markdown(f"**Hash (Assinatura):** `{contract_hash}`")
            st.text_area("Prévia do Conteúdo", contract_text[:500] + '...', height=150, disabled=True)

        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")


# --- Opção 2: Consultar Contrato por Número ---
elif menu_selection == "2. Consultar Contrato por Número":
    st.header("2. Consultar Contrato por Número")
    
    if manager.total_contracts == 0:
        st.warning("Nenhum contrato registrado ainda. Por favor, envie um arquivo primeiro.")
    else:
        # Usa um slider/select box para o número do contrato
        selected_number = st.select_slider(
            "Selecione o número do contrato:",
            options=manager.contract_numbers,
            value=manager.contract_numbers[-1]
        )
        
        contract = manager.get_contract_by_index(selected_number)

        if contract:
            st.markdown("---")
            st.subheader(f"Contrato #{contract['number']}")
            st.markdown(f"**Hash (Assinatura):** `{contract['hash']}`")
            st.text_area("Conteúdo do Contrato", contract['text'], height=300)
        else:
            st.error(f"Contrato número {selected_number} não encontrado.")


# --- Opção 3: Consultar Contrato por Hash ---
elif menu_selection == "3. Consultar Contrato por Hash":
    st.header("3. Consultar Contrato por Hash")

    input_hash = st.text_input("Cole o Hash (Assinatura Digital) para buscar:", key="hash_search")

    if input_hash:
        contract = manager.get_contract_by_hash(input_hash.strip())
        
        st.markdown("---")
        if contract:
            st.success("✅ Contrato Encontrado!")
            st.subheader(f"Contrato #{contract['number']}")
            st.markdown(f"**Hash Correspondente:** `{contract['hash']}`")
            st.text_area("Conteúdo do Contrato", contract['text'], height=300)
        else:
            st.error("❌ Hash não encontrado. O contrato pode não estar registrado neste sistema.")


# --- Opção 4: Verificar Texto e Integridade (por Upload) ---
elif menu_selection == "4. Verificar Texto e Integridade (Upload)":
    st.header("4. Verificar Texto e Integridade")
    st.info("Faça o upload do arquivo para verificar se o hash gerado confere com algum registro oficial.")

    uploaded_verify_file = st.file_uploader(
        "Selecione o arquivo .txt a ser verificado:", 
        type="txt", 
        key="upload_verify"
    )

    if uploaded_verify_file is not None:
        try:
            # Lendo o conteúdo do arquivo
            string_io = io.StringIO(uploaded_verify_file.getvalue().decode("utf-8"))
            input_text = string_io.read()
            
            # Gera o hash do texto de entrada
            calculated_hash = manager.hash_text(input_text.strip())
            
            # Verifica se o hash gerado existe
            contract = manager.verify_text_and_find_contract(input_text.strip())

            st.markdown("---")
            st.markdown(f"**Hash Calculado:** `{calculated_hash}`")
            
            if contract:
                st.success(f"🎉 **INTEGRIDADE VERIFICADA!**")
                st.markdown(f"Este hash corresponde ao **Contrato Número:** **`{contract['number']}`**")
                st.info("O arquivo enviado é **idêntico** ao contrato original registrado. Sua integridade está garantida.")
            else:
                st.error("⚠️ Hash Não Encontrado!")
                st.warning("O hash calculado não corresponde a nenhum contrato registrado. O arquivo pode ser novo, ou ter sido adulterado.")
                
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")

# --- Opção 5: Baixar Contrato por Hash (Download) ---
elif menu_selection == "5. Baixar Contrato por Hash (Download)":
    st.header("5. Baixar Contrato por Hash")
    st.info("Selecione um contrato registrado para baixá-lo. O nome do arquivo será o seu Hash (assinatura digital).")

    if manager.total_contracts == 0:
        st.warning("Nenhum contrato registrado para baixar.")
    else:
        # Permite selecionar o contrato pelo número
        selected_number = st.selectbox(
            "Selecione o número do contrato para download:",
            options=manager.contract_numbers,
            key="download_select"
        )
        
        contract = manager.get_contract_by_index(selected_number)
        
        if contract:
            contract_text = contract['text']
            contract_hash = contract['hash']
            file_name = f"{contract_hash}.txt"
            
            st.markdown("---")
            st.markdown(f"**Contrato selecionado #**`{contract['number']}`")
            st.markdown(f"**Nome do Arquivo de Download:** `{file_name}`")
            
            # Botão de download
            st.download_button(
                label="Clique para Baixar o Contrato",
                data=contract_text,
                file_name=file_name,
                mime="text/plain"
            )
            st.markdown("A integridade do arquivo baixado pode ser verificada usando a Opção 4.")
