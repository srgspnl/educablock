import hashlib
from typing import Dict, List, Optional, Tuple

class ContractManager:
    """
    Gerencia uma lista de contratos, armazenando o texto e seu hash SHA-256.
    """
    
    # Estrutura: list of (hash_str, contract_text)
    # Ex: [(hash1, text1), (hash2, text2), ...]
    def __init__(self):
        self.contracts: List[Tuple[str, str]] = []

    @staticmethod
    def hash_text(text: str) -> str:
        """
        Gera o hash SHA-256 para o texto fornecido.
        :param text: O texto do contrato.
        :return: O hash SHA-256 como string hexadecimal.
        """
        # Codifica o texto para bytes e calcula o hash
        text_bytes = text.encode('utf-8')
        return hashlib.sha256(text_bytes).hexdigest()

    def add_contract(self, text: str) -> int:
        """
        Adiciona um novo contrato e seu hash na lista.
        :param text: O texto do contrato (upload).
        :return: O número/índice (base 1) do contrato adicionado.
        """
        contract_hash = self.hash_text(text)
        self.contracts.append((contract_hash, text))
        
        # Retorna o número do contrato (índice + 1)
        return len(self.contracts)

    def get_contract_by_index(self, index: int) -> Optional[Dict]:
        """
        Busca um contrato pelo seu número (índice base 1).
        :param index: O número do contrato (1, 2, 3...).
        :return: Dicionário com 'number', 'hash', 'text' ou None.
        """
        # Converte para índice base 0
        list_index = index - 1 
        
        if 0 <= list_index < len(self.contracts):
            contract_hash, text = self.contracts[list_index]
            return {
                'number': index,
                'hash': contract_hash,
                'text': text
            }
        return None

    def get_contract_by_hash(self, target_hash: str) -> Optional[Dict]:
        """
        Busca um contrato pelo seu hash.
        :param target_hash: O hash do contrato a ser buscado.
        :return: Dicionário com 'number', 'hash', 'text' ou None.
        """
        for i, (contract_hash, text) in enumerate(self.contracts):
            if contract_hash == target_hash:
                return {
                    'number': i + 1,  # Retorna o número (base 1)
                    'hash': contract_hash,
                    'text': text
                }
        return None

    def verify_text_and_find_contract(self, text: str) -> Optional[Dict]:
        """
        Gera o hash de um texto e verifica se confere com algum contrato existente.
        :param text: O texto a ser verificado.
        :return: Dicionário com os dados do contrato correspondente ou None.
        """
        verified_hash = self.hash_text(text)
        
        # Reutiliza a função de busca por hash
        return self.get_contract_by_hash(verified_hash)

    @property
    def total_contracts(self) -> int:
        """Retorna o número total de contratos registrados."""
        return len(self.contracts)

    @property
    def contract_numbers(self) -> List[int]:
        """Retorna uma lista de números de contratos (1, 2, 3...)."""
        return list(range(1, len(self.contracts) + 1))