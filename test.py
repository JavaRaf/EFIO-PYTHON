import requests
import os




def excluir_postagem(post_id):
    try:
        response = requests.delete(f"https://graph.facebook.com/{post_id}", params={"access_token": os.getenv('FB_TOKEN')})
        response.raise_for_status()
        print("Postagem excluida com sucesso, post_id:", post_id)
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao excluir a postagem: {e}")


def get_posts():
    try:
        response = requests.get("https://graph.facebook.com/me/posts", params={"access_token": os.getenv('FB_TOKEN')})
        response.raise_for_status()
        posts = response.json()["data"]
        return posts
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter as postagens: {e}")
        return []


def main():
    posts = get_posts()
    for post in posts:
        excluir_postagem(post["id"])


main()