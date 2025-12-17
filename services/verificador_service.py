"""
Serviço de verificação automática de romaneios
Verifica se as quantidades dos itens batem e atualiza o status
"""
from datetime import datetime
from services.api_client import RomaneioAPIClient
import config

class VerificadorService:
    """
    Serviço para verificar romaneios automaticamente
    """
    
    def __init__(self):
        self.api_client = RomaneioAPIClient()
    
    def _log(self, mensagem):
        """Log interno"""
        if config.VERIFICADOR_LOG_DETALHADO:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] Verificador: {mensagem}")
    
    def executar_verificacao_automatica(self):
        """
        Executa a verificação automática de todos os romaneios não finalizados
        
        Returns:
            dict: Resumo da execução
        """
        from app import Romaneio
        
        inicio = datetime.now()
        self._log("=" * 60)
        self._log("INICIANDO VERIFICACAO AUTOMATICA DE ROMANEIOS")
        if config.MODO_TESTE:
            self._log("*** ATENCAO: EXECUTANDO EM MODO TESTE ***")
        self._log("=" * 60)
        
        # Buscar romaneios não finalizados
        romaneios = Romaneio.query.filter(Romaneio.status != 'F').all()
        
        self._log(f"Encontrados {len(romaneios)} romaneios para verificar")
        
        resultados = {
            'total_verificados': 0,
            'atualizados_para_aberto': 0,
            'mantidos_pendente': 0,
            'max_tentativas_atingidas': 0,
            'aguardando_contagem': 0,
            'erros': 0,
            'detalhes': []
        }
        
        for romaneio in romaneios:
            try:
                resultado = self.verificar_romaneio(romaneio)
                resultados['total_verificados'] += 1
                
                if resultado['status'] == 'atualizado_aberto':
                    resultados['atualizados_para_aberto'] += 1
                elif resultado['status'] == 'mantido_pendente':
                    resultados['mantidos_pendente'] += 1
                elif resultado['status'] == 'max_tentativas':
                    resultados['max_tentativas_atingidas'] += 1
                elif resultado['status'] == 'aguardando_contagem':
                    resultados['aguardando_contagem'] += 1
                
                resultados['detalhes'].append({
                    'pedido': romaneio.pedido_compra,
                    'status': resultado['status'],
                    'mensagem': resultado['mensagem']
                })
                
            except Exception as e:
                self._log(f"ERRO ao verificar romaneio {romaneio.pedido_compra}: {str(e)}")
                resultados['erros'] += 1
                resultados['detalhes'].append({
                    'pedido': romaneio.pedido_compra,
                    'status': 'erro',
                    'mensagem': str(e)
                })
        
        duracao = (datetime.now() - inicio).total_seconds()
        
        self._log("=" * 60)
        self._log("VERIFICACAO CONCLUIDA")
        self._log(f"Tempo total: {duracao:.2f} segundos")
        self._log(f"Total verificados: {resultados['total_verificados']}")
        self._log(f"Atualizados para Aberto: {resultados['atualizados_para_aberto']}")
        self._log(f"Mantidos Pendente: {resultados['mantidos_pendente']}")
        self._log(f"Max tentativas: {resultados['max_tentativas_atingidas']}")
        self._log(f"Aguardando contagem: {resultados['aguardando_contagem']}")
        self._log(f"Erros: {resultados['erros']}")
        self._log("=" * 60)
        
        resultados['duracao'] = duracao
        resultados['timestamp'] = inicio.isoformat()
        
        return resultados
    
    def verificar_romaneio(self, romaneio):
        """
        Verifica um romaneio específico
        """
        from app import db, RomaneioItem, RomaneioLog
        
        self._log(f"\nVerificando romaneio: {romaneio.pedido_compra}")
        
        # Verificar se pode ser verificado
        if not romaneio.pode_verificar():
            self._log(f"  Romaneio nao pode ser verificado (status: {romaneio.status}, tentativas: {romaneio.tentativas_contagem})")
            return {
                'status': 'nao_verificavel',
                'mensagem': 'Romaneio não pode ser verificado (finalizado ou max tentativas)'
            }
        
        try:
            # Buscar dados da API
            self._log(f"  Buscando dados da API para pedido {romaneio.pedido_compra}...")
            dados_api = self.api_client.get_romaneio(romaneio.pedido_compra)
            
            if not dados_api or len(dados_api) == 0:
                self._log(f"  AVISO: API nao retornou dados")
                return {
                    'status': 'sem_dados',
                    'mensagem': 'API não retornou dados para este pedido'
                }
            
            # Pegar primeiro romaneio da resposta
            dados_romaneio = dados_api[0]
            
            # Atualizar IDRO se ainda não tiver
            if not romaneio.idro and 'IDRO' in dados_romaneio:
                romaneio.idro = dados_romaneio['IDRO']
                self._log(f"  IDRO atualizado: {romaneio.idro}")
            
            # Processar itens
            itens_api = dados_romaneio.get('ITEM', [])
            self._log(f"  Encontrados {len(itens_api)} itens na API")
            
            # Verificar se todos os itens ja foram contados
            # Se algum item ainda tiver QUANTIDADE_CONTADA = null, nao processar
            itens_nao_contados = [
                item for item in itens_api 
                if item.get('QUANTIDADE_CONTADA') is None
            ]
            
            if itens_nao_contados:
                self._log(f"  IGNORADO: {len(itens_nao_contados)} item(ns) ainda sem contagem (QUANTIDADE_CONTADA = null)")
                for item in itens_nao_contados:
                    self._log(f"     - {item.get('CODIGO')}: {item.get('DESCRICAO')}")
                return {
                    'status': 'aguardando_contagem',
                    'mensagem': f'{len(itens_nao_contados)} item(ns) ainda nao foram contados'
                }
            
            # Atualizar ou criar itens no banco
            self._atualizar_itens_banco(romaneio, itens_api)
            
            # Verificar quantidades
            todas_contadas, todas_batem = self._verificar_quantidades(romaneio)
            
            self._log(f"  Todas contadas: {todas_contadas}, Todas batem: {todas_batem}")
            
            # Incrementar tentativa
            romaneio.incrementar_tentativa()
            
            # Decidir acao baseado nas quantidades
            if todas_contadas and todas_batem:
                # Todas as quantidades bateram -> Atualizar para ABERTO
                self._log(f"  SUCESSO: Todas as quantidades bateram!")
                return self._atualizar_para_aberto(romaneio)
            else:
                # Divergências encontradas
                divergencias = [item for item in romaneio.itens if item.tem_divergencia()]
                self._log(f"  Divergencias encontradas: {len(divergencias)} itens")
                
                if romaneio.tentativas_contagem >= config.MAX_TENTATIVAS_CONTAGEM:
                    self._log(f"  ATENCAO: Maximo de tentativas atingido ({romaneio.tentativas_contagem})")
                    return self._registrar_max_tentativas(romaneio, divergencias)
                else:
                    self._log(f"  Mantendo pendente (tentativa {romaneio.tentativas_contagem}/{config.MAX_TENTATIVAS_CONTAGEM})")
                    return self._manter_pendente(romaneio, divergencias)
            
        except Exception as e:
            self._log(f"  ERRO: {str(e)}")
            
            # Registrar erro no log do romaneio
            log = RomaneioLog(
                romaneio_id=romaneio.id,
                acao='erro_verificacao',
                detalhes=f'Erro na verificação: {str(e)}',
                tentativa=romaneio.tentativas_contagem
            )
            db.session.add(log)
            db.session.commit()
            
            raise
    
    def _atualizar_itens_banco(self, romaneio, itens_api):
        """Atualiza os itens do romaneio no banco de dados"""
        from app import db, RomaneioItem
        
        # Criar um mapa dos itens existentes
        itens_existentes = {item.codigo: item for item in romaneio.itens}
        
        for item_api in itens_api:
            codigo = item_api.get('CODIGO')
            
            if codigo in itens_existentes:
                # Atualizar item existente
                item = itens_existentes[codigo]
                item.quantidade_contada = item_api.get('QUANTIDADE_CONTADA')
                item.quantidade_nf = item_api.get('QUANTIDADE_NF')
                item.updated_at = datetime.utcnow()
            else:
                # Criar novo item
                item = RomaneioItem(
                    romaneio_id=romaneio.id,
                    idro=item_api.get('IDRO'),
                    codigo=codigo,
                    descricao=item_api.get('DESCRICAO', ''),
                    quantidade_nf=item_api.get('QUANTIDADE_NF', 0),
                    quantidade_contada=item_api.get('QUANTIDADE_CONTADA')
                )
                db.session.add(item)
        
        db.session.flush()
    
    def _verificar_quantidades(self, romaneio):
        """
        Verifica se todas as quantidades foram contadas e se batem
        """
        if len(romaneio.itens) == 0:
            return False, False
        
        todas_contadas = True
        todas_batem = True
        
        for item in romaneio.itens:
            if item.quantidade_contada is None:
                todas_contadas = False
                todas_batem = False
            elif item.quantidade_nf != item.quantidade_contada:
                todas_batem = False
        
        return todas_contadas, todas_batem
    
    def _atualizar_para_aberto(self, romaneio):
        """Atualiza romaneio para status ABERTO"""
        from app import db, RomaneioLog
        
        status_anterior = romaneio.status
        romaneio.status = 'A'  # Aberto
        
        # Chamar API para atualizar status (se não for modo teste)
        if not config.MODO_TESTE and romaneio.idro:
            try:
                self.api_client.atualizar_status_romaneio(romaneio.idro, 'A')
            except Exception as e:
                self._log(f"  ERRO ao atualizar status na API: {str(e)}")
                # Continua mesmo com erro na API
        
        # Criar log
        log = RomaneioLog(
            romaneio_id=romaneio.id,
            acao='verificado',
            status_anterior=status_anterior,
            status_novo='A',
            tentativa=romaneio.tentativas_contagem,
            detalhes='Todas as quantidades conferem. Status atualizado para Aberto.'
        )
        db.session.add(log)
        db.session.commit()
        
        return {
            'status': 'atualizado_aberto',
            'mensagem': f'Romaneio atualizado para ABERTO (tentativa {romaneio.tentativas_contagem})'
        }
    
    def _manter_pendente(self, romaneio, divergencias):
        """Mantém romaneio como PENDENTE"""
        from app import db, RomaneioLog
        
        # Criar log detalhado das divergências
        detalhes_divergencias = []
        for item in divergencias:
            if item.quantidade_contada is None:
                detalhes_divergencias.append(f"  - {item.codigo}: Nao contado")
            else:
                diff = item.quantidade_contada - item.quantidade_nf
                detalhes_divergencias.append(
                    f"  - {item.codigo}: NF={item.quantidade_nf}, Contado={item.quantidade_contada} (diff: {diff:+d})"
                )
        
        detalhes = f"Divergencias encontradas:\n" + "\n".join(detalhes_divergencias)
        
        log = RomaneioLog(
            romaneio_id=romaneio.id,
            acao='verificado',
            status_anterior='P',
            status_novo='P',
            tentativa=romaneio.tentativas_contagem,
            detalhes=detalhes
        )
        db.session.add(log)
        db.session.commit()
        
        return {
            'status': 'mantido_pendente',
            'mensagem': f'Mantido PENDENTE - {len(divergencias)} divergencia(s) (tentativa {romaneio.tentativas_contagem}/{config.MAX_TENTATIVAS_CONTAGEM})'
        }
    
    def _registrar_max_tentativas(self, romaneio, divergencias):
        """Registra que o máximo de tentativas foi atingido"""
        from app import db, RomaneioLog
        
        detalhes_divergencias = []
        for item in divergencias:
            if item.quantidade_contada is None:
                detalhes_divergencias.append(f"  - {item.codigo}: Nao contado")
            else:
                diff = item.quantidade_contada - item.quantidade_nf
                detalhes_divergencias.append(
                    f"  - {item.codigo}: NF={item.quantidade_nf}, Contado={item.quantidade_contada} (diff: {diff:+d})"
                )
        
        detalhes = f"MAXIMO DE TENTATIVAS ATINGIDO ({romaneio.tentativas_contagem}).\n\nDivergencias persistentes:\n" + "\n".join(detalhes_divergencias)
        
        log = RomaneioLog(
            romaneio_id=romaneio.id,
            acao='max_tentativas',
            status_anterior='P',
            status_novo='P',
            tentativa=romaneio.tentativas_contagem,
            detalhes=detalhes
        )
        db.session.add(log)
        db.session.commit()
        
        return {
            'status': 'max_tentativas',
            'mensagem': f'MAXIMO DE TENTATIVAS ATINGIDO - {len(divergencias)} divergencia(s) persistentes'
        }
