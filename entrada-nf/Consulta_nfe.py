import requests

def consultar_nfe(chave):
    url = f"https://nfe0.cerbras.com.br/nfe/{chave}"
    headers = {
        "X-API-Code": "Kx4Jq9Tp6Wm3Ls1RdU7v",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
        "Connection": "keep-alive"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("✅ Consulta realizada com sucesso!")
        print(response.json())
        return response.json()
    else:
        print(f"❌ Erro na consulta: {response.status_code}")
        print(response.text)
        return None

# Exemplo de uso:
if __name__ == "__main__":
    chave_exemplo = "42250773912859000140550010001500021998677356"
    consultar_nfe(chave_exemplo)
