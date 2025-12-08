import streamlit as st
import json
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, BulkWriteError
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Upload MongoDB Atlas",
    page_icon="📤",
    layout="wide"
)

def connect_to_mongodb(connection_string):
    """
    Conecta ao MongoDB Atlas usando a string de conexão.
    """
    try:
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        # Testa a conexão
        client.admin.command('ping')
        return client, None
    except ConnectionFailure as e:
        return None, f"Erro ao conectar ao MongoDB: {str(e)}"
    except Exception as e:
        return None, f"Erro inesperado: {str(e)}"

def validate_json_structure(data):
    """
    Valida a estrutura básica dos documentos JSON.
    """
    required_fields = ['idAtendimento', 'cnsPaciente', 'dataHoraAtendimento', 'tipoAtendimento']
    
    if not isinstance(data, list):
        return False, "O arquivo deve conter uma lista (array) de documentos."
    
    if len(data) != 10:
        return False, f"O arquivo deve conter exatamente 10 registros. Encontrados: {len(data)}"
    
    for idx, doc in enumerate(data, 1):
        if not isinstance(doc, dict):
            return False, f"Documento {idx} não é um objeto JSON válido."
        
        for field in required_fields:
            if field not in doc:
                return False, f"Documento {idx}: campo obrigatório '{field}' não encontrado."
    
    return True, "Estrutura validada com sucesso!"

def insert_documents(client, database_name, collection_name, documents):
    """
    Insere os documentos na coleção do MongoDB.
    """
    try:
        db = client[database_name]
        collection = db[collection_name]
        
        # Insere os documentos
        result = collection.insert_many(documents)
        
        return True, result.inserted_ids, None
    except BulkWriteError as e:
        return False, None, f"Erro ao inserir documentos: {e.details}"
    except Exception as e:
        return False, None, f"Erro inesperado: {str(e)}"

# Interface Principal
def main():
    st.title("📤 Upload de Atendimentos para MongoDB Atlas")
    st.markdown("---")
    
    # Informações sobre o sistema
    with st.expander("ℹ️ Como usar este sistema"):
        st.markdown("""
        ### Instruções de Uso:
        
        1. **Configure a Conexão**: Insira sua string de conexão do MongoDB Atlas
        2. **Faça Upload do Arquivo**: Selecione um arquivo `.txt` ou `.json` contendo exatamente 10 registros
        3. **Valide os Dados**: O sistema verificará automaticamente a estrutura
        4. **Insira no MongoDB**: Clique no botão para enviar os dados
        
        ### Formato Esperado:
        - Arquivo de texto contendo um array JSON
        - Exatamente 10 documentos
        - Cada documento deve ter os campos obrigatórios: `idAtendimento`, `cnsPaciente`, `dataHoraAtendimento`, `tipoAtendimento`
        
        ### String de Conexão:
        ```
        mongodb+srv://<usuario>:<senha>@<cluster>.mongodb.net/?retryWrites=true&w=majority
        ```
        """)
    
    st.markdown("---")
    
    # Seção 1: Configuração da Conexão
    st.header("1️⃣ Configuração da Conexão")
    
    # Campo para string de conexão
    connection_string = st.text_input(
        "String de Conexão MongoDB Atlas:",
        value="",
        type="password",
        placeholder="mongodb+srv://usuario:senha@cluster.mongodb.net/?retryWrites=true&w=majority",
        help="Cole aqui sua string de conexão completa do MongoDB Atlas (incluindo usuário e senha)"
    )
    
    # Botão alternativo para mostrar/ocultar senha
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.caption("💡 **Dica:** A string deve incluir usuário e senha. Exemplo: `mongodb+srv://usuario:senha@cluster.mongodb.net/`")
    
    with col2:
        test_connection = st.button("🔌 Testar Conexão", use_container_width=True)
    
    # Configurações do banco e coleção
    col1, col2 = st.columns(2)
    
    with col1:
        database_name = st.text_input(
            "Nome do Database:",
            value="context",
            help="Nome do database no MongoDB Atlas"
        )
    
    with col2:
        collection_name = st.text_input(
            "Nome da Coleção:",
            value="SaudeTeste",
            help="Nome da coleção onde os dados serão inseridos"
        )
    
    # Testa a conexão
    if test_connection:
        if not connection_string:
            st.error("❌ Por favor, insira a string de conexão primeiro.")
        else:
            with st.spinner("Testando conexão..."):
                client, error = connect_to_mongodb(connection_string)
                
                if error:
                    st.error(f"❌ {error}")
                else:
                    st.success("✅ Conexão estabelecida com sucesso!")
                    
                    # Mostra informações do banco
                    try:
                        db = client[database_name]
                        collections = db.list_collection_names()
                        
                        st.info(f"📊 Database '{database_name}' possui {len(collections)} coleção(ões)")
                        
                        if collection_name in collections:
                            collection = db[collection_name]
                            count = collection.count_documents({})
                            st.success(f"✅ Coleção '{collection_name}' existe e possui {count} documento(s)")
                        else:
                            st.warning(f"⚠️ Coleção '{collection_name}' será criada ao inserir os documentos")
                    except Exception as e:
                        st.error(f"❌ Erro ao verificar database: {str(e)}")
                    
                    client.close()
    
    st.markdown("---")
    
    # Seção 2: Upload do Arquivo
    st.header("2️⃣ Upload do Arquivo JSON")
    
    uploaded_file = st.file_uploader(
        "Selecione o arquivo contendo os 10 registros:",
        type=['txt', 'json'],
        help="Arquivo de texto contendo um array JSON com exatamente 10 documentos"
    )
    
    if uploaded_file is not None:
        try:
            # Lê o conteúdo do arquivo
            file_content = uploaded_file.read().decode('utf-8')
            
            # Tenta fazer o parse do JSON
            try:
                documents = json.loads(file_content)
            except json.JSONDecodeError as e:
                st.error(f"❌ Erro ao fazer parse do JSON: {str(e)}")
                st.stop()
            
            # Valida a estrutura
            is_valid, message = validate_json_structure(documents)
            
            if not is_valid:
                st.error(f"❌ {message}")
                st.stop()
            else:
                st.success(f"✅ {message}")
            
            # Mostra preview dos dados
            st.subheader("📋 Preview dos Dados")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Documentos", len(documents))
            
            with col2:
                tipos = set([doc.get('tipoAtendimento', 'N/A') for doc in documents])
                st.metric("Tipos de Atendimento", len(tipos))
            
            with col3:
                pendentes = sum(1 for doc in documents if doc.get('dadosClinicosGerais', {}).get('statusRegistroBlockchain') == 'Pendente de Validação')
                st.metric("Status Pendente", pendentes)
            
            # Tabela resumida
            st.write("**Resumo dos Atendimentos:**")
            
            resumo_data = []
            for doc in documents:
                resumo_data.append({
                    "ID": doc.get('idAtendimento', 'N/A'),
                    "Tipo": doc.get('tipoAtendimento', 'N/A'),
                    "Data": doc.get('dataHoraAtendimento', 'N/A'),
                    "Unidade": doc.get('unidadeSaude', {}).get('nome', 'N/A'),
                    "Status": doc.get('dadosClinicosGerais', {}).get('statusRegistroBlockchain', 'N/A')
                })
            
            st.dataframe(resumo_data, use_container_width=True)
            
            # Expander com JSON completo
            with st.expander("🔍 Ver JSON Completo"):
                st.json(documents)
            
            st.markdown("---")
            
            # Seção 3: Inserir no MongoDB
            st.header("3️⃣ Inserir no MongoDB Atlas")
            
            st.warning("⚠️ **ATENÇÃO**: Esta ação irá inserir os 10 documentos no MongoDB. Confirme antes de prosseguir.")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                insert_button = st.button("📤 Inserir Documentos", type="primary")
            
            with col2:
                if st.button("🔄 Resetar"):
                    st.rerun()
            
            # Executa a inserção
            if insert_button:
                if not connection_string:
                    st.error("❌ Por favor, configure a string de conexão primeiro.")
                elif not database_name or not collection_name:
                    st.error("❌ Por favor, informe o nome do database e da coleção.")
                else:
                    with st.spinner("Inserindo documentos no MongoDB..."):
                        # Conecta ao MongoDB
                        client, error = connect_to_mongodb(connection_string)
                        
                        if error:
                            st.error(f"❌ {error}")
                        else:
                            # Insere os documentos
                            success, inserted_ids, error = insert_documents(
                                client, 
                                database_name, 
                                collection_name, 
                                documents
                            )
                            
                            if success:
                                st.success(f"✅ {len(inserted_ids)} documentos inseridos com sucesso!")
                                
                                # Mostra IDs inseridos
                                with st.expander("🔍 Ver IDs Inseridos"):
                                    for idx, obj_id in enumerate(inserted_ids, 1):
                                        st.code(f"Documento {idx}: {obj_id}")
                                
                                # Log da operação
                                st.info(f"""
                                📊 **Resumo da Operação:**
                                - Database: `{database_name}`
                                - Coleção: `{collection_name}`
                                - Documentos inseridos: `{len(inserted_ids)}`
                                - Data/Hora: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
                                """)
                                
                                st.balloons()
                            else:
                                st.error(f"❌ Erro ao inserir documentos: {error}")
                            
                            client.close()
        
        except Exception as e:
            st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
    else:
        st.info("👆 Faça upload de um arquivo para continuar.")

if __name__ == "__main__":
    # Verifica se pymongo está instalado
    try:
        import pymongo
    except ImportError:
        st.error("""
        ⚠️ A biblioteca `pymongo` não foi encontrada.
        Por favor, instale-a usando:
        ```
        pip install pymongo
        ```
        """)
        st.stop()
    
    main()