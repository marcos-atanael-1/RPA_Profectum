"""
Cliente para comunicação com a API externa de Romaneios
"""
import requests
from datetime import datetime
import config

class RomaneioAPIClient:
    """
    Cliente para fazer requisições à API externa de romaneios
    """
    
    def __init__(self):
        self.base_url = config.API_BASE_URL
        self.system_id = config.API_SYSTEM_ID
        self.modo_teste = config.MODO_TESTE
        self.headers = {
            'Content-Type': 'application/json',
            'x-system-id-romaneios': self.system_id
        }
    
    def _log(self, mensagem):
        """Log interno para debug"""
        if config.VERIFICADOR_LOG_DETALHADO:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] API Client: {mensagem}")
    
    def _mock_get_romaneio(self, pedido_compra):
        """
        Retorna dados mockados para teste (quando MODO_TESTE=True)
        Simula resposta da API GET /api/romaneio/{pedido}
        """
        self._log(f"MODO TESTE: Simulando GET para pedido {pedido_compra}")
        
        # Simular dados de romaneio
        return [{
            "PEDIDO": pedido_compra,
            "IDRO": 999999,  # ID fictício
            "NOTA_FISCAL": "000999",
            "ITEM": [
                {
                    "IDRO": 999999,
                    "CODIGO": "01.000001",
                    "DESCRICAO": "PRODUTO TESTE A",
                    "QUANTIDADE_CONTADA": 100,  # Simula contagem completa
                    "QUANTIDADE_NF": 100
                },
                {
                    "IDRO": 999999,
                    "CODIGO": "01.000002",
                    "DESCRICAO": "PRODUTO TESTE B",
                    "QUANTIDADE_CONTADA": 50,  # Simula contagem completa
                    "QUANTIDADE_NF": 50
                }
            ]
        }]
    
    def _mock_inserir_romaneio(self, dados):
        """
        Simula inserção de romaneio (quando MODO_TESTE=True)
        """
        romaneio = dados.get('romaneio', {})
        self._log(f"MODO TESTE: Simulando POST para pedido {romaneio.get('pedidoCompra')}")
        
        return {
            "success": True,
            "message": "[TESTE] Romaneio inserido com sucesso",
            "idro": 999999,
            "pedido": romaneio.get('pedidoCompra')
        }
    
    def _mock_atualizar_status(self, idro, status):
        """
        Simula atualização de status (quando MODO_TESTE=True)
        """
        self._log(f"MODO TESTE: Simulando PUT para IDRO {idro} -> Status {status}")
        
        return {
            "success": True,
            "message": f"[TESTE] Status atualizado para {status}",
            "idro": idro,
            "status": status
        }
    
    def get_romaneio(self, pedido_compra):
        """
        Busca dados do romaneio na API externa
        
        Args:
            pedido_compra (str): Número do pedido de compra
            
        Returns:
            list: Lista com dados do romaneio e itens
            
        Exemplo de resposta:
        [
            {
                "PEDIDO": "000285847",
                "IDRO": 112244,
                "NOTA_FISCAL": "000123",
                "ITEM": [
                    {
                        "IDRO": 112244,
                        "CODIGO": "02.016596",
                        "DESCRICAO": "BONE",
                        "QUANTIDADE_CONTADA": null,
                        "QUANTIDADE_NF": 1200
                    }
                ]
            }
        ]
        """
        if self.modo_teste:
            return self._mock_get_romaneio(pedido_compra)
        
        try:
            url = f"{self.base_url}/api/romaneio/{pedido_compra}"
            self._log(f"GET {url}")
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            self._log(f"Resposta recebida: {len(data)} romaneio(s)")
            
            return data
            
        except requests.exceptions.RequestException as e:
            self._log(f"ERRO na requisicao GET: {str(e)}")
            raise Exception(f"Erro ao buscar romaneio: {str(e)}")
    
    def inserir_romaneio(self, pedido_compra, nota_fiscal, chave_acesso, 
                         apos_recebimento=None, programado=None, 
                         inserir_como_parcial=None):
        """
        Insere um novo romaneio na API externa
        
        Args:
            pedido_compra (str): Número do pedido de compra
            nota_fiscal (str): Número da nota fiscal
            chave_acesso (str): Chave de acesso da NFe (44 dígitos)
            apos_recebimento (bool): Se deve inserir após recebimento
            programado (bool): Se é programado
            inserir_como_parcial (bool): Se deve inserir como parcial se já existir
            
        Returns:
            dict: Resposta da API
        """
        # Usar valores padrão do config se não fornecidos
        if apos_recebimento is None:
            apos_recebimento = config.API_APOS_RECEBIMENTO
        if programado is None:
            programado = config.API_PROGRAMADO
        if inserir_como_parcial is None:
            inserir_como_parcial = config.API_INSERIR_PARCIAL_SE_EXISTIR
        
        dados = {
            "romaneio": {
                "pedidoCompra": pedido_compra,
                "notaFiscal": nota_fiscal,
                "chaveAcesso": chave_acesso,
                "aposRecebimento": apos_recebimento,
                "programado": programado,
                "inserirComoParcialSeJaExistir": inserir_como_parcial
            }
        }
        
        if self.modo_teste:
            return self._mock_inserir_romaneio(dados)
        
        try:
            url = f"{self.base_url}/api/romaneio/inserir"
            self._log(f"POST {url}")
            self._log(f"Dados: {dados}")
            
            response = requests.post(url, json=dados, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            result = response.json() if response.text else {"success": True}
            self._log(f"Romaneio inserido com sucesso")
            
            return result
            
        except requests.exceptions.RequestException as e:
            self._log(f"ERRO na requisicao POST: {str(e)}")
            raise Exception(f"Erro ao inserir romaneio: {str(e)}")
    
    def atualizar_status_romaneio(self, idro, status):
        """
        Atualiza o status de um romaneio na API externa
        
        Args:
            idro (int): ID do romaneio na API
            status (str): Novo status (A, P, R, F)
            
        Returns:
            dict: Resposta da API
        """
        if self.modo_teste:
            return self._mock_atualizar_status(idro, status)
        
        try:
            url = f"{self.base_url}/api/romaneio/atualizar/{idro}"
            self._log(f"PUT {url}")
            
            dados = {"status": status}
            self._log(f"Dados: {dados}")
            
            response = requests.put(url, json=dados, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            result = response.json() if response.text else {"success": True}
            self._log(f"Status atualizado com sucesso para {status}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            self._log(f"ERRO na requisicao PUT: {str(e)}")
            raise Exception(f"Erro ao atualizar status: {str(e)}")

