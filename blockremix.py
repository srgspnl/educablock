import streamlit as st
import json
from web3 import Web3
from eth_account import Account
import time

# Configurações
ALCHEMY_URL = "https://eth-sepolia.g.alchemy.com/v2/lda58Tw_56pU42krLOmDH"
CONTRACT_ADDRESS = "0x15A04197f89e508389513eeE46320A02A2DDEDEb"

CONTRACT_ABI = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "fromContract",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "EtherTransferred",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "from",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "FundsReceived",
        "type": "event"
    },
    {
        "inputs": [
            {
                "internalType": "address payable",
                "name": "_to",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "_amountInWei",
                "type": "uint256"
            }
        ],
        "name": "transferFromContract",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "stateMutability": "payable",
        "type": "receive"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_account",
                "type": "address"
            }
        ],
        "name": "getAccountBalance",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getContractBalance",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

ACCOUNT_ADDRESSES = [
    "0x7313fb7f6e6D7D4413B172B5eF9838421Aba2998",
    "0x5e1C1D61b931a3D178c1Bf233466f93e96D8d50c",
    "0x00009b53F7bc3aBB58D9eaf72121D7161DCfC216"
]


class EthereumContractManager:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))
        if not self.w3.is_connected():
            raise Exception("Falha ao conectar com a rede Ethereum")
        
        self.contract = self.w3.eth.contract(
            address=CONTRACT_ADDRESS,
            abi=CONTRACT_ABI
        )

    def get_account_from_private_key(self, private_key):
        try:
            if private_key.startswith('0x'):
                private_key = private_key[2:]
            return Account.from_key(private_key)
        except Exception as e:
            return None

    def get_balance(self, account_address):
        try:
            balance_wei = self.contract.functions.getAccountBalance(account_address).call()
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            return balance_wei, balance_eth
        except Exception as e:
            return 0, 0

    def get_contract_balance(self):
        try:
            balance_wei = self.contract.functions.getContractBalance().call()
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            return balance_wei, balance_eth
        except Exception as e:
            return 0, 0

    def get_contract_eth_balance(self):
        try:
            balance_wei = self.w3.eth.get_balance(CONTRACT_ADDRESS)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            return balance_wei, balance_eth
        except Exception as e:
            return 0, 0

    def get_account_eth_balance(self, account_address):
        try:
            balance_wei = self.w3.eth.get_balance(account_address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            return balance_wei, balance_eth
        except Exception as e:
            return 0, 0

    def get_owner(self):
        try:
            return self.contract.functions.owner().call()
        except Exception as e:
            return None

    def send_transaction_safe(self, signed_txn):
        try:
            raw_tx = signed_txn.raw_transaction
            return self.w3.eth.send_raw_transaction(raw_tx)
        except Exception as e:
            st.error(f"Erro ao enviar transação: {str(e)}")
            return None

    def transfer_from_contract(self, private_key, to_address, amount_eth):
        try:
            account = self.get_account_from_private_key(private_key)
            if not account:
                return False, "Chave privada inválida"

            amount_wei = self.w3.to_wei(amount_eth, 'ether')
            contract_balance_wei, _ = self.get_contract_balance()
            
            if contract_balance_wei < amount_wei:
                return False, f"Saldo insuficiente no contrato"

            transaction = self.contract.functions.transferFromContract(
                to_address,
                amount_wei
            ).build_transaction({
                'from': account.address,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(account.address),
            })

            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = self.send_transaction_safe(signed_txn)

            if tx_hash is None:
                return False, "Falha ao enviar transação"

            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            if tx_receipt.status == 1:
                return True, f"Transferência realizada! Hash: {tx_hash.hex()}"
            else:
                return False, "Transação falhou"

        except Exception as e:
            return False, f"Erro: {str(e)}"

    def transfer_eth_to_contract(self, private_key, amount_eth):
        try:
            account = self.get_account_from_private_key(private_key)
            if not account:
                return False, "Chave privada inválida"

            account_balance_wei, account_balance_eth = self.get_account_eth_balance(account.address)
            amount_wei = self.w3.to_wei(amount_eth, 'ether')

            if account_balance_wei < amount_wei:
                return False, f"Saldo insuficiente! Você tem {account_balance_eth:.6f} ETH"

            transaction = {
                'to': CONTRACT_ADDRESS,
                'value': amount_wei,
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(account.address),
            }

            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = self.send_transaction_safe(signed_txn)

            if tx_hash is None:
                return False, "Falha ao enviar transação"

            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            if tx_receipt.status == 1:
                return True, f"ETH enviado com sucesso! Hash: {tx_hash.hex()}"
            else:
                return False, "Transação falhou"

        except Exception as e:
            return False, f"Erro: {str(e)}"


# Configuração da página
st.set_page_config(
    page_title="Ethereum Contract Manager",
    page_icon="⛓️",
    layout="wide"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #627EEA;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #627EEA;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização do estado
if 'manager' not in st.session_state:
    try:
        st.session_state.manager = EthereumContractManager()
        st.session_state.connected = True
    except Exception as e:
        st.session_state.connected = False
        st.error(f"Erro ao conectar: {str(e)}")

# Header
st.markdown('<p class="main-header">⛓️ Ethereum Contract Manager</p>', unsafe_allow_html=True)

if st.session_state.connected:
    manager = st.session_state.manager
    
    # Informações do contrato
    with st.container():
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📋 Endereço do Contrato:**")
            st.code(CONTRACT_ADDRESS, language="text")
            
        with col2:
            owner = manager.get_owner()
            st.markdown("**👑 Owner do Contrato:**")
            st.code(owner if owner else "Não disponível", language="text")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard", 
        "💸 Transferir do Contrato", 
        "📤 Enviar para Contrato",
        "🔍 Consultar Conta"
    ])
    
    # Tab 1: Dashboard
    with tab1:
        st.subheader("💰 Saldos do Sistema")
        
        # Métricas do contrato
        col1, col2, col3 = st.columns(3)
        
        contract_balance_wei, contract_balance_eth = manager.get_contract_balance()
        contract_eth_wei, contract_eth_eth = manager.get_contract_eth_balance()
        
        with col1:
            st.metric(
                label="💼 Saldo Interno do Contrato",
                value=f"{contract_balance_eth:.6f} ETH",
                delta=f"{contract_balance_wei} Wei"
            )
        
        with col2:
            st.metric(
                label="🏦 Saldo Real (Blockchain)",
                value=f"{contract_eth_eth:.6f} ETH",
                delta=f"{contract_eth_wei} Wei"
            )
        
        with col3:
            chain_id = manager.w3.eth.chain_id
            st.metric(
                label="🌐 Rede",
                value="Sepolia",
                delta=f"Chain ID: {chain_id}"
            )
        
        st.markdown("---")
        
        # Tabela de contas
        st.subheader("👥 Contas Registradas")
        
        for i, address in enumerate(ACCOUNT_ADDRESSES, 1):
            with st.expander(f"👤 Account {i}: {address[:10]}...{address[-8:]}"):
                col1, col2 = st.columns(2)
                
                balance_wei, balance_eth = manager.get_balance(address)
                eth_balance_wei, eth_balance_eth = manager.get_account_eth_balance(address)
                
                with col1:
                    st.metric("💰 Saldo no Contrato", f"{balance_eth:.6f} ETH")
                    st.caption(f"{balance_wei} Wei")
                
                with col2:
                    st.metric("🏦 Saldo Real (Blockchain)", f"{eth_balance_eth:.6f} ETH")
                    st.caption(f"{eth_balance_wei} Wei")
                
                st.code(address, language="text")
        
        if st.button("🔄 Atualizar Dados", type="primary"):
            st.rerun()
    
    # Tab 2: Transferir do Contrato
    with tab2:
        st.subheader("💸 Transferir ETH do Contrato")
        
        st.warning("⚠️ Apenas o owner pode realizar esta operação!")
        
        with st.form("transfer_from_contract_form"):
            private_key = st.text_input(
                "🔑 Chave Privada (sem 0x)",
                type="password",
                help="Digite sua chave privada sem o prefixo 0x"
            )
            
            to_address = st.selectbox(
                "📍 Conta de Destino",
                options=ACCOUNT_ADDRESSES,
                format_func=lambda x: f"{x[:10]}...{x[-8:]}"
            )
            
            amount = st.number_input(
                "💰 Valor em ETH",
                min_value=0.0,
                step=0.001,
                format="%.6f"
            )
            
            submitted = st.form_submit_button("🚀 Transferir", type="primary")
            
            if submitted:
                if not private_key:
                    st.error("❌ Digite a chave privada!")
                elif amount <= 0:
                    st.error("❌ O valor deve ser maior que zero!")
                else:
                    with st.spinner("⏳ Processando transação..."):
                        success, message = manager.transfer_from_contract(
                            private_key,
                            to_address,
                            amount
                        )
                        
                        if success:
                            st.success(f"✅ {message}")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
    
    # Tab 3: Enviar para Contrato
    with tab3:
        st.subheader("📤 Enviar ETH para o Contrato")
        
        st.info("ℹ️ Qualquer conta pode enviar ETH para o contrato")
        
        with st.form("send_to_contract_form"):
            private_key_send = st.text_input(
                "🔑 Chave Privada (sem 0x)",
                type="password",
                help="Digite sua chave privada sem o prefixo 0x"
            )
            
            # Mostrar endereço da conta se a chave for válida
            if private_key_send:
                account = manager.get_account_from_private_key(private_key_send)
                if account:
                    st.info(f"👤 Sua conta: {account.address}")
                    balance_wei, balance_eth = manager.get_account_eth_balance(account.address)
                    st.metric("💰 Saldo Disponível", f"{balance_eth:.6f} ETH")
            
            amount_send = st.number_input(
                "💰 Valor em ETH",
                min_value=0.0,
                step=0.001,
                format="%.6f",
                key="amount_send"
            )
            
            submitted_send = st.form_submit_button("📤 Enviar", type="primary")
            
            if submitted_send:
                if not private_key_send:
                    st.error("❌ Digite a chave privada!")
                elif amount_send <= 0:
                    st.error("❌ O valor deve ser maior que zero!")
                else:
                    with st.spinner("⏳ Processando transação..."):
                        success, message = manager.transfer_eth_to_contract(
                            private_key_send,
                            amount_send
                        )
                        
                        if success:
                            st.success(f"✅ {message}")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
    
    # Tab 4: Consultar Conta
    with tab4:
        st.subheader("🔍 Consultar Saldo de Conta Específica")
        
        private_key_query = st.text_input(
            "🔑 Chave Privada (sem 0x)",
            type="password",
            help="Digite a chave privada para consultar os saldos"
        )
        
        if st.button("🔍 Consultar", type="primary"):
            if not private_key_query:
                st.error("❌ Digite a chave privada!")
            else:
                account = manager.get_account_from_private_key(private_key_query)
                
                if not account:
                    st.error("❌ Chave privada inválida!")
                else:
                    st.success(f"✅ Conta encontrada: {account.address}")
                    
                    # Saldos da conta
                    st.markdown("### 👤 Saldos da Conta")
                    col1, col2 = st.columns(2)
                    
                    balance_wei, balance_eth = manager.get_balance(account.address)
                    eth_balance_wei, eth_balance_eth = manager.get_account_eth_balance(account.address)
                    
                    with col1:
                        st.metric(
                            "💼 Saldo no Contrato",
                            f"{balance_eth:.6f} ETH",
                            delta=f"{balance_wei} Wei"
                        )
                    
                    with col2:
                        st.metric(
                            "🏦 Saldo Real (Blockchain)",
                            f"{eth_balance_eth:.6f} ETH",
                            delta=f"{eth_balance_wei} Wei"
                        )
                    
                    st.code(account.address, language="text")
                    
                    st.markdown("---")
                    
                    # Saldos do contrato
                    st.markdown("### 📋 Saldos do Contrato")
                    col3, col4 = st.columns(2)
                    
                    contract_bal_wei, contract_bal_eth = manager.get_contract_balance()
                    contract_real_wei, contract_real_eth = manager.get_contract_eth_balance()
                    
                    with col3:
                        st.metric(
                            "💼 Saldo Interno (função)",
                            f"{contract_bal_eth:.6f} ETH",
                            delta=f"{contract_bal_wei} Wei"
                        )
                    
                    with col4:
                        st.metric(
                            "🏦 Saldo Real de ETH",
                            f"{contract_real_eth:.6f} ETH",
                            delta=f"{contract_real_wei} Wei"
                        )

else:
    st.error("❌ Não foi possível conectar à rede Ethereum. Verifique sua conexão e tente novamente.")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📡 Status da Conexão**")
    if st.session_state.connected:
        st.success("🟢 Conectado")
    else:
        st.error("🔴 Desconectado")

with col2:
    st.markdown("**🌐 Rede**")
    st.info("Sepolia Testnet")

with col3:
    st.markdown("**⚙️ Chain ID**")
    if st.session_state.connected:
        st.info(f"{manager.w3.eth.chain_id}")
    else:
        st.info("N/A")

st.markdown(
    "<p style='text-align: center; color: #666; margin-top: 20px;'>⛓️ Ethereum Contract Manager | Desenvolvido com Streamlit</p>",
    unsafe_allow_html=True
)

# Informações adicionais na sidebar
with st.sidebar:
    st.markdown("### 📚 Informações")
    st.markdown("---")
    
    st.markdown("#### 🔐 Segurança")
    st.info("Suas chaves privadas não são armazenadas e são usadas apenas durante a transação.")
    
    st.markdown("#### ⚠️ Avisos Importantes")
    st.warning("""
    - Apenas o **owner** pode transferir ETH do contrato
    - Todas as transações são irreversíveis
    - Verifique os endereços antes de confirmar
    - Esta é uma testnet (Sepolia)
    """)
    
    st.markdown("#### 📊 Gas Price Atual")
    if st.session_state.connected:
        gas_price = manager.w3.eth.gas_price
        gas_price_gwei = manager.w3.from_wei(gas_price, 'gwei')
        st.metric("Gas Price", f"{gas_price_gwei:.2f} Gwei")
    
    st.markdown("#### 🔗 Links Úteis")
    st.markdown(f"[Ver Contrato no Etherscan](https://sepolia.etherscan.io/address/{CONTRACT_ADDRESS})")
    st.markdown("[Faucet Sepolia](https://sepoliafaucet.com/)")
    
    st.markdown("---")
    st.markdown("**Versão:** 1.0.0")
    st.markdown("**Última Atualização:** 2025")