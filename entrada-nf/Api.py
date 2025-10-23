import requests

def consultar_api_publica():
    url = "https://jsonplaceholder.typicode.com/posts"  # API pública gratuita
    try:
        response = requests.get(url)
        response.raise_for_status()  # lança erro se status != 200
        dados = response.json()
        
        # Exibe os 3 primeiros registros
        for item in dados[:3]:
            print(f"ID: {item['id']}")
            print(f"Título: {item['title']}")
            print(f"Conteúdo: {item['body']}")
            print("-" * 40)

    except requests.exceptions.RequestException as e:
        print("Erro ao consultar API:", e)

if __name__ == "__main__":
    consultar_api_publica()