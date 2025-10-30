import streamlit as st
import hashlib
import datetime
import json
import pandas as pd
import time


class Block:
    def __init__(self, index, timestamp, data, previous_hash, difficulty=0):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.difficulty = difficulty
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        hash_string = str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash) + str(self.nonce)
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def mine_block(self, difficulty):
        """Minera o bloco encontrando um hash com o número especificado de zeros à esquerda."""
        target = "0" * difficulty
        start_time = time.time()
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        
        end_time = time.time()
        mining_time = end_time - start_time
        
        return mining_time, self.nonce
    
    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': str(self.timestamp),
            'data': self.data,
            'previous_hash': self.previous_hash,
            'hash': self.hash,
            'nonce': self.nonce,
            'difficulty': self.difficulty
        }


class Blockchain:
    def __init__(self, difficulty=0):
        self.difficulty = difficulty
        self.chain = [self.create_genesis_block()]
    
    def create_genesis_block(self):
        return Block(0, datetime.datetime.now(), "Genesis Block", "0", self.difficulty)
    
    def get_latest_block(self):
        return self.chain[-1]
    
    def add_block(self, data, mine=False):
        index = len(self.chain)
        timestamp = datetime.datetime.now()
        previous_hash = self.get_latest_block().hash
        new_block = Block(index, timestamp, data, previous_hash, self.difficulty)
        
        mining_time = 0
        nonce = 0
        
        if mine and self.difficulty > 0:
            mining_time, nonce = new_block.mine_block(self.difficulty)
        
        self.chain.append(new_block)
        return mining_time, nonce
    
    def is_valid(self):
        if self.chain[0].previous_hash != "0":
            return False
        
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
            
            # Verifica se o bloco foi minerado corretamente (se tiver dificuldade)
            if current_block.difficulty > 0:
                target = "0" * current_block.difficulty
                if current_block.hash[:current_block.difficulty] != target:
                    return False
        
        return True
    
    def to_json(self):
        return json.dumps([block.to_dict() for block in self.chain], indent=4)


# Configuração da página
st.set_page_config(
    page_title="Blockchain Educacional",
    page_icon="⛓️",
    layout="wide"
)

# Inicializa a blockchain no session_state
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = Blockchain(difficulty=0)
if 'mining_stats' not in st.session_state:
    st.session_state.mining_stats = []

blockchain = st.session_state.blockchain

# Título e descrição
st.title("⛓️ Blockchain Educacional Interativa")
st.markdown("""
Esta aplicação demonstra o funcionamento de uma blockchain de forma didática e interativa.
Explore as diferentes funcionalidades para entender como funciona essa tecnologia revolucionária!
""")

# Sidebar com menu de navegação
st.sidebar.title("📚 Menu")
opcao = st.sidebar.radio(
    "Escolha uma opção:",
    [
        "🏠 Visão Geral",
        "➕ Adicionar Transação",
        "⛏️ Minerar Bloco",
        "🔍 Visualizar Blockchain",
        "✅ Validar Integridade",
        "🔧 Simular Adulteração",
        "📊 Estatísticas",
        "📥 Exportar JSON",
        "❓ Como Funciona"
    ]
)

# ===== VISÃO GERAL =====
if opcao == "🏠 Visão Geral":
    st.header("Visão Geral da Blockchain")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Blocos", len(blockchain.chain))
    
    with col2:
        st.metric("Status", "✅ Válida" if blockchain.is_valid() else "❌ Inválida")
    
    with col3:
        st.metric("Último Bloco", f"#{blockchain.get_latest_block().index}")
    
    with col4:
        st.metric("Dificuldade Atual", blockchain.difficulty)
    
    st.divider()
    
    st.subheader("📦 Último Bloco Adicionado")
    if len(blockchain.chain) > 0:
        last_block = blockchain.get_latest_block()
        st.code(f"""
Índice: {last_block.index}
Data/Hora: {last_block.timestamp}
Dados: {last_block.data}
Hash: {last_block.hash}
Hash Anterior: {last_block.previous_hash[:32]}...
Nonce: {last_block.nonce}
Dificuldade: {last_block.difficulty} zeros
        """)

# ===== ADICIONAR TRANSAÇÃO =====
elif opcao == "➕ Adicionar Transação":
    st.header("Adicionar Nova Transação")
    
    st.info("💡 **Dica:** Cada transação será registrada permanentemente na blockchain!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        remetente = st.text_input("Remetente", placeholder="Ex: João")
        valor = st.number_input("Valor", min_value=0.01, step=0.01, format="%.2f")
    
    with col2:
        destinatario = st.text_input("Destinatário", placeholder="Ex: Maria")
        moeda = st.selectbox("Moeda", ["BRL", "USD", "EUR", "BTC"])
    
    if st.button("🚀 Adicionar à Blockchain", type="primary"):
        if remetente and destinatario and valor > 0:
            transacao = f"{remetente} transferiu {valor:.2f} {moeda} para {destinatario}"
            blockchain.add_block(transacao, mine=False)
            st.success(f"✅ Transação adicionada ao bloco #{len(blockchain.chain)-1}")
            st.balloons()
        else:
            st.error("⚠️ Por favor, preencha todos os campos corretamente!")

# ===== MINERAR BLOCO =====
elif opcao == "⛏️ Minerar Bloco":
    st.header("⛏️ Mineração de Bloco (Proof of Work)")
    
    st.markdown("""
    ### 🎯 O que é Mineração?
    
    A **mineração** é o processo de encontrar um hash válido que satisfaça certos critérios de dificuldade.
    O minerador testa diferentes valores de **nonce** até encontrar um hash que comece com o número
    especificado de zeros.
    
    **Por que isso é importante?**
    - 🔐 Torna a blockchain mais segura
    - ⏱️ Controla a velocidade de criação de blocos
    - 💪 Requer trabalho computacional (Proof of Work)
    - 🛡️ Dificulta ataques maliciosos
    """)
    
    st.divider()
    
    # Configuração da dificuldade
    col1, col2 = st.columns([2, 1])
    
    with col1:
        difficulty = st.slider(
            "🎚️ Dificuldade (Leading Zeros)",
            min_value=1,
            max_value=6,
            value=3,
            help="Número de zeros que o hash deve começar. Quanto maior, mais difícil!"
        )
        
        st.info(f"""
        **Dificuldade {difficulty}:** O hash deve começar com {"0" * difficulty}
        
        - Dificuldade 1: ~16 tentativas (rápido ⚡)
        - Dificuldade 2: ~256 tentativas (segundos ⏱️)
        - Dificuldade 3: ~4.096 tentativas (alguns segundos 🕐)
        - Dificuldade 4: ~65.536 tentativas (pode demorar ⏳)
        - Dificuldade 5+: Milhões de tentativas (muito demorado! 🐌)
        """)
    
    with col2:
        st.metric("Dificuldade Selecionada", f"{difficulty} zeros")
        st.metric("Tentativas Estimadas", f"~{16**difficulty:,}")
    
    st.divider()
    
    # Entrada de dados para o bloco
    st.subheader("📝 Dados do Bloco a ser Minerado")
    
    opcao_dados = st.radio(
        "Escolha o tipo de dados:",
        ["Transação", "Mensagem Personalizada"]
    )
    
    if opcao_dados == "Transação":
        col1, col2, col3 = st.columns(3)
        with col1:
            remetente = st.text_input("Remetente", placeholder="Ex: João")
        with col2:
            destinatario = st.text_input("Destinatário", placeholder="Ex: Maria")
        with col3:
            valor = st.number_input("Valor", min_value=0.01, step=0.01, format="%.2f")
        
        dados_bloco = f"{remetente} transferiu {valor:.2f} para {destinatario}"
    else:
        dados_bloco = st.text_area(
            "Mensagem",
            placeholder="Digite qualquer mensagem para ser gravada na blockchain...",
            height=100
        )
    
    st.divider()
    
    # Botão de mineração
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        minerar_btn = st.button("⛏️ COMEÇAR MINERAÇÃO", type="primary", use_container_width=True)
    
    if minerar_btn:
        if dados_bloco and dados_bloco.strip():
            # Atualiza a dificuldade da blockchain
            blockchain.difficulty = difficulty
            
            # Container para mostrar o progresso
            progress_container = st.container()
            
            with progress_container:
                st.markdown("### 🔄 Minerando...")
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Adiciona e minera o bloco
                mining_time, nonce = blockchain.add_block(dados_bloco, mine=True)
                
                progress_bar.progress(100)
                
                # Salva estatísticas
                st.session_state.mining_stats.append({
                    'bloco': len(blockchain.chain) - 1,
                    'dificuldade': difficulty,
                    'nonce': nonce,
                    'tempo': mining_time,
                    'tentativas': nonce + 1
                })
            
            # Mostra resultados
            st.success("✅ **BLOCO MINERADO COM SUCESSO!**")
            st.balloons()
            
            last_block = blockchain.get_latest_block()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("⏱️ Tempo de Mineração", f"{mining_time:.3f}s")
            with col2:
                st.metric("🔢 Nonce Encontrado", f"{nonce:,}")
            with col3:
                st.metric("🎯 Tentativas", f"{nonce + 1:,}")
            with col4:
                st.metric("📦 Bloco #", last_block.index)
            
            st.divider()
            
            # Mostra o bloco minerado
            st.subheader("📦 Detalhes do Bloco Minerado")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Dados:**")
                st.info(last_block.data)
                
                st.write("**Timestamp:**")
                st.code(last_block.timestamp)
                
                st.write("**Nonce:**")
                st.code(f"{last_block.nonce:,} (após {nonce + 1:,} tentativas)")
            
            with col2:
                st.write("**Hash Minerado:**")
                hash_display = last_block.hash
                # Destaca os zeros no início
                zeros_part = hash_display[:difficulty]
                rest_part = hash_display[difficulty:]
                st.markdown(f"<code style='color: #00ff00; font-weight: bold;'>{zeros_part}</code><code>{rest_part}</code>", unsafe_allow_html=True)
                
                st.write("**Hash Anterior:**")
                st.code(last_block.previous_hash[:32] + "...")
                
                st.write("**Dificuldade:**")
                st.code(f"{difficulty} zeros iniciais")
            
            # Explicação visual
            st.divider()
            st.markdown("### 🎓 O que aconteceu?")
            st.markdown(f"""
            1. **Início:** O minerador começou com nonce = 0
            2. **Tentativas:** Foram necessárias **{nonce + 1:,} tentativas** até encontrar um hash válido
            3. **Hash Válido:** O hash encontrado começa com **{difficulty} zeros**: `{"0" * difficulty}...`
            4. **Tempo:** Todo o processo levou **{mining_time:.3f} segundos**
            5. **Proof of Work:** Este trabalho computacional prova que o bloco foi minerado legitimamente
            """)
            
        else:
            st.error("⚠️ Por favor, insira dados para o bloco!")

# ===== VISUALIZAR BLOCKCHAIN =====
elif opcao == "🔍 Visualizar Blockchain":
    st.header("Visualizar Toda a Blockchain")
    
    visualizacao = st.radio("Modo de visualização:", ["Detalhada", "Tabela", "Diagrama"])
    
    if visualizacao == "Detalhada":
        for i, block in enumerate(blockchain.chain):
            with st.expander(f"📦 Bloco #{block.index} - {block.data[:50]}{'...' if len(block.data) > 50 else ''}", expanded=(i == len(blockchain.chain)-1)):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Índice:**", block.index)
                    st.write("**Timestamp:**", block.timestamp)
                    st.write("**Dados:**", block.data)
                    st.write("**Nonce:**", f"{block.nonce:,}")
                    st.write("**Dificuldade:**", f"{block.difficulty} zeros")
                
                with col2:
                    st.write("**Hash:**")
                    if block.difficulty > 0:
                        zeros_part = block.hash[:block.difficulty]
                        rest_part = block.hash[block.difficulty:]
                        st.markdown(f"<code style='color: #00ff00; font-weight: bold;'>{zeros_part}</code><code>{rest_part}</code>", unsafe_allow_html=True)
                    else:
                        st.code(block.hash, language="text")
                    
                    st.write("**Hash Anterior:**")
                    st.code(block.previous_hash if block.previous_hash != "0" else "Genesis Block", language="text")
    
    elif visualizacao == "Tabela":
        df_data = []
        for block in blockchain.chain:
            df_data.append({
                "Bloco": block.index,
                "Dados": block.data[:40] + "..." if len(block.data) > 40 else block.data,
                "Nonce": f"{block.nonce:,}",
                "Dificuldade": block.difficulty,
                "Hash": block.hash[:16] + "...",
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    else:  # Diagrama
        st.markdown("### 📊 Estrutura da Blockchain")
        for i, block in enumerate(blockchain.chain):
            if i > 0:
                st.markdown("⬇️")
            
            color = "green" if i == 0 else "blue"
            difficulty_badge = f" | Dificuldade: {block.difficulty}" if block.difficulty > 0 else ""
            st.markdown(f"""
            <div style="border: 2px solid {color}; padding: 15px; border-radius: 10px; background-color: rgba(0,123,255,0.1);">
                <h4>Bloco #{block.index}{difficulty_badge}</h4>
                <p><strong>Dados:</strong> {block.data}</p>
                <p><strong>Nonce:</strong> {block.nonce:,}</p>
                <p><strong>Hash:</strong> <code>{block.hash[:32]}...</code></p>
            </div>
            """, unsafe_allow_html=True)

# ===== VALIDAR INTEGRIDADE =====
elif opcao == "✅ Validar Integridade":
    st.header("Validar Integridade da Blockchain")
    
    st.markdown("""
    A validação verifica se:
    1. ✅ O bloco gênesis está intacto
    2. ✅ Todos os hashes foram calculados corretamente
    3. ✅ Cada bloco aponta para o hash correto do bloco anterior
    4. ✅ Blocos minerados atendem à dificuldade especificada
    """)
    
    if st.button("🔍 Executar Validação", type="primary"):
        with st.spinner("Validando blockchain..."):
            time.sleep(1)  # Simula processamento
            
            is_valid = blockchain.is_valid()
            
            if is_valid:
                st.success("✅ **BLOCKCHAIN VÁLIDA!** Todos os blocos estão íntegros e conectados corretamente.")
                st.balloons()
            else:
                st.error("❌ **BLOCKCHAIN INVÁLIDA!** Detectada adulteração ou inconsistência nos blocos.")
            
            # Validação detalhada
            st.divider()
            st.subheader("Detalhes da Validação")
            
            for i in range(len(blockchain.chain)):
                block = blockchain.chain[i]
                
                if i == 0:
                    check = block.previous_hash == "0"
                    st.write(f"**Bloco {i}:** {'✅' if check else '❌'} Bloco gênesis válido")
                else:
                    previous_block = blockchain.chain[i-1]
                    hash_valid = block.hash == block.calculate_hash()
                    link_valid = block.previous_hash == previous_block.hash
                    
                    # Verifica dificuldade
                    difficulty_valid = True
                    if block.difficulty > 0:
                        target = "0" * block.difficulty
                        difficulty_valid = block.hash[:block.difficulty] == target
                    
                    st.write(f"**Bloco {i}:**")
                    st.write(f"  {'✅' if hash_valid else '❌'} Hash calculado corretamente")
                    st.write(f"  {'✅' if link_valid else '❌'} Conectado ao bloco anterior")
                    if block.difficulty > 0:
                        st.write(f"  {'✅' if difficulty_valid else '❌'} Dificuldade de mineração válida ({block.difficulty} zeros)")

# ===== SIMULAR ADULTERAÇÃO =====
elif opcao == "🔧 Simular Adulteração":
    st.header("Simular Adulteração de Dados")
    
    st.warning("""
    ⚠️ **Experimento Educacional**
    
    Esta seção demonstra o que acontece quando alguém tenta adulterar dados na blockchain.
    Você verá como a validação detecta imediatamente a manipulação!
    """)
    
    if len(blockchain.chain) > 1:
        bloco_selecionado = st.selectbox(
            "Escolha um bloco para adulterar:",
            range(1, len(blockchain.chain)),
            format_func=lambda x: f"Bloco #{x}: {blockchain.chain[x].data}"
        )
        
        st.subheader(f"📦 Dados Originais do Bloco #{bloco_selecionado}")
        st.code(blockchain.chain[bloco_selecionado].data)
        
        novos_dados = st.text_area(
            "Digite os novos dados (adulterados):",
            placeholder="Ex: Dados fraudulentos..."
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💥 Adulterar Dados", type="secondary"):
                if novos_dados:
                    blockchain.chain[bloco_selecionado].data = novos_dados
                    st.error(f"⚠️ Bloco #{bloco_selecionado} foi adulterado!")
                    st.info("🔍 Execute a validação para ver o resultado...")
                else:
                    st.warning("Digite os novos dados primeiro!")
        
        with col2:
            if st.button("♻️ Restaurar Blockchain Original"):
                st.session_state.blockchain = Blockchain(difficulty=0)
                st.session_state.mining_stats = []
                st.success("✅ Blockchain restaurada ao estado inicial!")
                st.rerun()
    else:
        st.info("Adicione mais blocos antes de simular adulteração!")

# ===== ESTATÍSTICAS =====
elif opcao == "📊 Estatísticas":
    st.header("Estatísticas da Blockchain")
    
    total_blocos = len(blockchain.chain)
    total_caracteres = sum(len(block.data) for block in blockchain.chain)
    total_tentativas = sum(block.nonce + 1 for block in blockchain.chain)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Blocos", total_blocos)
    
    with col2:
        st.metric("Blocos Minerados", sum(1 for b in blockchain.chain if b.difficulty > 0))
    
    with col3:
        st.metric("Total de Tentativas", f"{total_tentativas:,}")
    
    with col4:
        tempo_decorrido = (blockchain.get_latest_block().timestamp - blockchain.chain[0].timestamp).total_seconds()
        st.metric("Tempo Total (seg)", f"{tempo_decorrido:.1f}")
    
    st.divider()
    
    # Estatísticas de Mineração
    if st.session_state.mining_stats:
        st.subheader("⛏️ Histórico de Mineração")
        
        mining_df = pd.DataFrame(st.session_state.mining_stats)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Tentativas por Bloco**")
            chart_data = mining_df[['bloco', 'tentativas']].set_index('bloco')
            st.bar_chart(chart_data)
        
        with col2:
            st.markdown("**Tempo de Mineração (segundos)**")
            chart_data = mining_df[['bloco', 'tempo']].set_index('bloco')
            st.line_chart(chart_data)
        
        st.dataframe(
            mining_df.rename(columns={
                'bloco': 'Bloco #',
                'dificuldade': 'Dificuldade',
                'nonce': 'Nonce',
                'tempo': 'Tempo (s)',
                'tentativas': 'Tentativas'
            }),
            use_container_width=True,
            hide_index=True
        )
    
    st.divider()
    
    st.subheader("📈 Distribuição de Nonces")
    nonce_data = pd.DataFrame({
        'Bloco': [f"#{b.index}" for b in blockchain.chain],
        'Nonce': [b.nonce for b in blockchain.chain]
    })
    st.bar_chart(nonce_data.set_index('Bloco'))

# ===== EXPORTAR JSON =====
elif opcao == "📥 Exportar JSON":
    st.header("Exportar Blockchain em JSON")
    
    st.markdown("""
    Exporte toda a blockchain em formato JSON para:
    - 📄 Análise externa
    - 💾 Backup dos dados
    - 🔄 Compartilhamento
    - 📚 Documentação
    """)
    
    json_data = blockchain.to_json()
    
    st.code(json_data, language="json")
    
    st.download_button(
        label="⬇️ Download JSON",
        data=json_data,
        file_name=f"blockchain_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

# ===== COMO FUNCIONA =====
elif opcao == "❓ Como Funciona":
    st.header("Como Funciona uma Blockchain?")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📚 Conceitos Básicos", "🔗 Encadeamento", "⛏️ Mineração", "🔐 Segurança", "💡 Aplicações"])
    
    with tab1:
        st.subheader("O que é Blockchain?")
        st.markdown("""
        Uma **blockchain** é uma estrutura de dados que armazena informações em blocos conectados sequencialmente,
        formando uma cadeia imutável e verificável.
        
        **Componentes de um Bloco:**
        - **Índice:** Posição do bloco na cadeia
        - **Timestamp:** Data e hora de criação
        - **Dados:** Informação armazenada (transações, documentos, etc.)
        - **Hash:** Identificador único do bloco (como uma impressão digital)
        - **Hash Anterior:** Referência ao bloco anterior (cria o encadeamento)
        - **Nonce:** Número usado na mineração (Proof of Work)
        - **Dificuldade:** Quantos zeros o hash deve ter no início
        
        **Bloco Gênesis:** É o primeiro bloco da cadeia, criado manualmente sem predecessor.
        """)
    
    with tab2:
        st.subheader("Como Funciona o Encadeamento?")
        st.markdown("""
        Cada bloco contém o hash do bloco anterior, criando uma corrente inquebrável:
        
        ```
        Bloco 0 (Gênesis)          Bloco 1                    Bloco 2
        ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
        │ Dados: Genesis  │        │ Dados: Trans. 1 │        │ Dados: Trans. 2 │
        │ Hash Prev.: "0" │───────▶│ Hash Prev.: ABC │───────▶│ Hash Prev.: XYZ │
        │ Hash: ABC...    │        │ Hash: XYZ...    │        │ Hash: 123...    │
        │ Nonce: 0        │        │ Nonce: 4582     │        │ Nonce: 12049    │
        └─────────────────┘        └─────────────────┘        └─────────────────┘
        ```
        
        **Função Hash (SHA-256):**
        - Transforma qualquer dado em uma string única de 64 caracteres
        - Qualquer alteração nos dados gera um hash completamente diferente
        - É impossível reverter o processo (função unidirecional)
        """)
    
    with tab3:
        st.subheader("⛏️ O que é Mineração?")
        st.markdown("""
        **Mineração** é o processo de encontrar um hash válido através de tentativa e erro.
        
        **Como funciona:**
        1. O minerador começa com nonce = 0
        2. Calcula o hash do bloco (incluindo o nonce)
        3. Verifica se o hash começa com o número exigido de zeros
        4. Se não, incrementa o nonce e tenta novamente
        5. Repete até encontrar um hash válido
        
        **Exemplo com Dificuldade 3:**
        ```
        Tentativa 1: nonce=0    → hash=a4f2b8c... ❌
        Tentativa 2: nonce=1    → hash=7e9d1a2... ❌
        ...
        Tentativa 4096: nonce=4095 → hash=000a1f3... ✅
        ```
        
        **Por que isso importa?**
        - 🛡️ **Segurança:** Torna muito custoso criar blocos falsos
        - ⏱️ **Controle:** Regula a velocidade de criação de blocos
        - 💰 **Incentivo:** Mineradores são recompensados pelo trabalho
        - 🔐 **Proof of Work:** Prova que trabalho computacional foi realizado
        
        **Dificuldade:**
        - Dificuldade 1: Hash deve começar com 1 zero (0...)
        - Dificuldade 2: Hash deve começar com 2 zeros (00...)
        - Dificuldade 3: Hash deve começar com 3 zeros (000...)
        - A cada zero adicional, a dificuldade aumenta 16x!
        
        **Comparação com Bitcoin:**
        - Bitcoin usa dificuldade ~19-20 zeros
        - Requer hardware especializado (ASICs)
        - Consome muita energia elétrica
        - Ajusta dificuldade a cada 2016 blocos
        """)
    
    with tab4:
        st.subheader("Por que é Seguro?")
        st.markdown("""
        A blockchain é resistente a adulteração por várias razões:
        
        **1. Imutabilidade Criptográfica:**
        - Se alguém mudar os dados de um bloco, o hash dele muda
        - Isso quebra o encadeamento com o próximo bloco
        - A validação detecta imediatamente a inconsistência
        
        **2. Proof of Work (Prova de Trabalho):**
        - Criar um bloco válido requer muito trabalho computacional
        - Adulterar um bloco antigo requer:
          - Reminar esse bloco (trabalho computacional)
          - Reminar TODOS os blocos seguintes (ainda mais trabalho!)
          - Fazer isso mais rápido que a rede honesta cria novos blocos
        - **Praticamente impossível** em blockchains grandes
        
        **3. Encadeamento:**
        - Cada bloco "trava" todos os anteriores
        - Quanto mais antigo o bloco, mais protegido ele está
        - Blocos recentes têm menos proteção
        
        **4. Distribuição (em blockchain real):**
        - Cópias da blockchain existem em milhares de computadores
        - Consenso determina qual versão é válida
        - Impossível controlar a maioria das cópias simultaneamente
        
        **Ataque dos 51%:**
        - Um atacante precisaria controlar >50% do poder computacional
        - Custo proibitivo em redes grandes como Bitcoin
        - Por isso blockchains maiores são mais seguras
        """)
    
    with tab5:
        st.subheader("Aplicações Práticas")
        st.markdown("""
        **Criptomoedas:**
        - Bitcoin, Ethereum, etc.
        - Registro de transações financeiras
        - Eliminação de intermediários bancários
        
        **Contratos Inteligentes (Smart Contracts):**
        - Acordos automáticos e auto-executáveis
        - Eliminação de intermediários jurídicos
        - Exemplo: Seguro que paga automaticamente
        
        **Cadeia de Suprimentos:**
        - Rastreamento de produtos do fabricante ao consumidor
        - Garantia de autenticidade e origem
        - Combate à falsificação
        
        **Documentos e Certificados:**
        - Diplomas e certificados digitais
        - Registro de propriedade imobiliária
        - Cartórios descentralizados
        
        **Saúde:**
        - Prontuários médicos seguros e portáteis
        - Rastreabilidade de medicamentos
        - Compartilhamento seguro entre hospitais
        
        **Votação Eletrônica:**
        - Sistemas eleitorais transparentes e auditáveis
        - Impossível alterar votos após registro
        - Cada eleitor pode verificar seu voto
        
        **NFTs (Non-Fungible Tokens):**
        - Arte digital
        - Itens de jogos
        - Propriedade de ativos únicos
        
        **DeFi (Finanças Descentralizadas):**
        - Empréstimos sem bancos
        - Exchanges descentralizadas
        - Yield farming e staking
        """)

# Footer
st.sidebar.divider()
st.sidebar.markdown("""
### 📖 Sobre
Esta aplicação é uma ferramenta educacional para demonstrar os conceitos fundamentais de blockchain e mineração.

**Desenvolvido com:**
- Python 🐍
- Streamlit 🎈
- SHA-256 🔐
- Proof of Work ⛏️

**Recursos:**
- Mineração interativa
- Validação em tempo real
- Estatísticas detalhadas
- Tutorial completo
""")