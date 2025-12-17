"""
Serviço de lógica de negócio para Romaneios
"""
from datetime import datetime
from services.api_client import RomaneioAPIClient
import config

class RomaneioService:
    """
    Serviço para gerenciar romaneios
    """
    
    def __init__(self):
        self.api_client = RomaneioAPIClient()
    
    def criar_romaneio(self, pedido_compra, nota_fiscal, chave_acesso, user_id,
                       apos_recebimento=None, programado=None, inserir_como_parcial=None,
                       observacoes=None):
        """
        Cria um novo romaneio e chama a API externa para inserir
        """
        # Importar aqui para evitar importação circular
        from app import db, Romaneio, RomaneioLog
        
        try:
            # Verificar se já existe
            romaneio_existente = Romaneio.query.filter_by(pedido_compra=pedido_compra).first()
            if romaneio_existente:
                return None, f"Já existe um romaneio para o pedido {pedido_compra}"
            
            # Validar chave de acesso
            if len(chave_acesso) != 44:
                return None, "Chave de acesso deve ter 44 dígitos"
            
            # Usar valores padrão se não fornecidos
            if apos_recebimento is None:
                apos_recebimento = config.API_APOS_RECEBIMENTO
            if programado is None:
                programado = config.API_PROGRAMADO
            if inserir_como_parcial is None:
                inserir_como_parcial = config.API_INSERIR_PARCIAL_SE_EXISTIR
            
            # Criar romaneio no banco
            romaneio = Romaneio(
                pedido_compra=pedido_compra,
                nota_fiscal=nota_fiscal,
                chave_acesso=chave_acesso,
                created_by=user_id,
                status='P',  # Pendente
                tentativas_contagem=0,
                apos_recebimento=apos_recebimento,
                programado=programado,
                inserir_como_parcial=inserir_como_parcial,
                observacoes=observacoes
            )
            
            # Se não for modo teste, chamar API para inserir
            if not config.MODO_TESTE:
                try:
                    resultado_api = self.api_client.inserir_romaneio(
                        pedido_compra=pedido_compra,
                        nota_fiscal=nota_fiscal,
                        chave_acesso=chave_acesso,
                        apos_recebimento=apos_recebimento,
                        programado=programado,
                        inserir_como_parcial=inserir_como_parcial
                    )
                    
                    # Extrair IDRO da resposta se disponível
                    if isinstance(resultado_api, dict) and 'idro' in resultado_api:
                        romaneio.idro = resultado_api['idro']
                    
                except Exception as e:
                    return None, f"Erro ao chamar API externa: {str(e)}"
            else:
                # Modo teste: usar IDRO fictício
                romaneio.idro = 999999
            
            # Salvar no banco
            db.session.add(romaneio)
            db.session.flush()  # Garante que temos o ID antes de criar o log
            
            # Criar log de criação
            log = RomaneioLog(
                romaneio_id=romaneio.id,
                acao='criado',
                status_novo='P',
                detalhes=f'Romaneio criado {"[MODO TESTE]" if config.MODO_TESTE else ""}',
                user_id=user_id
            )
            db.session.add(log)
            
            db.session.commit()
            
            return romaneio, None
            
        except Exception as e:
            db.session.rollback()
            return None, f"Erro ao criar romaneio: {str(e)}"
    
    def listar_romaneios(self, status=None, pedido=None, nf=None, page=1, per_page=10):
        """
        Lista romaneios com filtros e paginação
        """
        from app import Romaneio
        
        query = Romaneio.query
        
        if status:
            query = query.filter(Romaneio.status == status)
        if pedido:
            query = query.filter(Romaneio.pedido_compra.contains(pedido))
        if nf:
            query = query.filter(Romaneio.nota_fiscal.contains(nf))
        
        query = query.order_by(Romaneio.created_at.desc())
        
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    def get_romaneio(self, romaneio_id):
        """
        Busca um romaneio específico
        """
        from app import Romaneio
        return Romaneio.query.get(romaneio_id)
    
    def excluir_romaneio(self, romaneio_id, user_id):
        """
        Exclui um romaneio (apenas se pendente e sem tentativas)
        """
        from app import db, Romaneio
        
        try:
            romaneio = Romaneio.query.get(romaneio_id)
            
            if not romaneio:
                return False, "Romaneio não encontrado"
            
            if not romaneio.pode_excluir():
                return False, "Apenas romaneios pendentes sem tentativas podem ser excluídos"
            
            db.session.delete(romaneio)
            db.session.commit()
            
            return True, "Romaneio excluído com sucesso"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao excluir romaneio: {str(e)}"
    
    def atualizar_status_manual(self, romaneio_id, novo_status, user_id, observacoes=None):
        """
        Atualiza manualmente o status de um romaneio (uso administrativo)
        """
        from app import db, Romaneio, RomaneioLog
        
        try:
            romaneio = Romaneio.query.get(romaneio_id)
            
            if not romaneio:
                return False, "Romaneio não encontrado"
            
            if novo_status not in config.STATUS_CHOICES:
                return False, f"Status inválido: {novo_status}"
            
            status_anterior = romaneio.status
            romaneio.status = novo_status
            romaneio.updated_at = datetime.utcnow()
            
            # Criar log
            log = RomaneioLog(
                romaneio_id=romaneio.id,
                acao='atualizado_manual',
                status_anterior=status_anterior,
                status_novo=novo_status,
                detalhes=observacoes or 'Status atualizado manualmente',
                user_id=user_id
            )
            db.session.add(log)
            
            db.session.commit()
            
            return True, f"Status atualizado para {config.STATUS_CHOICES[novo_status]}"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao atualizar status: {str(e)}"
    
    def get_logs_romaneio(self, romaneio_id):
        """
        Busca o histórico de logs de um romaneio
        """
        from app import RomaneioLog
        
        return RomaneioLog.query.filter_by(romaneio_id=romaneio_id)\
            .order_by(RomaneioLog.timestamp.desc()).all()
    
    def get_estatisticas(self):
        """
        Retorna estatísticas gerais dos romaneios
        """
        from app import Romaneio
        
        total = Romaneio.query.count()
        pendentes = Romaneio.query.filter_by(status='P').count()
        abertos = Romaneio.query.filter_by(status='A').count()
        recebidos = Romaneio.query.filter_by(status='R').count()
        finalizados = Romaneio.query.filter_by(status='F').count()
        
        # Romaneios com tentativas máximas atingidas
        max_tentativas = Romaneio.query.filter(
            Romaneio.tentativas_contagem >= config.MAX_TENTATIVAS_CONTAGEM
        ).count()
        
        return {
            'total': total,
            'pendentes': pendentes,
            'abertos': abertos,
            'recebidos': recebidos,
            'finalizados': finalizados,
            'max_tentativas_atingidas': max_tentativas
        }
