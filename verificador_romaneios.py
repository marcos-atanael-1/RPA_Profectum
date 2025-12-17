"""
Script de verificação automática de romaneios
Executa a cada X minutos (configurável via .env)
Verifica se as quantidades dos itens batem com a NF e atualiza o status
"""
import sys
import time
from datetime import datetime
from app import app
from services.verificador_service import VerificadorService
import config

def main():
    """Função principal"""
    print("=" * 70)
    print("VERIFICADOR AUTOMATICO DE ROMANEIOS - RPA Profectum")
    print("=" * 70)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Modo: {'TESTE (nao chama APIs)' if config.MODO_TESTE else 'PRODUCAO'}")
    print(f"Intervalo: {config.INTERVALO_VERIFICACAO_MINUTOS} minutos")
    print(f"Max Tentativas: {config.MAX_TENTATIVAS_CONTAGEM}")
    print("=" * 70)
    
    if not config.VERIFICADOR_ATIVO:
        print("\n[AVISO] Verificador desativado no .env (VERIFICADOR_ATIVO=False)")
        print("        Ative-o para executar a verificacao automatica.\n")
        return
    
    verificador = VerificadorService()
    
    with app.app_context():
        try:
            resultado = verificador.executar_verificacao_automatica()
            
            print("\n" + "=" * 70)
            print("RESUMO DA EXECUCAO")
            print("=" * 70)
            print(f"Total verificados: {resultado['total_verificados']}")
            print(f"Atualizados para Aberto: {resultado['atualizados_para_aberto']}")
            print(f"Mantidos Pendente: {resultado['mantidos_pendente']}")
            print(f"Max tentativas atingidas: {resultado['max_tentativas_atingidas']}")
            print(f"Erros: {resultado['erros']}")
            print(f"Duracao: {resultado['duracao']:.2f} segundos")
            print("=" * 70)
            
            if resultado['erros'] > 0:
                print("\nDetalhes dos erros:")
                for detalhe in resultado['detalhes']:
                    if detalhe['status'] == 'erro':
                        print(f"  - Pedido {detalhe['pedido']}: {detalhe['mensagem']}")
            
            print("\nVerificacao concluida com sucesso!")
            return 0
            
        except Exception as e:
            print(f"\n[ERRO] Falha na execucao do verificador: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1

def executar_loop():
    """Executa o verificador em loop contínuo"""
    print("\n[INFO] Modo LOOP ativado - Verificacao continua")
    print(f"[INFO] Pressione Ctrl+C para interromper\n")
    
    contador = 1
    
    try:
        while True:
            print(f"\n{'='*70}")
            print(f"EXECUCAO #{contador}")
            print(f"{'='*70}")
            
            main()
            
            contador += 1
            
            print(f"\n[INFO] Aguardando {config.INTERVALO_VERIFICACAO_MINUTOS} minutos ate proxima verificacao...")
            print(f"[INFO] Proxima execucao: {datetime.now().strftime('%H:%M:%S')}")
            
            time.sleep(config.INTERVALO_VERIFICACAO_MINUTOS * 60)
            
    except KeyboardInterrupt:
        print("\n\n[INFO] Verificador interrompido pelo usuario.")
        print("[INFO] Encerrando...")
        return 0
    except Exception as e:
        print(f"\n[ERRO] Erro no loop de verificacao: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Verificador automatico de romaneios'
    )
    parser.add_argument(
        '--loop',
        action='store_true',
        help='Executar em loop continuo (a cada X minutos)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Executar uma unica vez e sair (padrao)'
    )
    
    args = parser.parse_args()
    
    if args.loop:
        sys.exit(executar_loop())
    else:
        sys.exit(main())

