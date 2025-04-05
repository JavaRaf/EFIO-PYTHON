<h1 align="center">Every <sup><sub><sub>(name)</sub></sub></sup> Frame in Order BOT</h1>

<div align="center">

A bot to post frames on Facebook pages for free

</div>


### Table of contents

- [Criando um app do facebook](#criando-um-app-do-facebook)
- [Fazendo o app do facebook publico](#fazendo-o-app-do-facebook-publico)
- [Gerando um access token](#gerando-um-access-token)
- [Tornando o token de acesso permanente](#tornando-o-token-de-acesso-permanente)
- [Configurando o bot](#configurando-o-bot)
- [Fazendo o commit das alterações](#fazendo-o-commit-das-alterações)
- [Rodar seu bot manualmente](#rodar-seu-bot-manualmente)


### Criando um app do facebook
<details><summary>click to expand</summary>

Antes de começar, certifique-se de ter uma pagina do Facebook ativa

- Acesse a pagina [Facebook for Developers](https://developers.facebook.com/) e clique em My Apps
![image](./utils/assets/tutorial/01.png)

- Clique em Create application para criar um novo app
![image](./utils/assets/tutorial/02.png)

- De um nome a seu app, pode ser qualquer nome, por exemplo EFIO, e um email
![image](./utils/assets/tutorial/03.png)

- Em Use cases escolha Other
![image](./utils/assets/tutorial/04.png)

- Em Type escolha Business
![image](./utils/assets/tutorial/05.png)

- Clique em Create application, sua senha será solicitada, confirme e continue
![image](./utils/assets/tutorial/06.png)

</details>

---

### Fazendo o app do facebook publico
<details><summary>click to expand</summary>

- Acesse o App/Settings/Basic
![image](./utils/assets/tutorial/07.png)

- Em sua Privacy Policy URL coloque o link do google https://google.com/, depois clique em Save Changes
![image](./utils/assets/tutorial/08.png)

- Para que seu conteudo seja publicado e visivel para todos os usuarios, selecione Application mode para live 
![image](./utils/assets/tutorial/09.png)

</details>

---

### Gerando um access token
<details><summary>click to expand</summary>

- Acesse o Tools/Graph API Explorer
![image](./utils/assets/tutorial/10.png)

- Selecione todas as permissoes de pagina
![image](./utils/assets/tutorial/11.png)

- Selecione seu app name, e pagina
![image](./utils/assets/tutorial/12.png)

- Confirme sua pagina de frames e aceite os demais termos   
![image](./utils/assets/tutorial/13.png)

- As permissoes devem ficar em preto, caso contrario refaça o processo
![image](./utils/assets/tutorial/14.png)

</details>

---

### Tornando o token de acesso permanente
<details><summary>click to expand</summary>

- Verifique o se tudo esta conforme a imagem, App meta, with your app name and User or page, with your user token and click on 🛈 icon and click on tool Open in access token tool
![image](./utils/assets/tutorial/15.png)

- Extenda e copie o token de acesso e volte para a aba anterior
![image](./utils/assets/tutorial/16.png)

- Subistitua o codigo de acesso pelo novo que voce copiou, cheque o App meta, with your app name and User or page, with your page name e extenda o token de acesso novamente.
![image](./utils/assets/tutorial/17.png)

- Voce obterá um token de acesso permanente. Copie ele e save, ele sera importante mais tarde.
![image](./utils/assets/tutorial/18.png)

</details>

---

### Configurando o bot
<details><summary>click to expand</summary>

- Aceesse o link do repositorio [EFIO-PYTHON](https://github.com/JavaRaf/EFIO-PYTHON) e clicque em Use this template para copiar o repositorio para seu perfil do github

- Apos copiar o repositorio, acesse as configuracoes do repositorio e va ate Settings/Secrets and variables/Actions
![image](./utils/assets/tutorial/19.png)

- Clique em New repository secret e adicione o token de acesso que voce gerou anteriormente, usando o nome FB_TOKEN
![image](./utils/assets/tutorial/20.png)

</details>

---

### Clone o repositorio no seu pc
<details><summary>click to expand</summary>

- Abra o terminal e digite git clone <url do repositorio>
![image](./utils/assets/tutorial/25.png)
![image](./utils/assets/tutorial/26.png)

</details>

---

### Gerando os frames
<details><summary>click to expand</summary>

#### Usando o [FFmpeg](https://ffmpeg.org/)

- Com o ffmepg  ja instalado, abra o terminal e digite ffmpeg -i "video.mkv" -vf "fps=2" -fps_mode vfr -q:v 3 "frame_%00d.jpg" <br>
onde
- video.mkv e o nome do arquivo do video
- fps=2 e o fps do video (1 a 60, quanto maior, mais frames por segundo serão gerados)
- -fps_mode vfr e o fps mode (vfr = variable frame rate)
- -q:v 3 e a qualidade do frame (1 a 5, quanto maior pior a qualidade)
- frame_%00d.jpg e o nome do arquivo do frame e destino

nota. voce deve criar uma pasta para os frames de saida para melhorar a organizacao, por exemplo 01 para o episodio 1, 02 para o episodio 2, etc...

![image](./utils/assets/tutorial/23.png)

</details>

---

#### Usando o Frame Chopper
<details><summary>click to expand</summary>


- baixe o aplicativo [Frame Chopper](https://github.com/JavaRaf/Frame-Chopper), abra-o e instale, agora selecione o arquivo do video, pasta de saida, fps, qualidade e clique em Generate    

<div align="center">
<img src="./utils/assets/tutorial/24.png" width="400" />
</div>

</details>

---

### Copiando os frames
<details><summary>click to expand</summary>

#### Após gerar os frames, copie a pasta 01 com todos os frames dentro e cole na pasta frames do repositorio
![image](./utils/assets/tutorial/27.png)

</details>

---

### Voce tambem pode incluir legendas do tipo .ass
<details><summary>click to expand</summary>

- Dentro da pasta subtitles crie uma pasta com o nunero do episodio, por exemplo 01 e cole o arquivo dentro
- Essas legendas  serão usadas para o bot postar as legendas no post ou no comentario do frame

</details>

---

### Configurando o bot
<details><summary>click to expand</summary>

- Nessa parte voce tera que configurar o arquivo config.yml
- abrar  o repositorio no seu editor de codigo, por exemplo VSCode
![image](./utils/assets/tutorial/28.png)

- no arquivo config.yml voce precisara configurar o page_name com o nome da sua pagina, isso ajudara a checar se seu FB_TOKEN e valido
- Em episodes, voce tera que cria um objeto com o numero do episodio, nesse exemplo, o 1
- img_fps: e o fps do video que voce gerou os frames
- o album_id serve para repostar osframes dentro de um album do facebook, voce pode criar um album no facebook e pegar o id dele e colar aqui
![image](./utils/assets/tutorial/29.png)

- voce pode adicionar mais episodes no futuro

</details>

---

### Fazendo o commit das alterações
<details><summary>click to expand</summary>
- Abra o terminal, na pasta do repositorio e digite 

```bash
    git add .
    git commit -m "initial commit"
    git push origin main
```

</details>

---

### Rodar seu bot manualmente
<details><summary>click to expand</summary>

- Apos empurar todas suas alterações para o github, voce pode rodar o bot manualmente
- Va ate seu repositorio no github e clique em Actions, e clique em Init banner and Run workflow
![image](./utils/assets/tutorial/30.png)

</details>


### Description
<details><summary>click to expand</summary>
Este repositório é um bot em Python que publica frames no Facebook com legendas e um tempo de espera entre posts. Ele utiliza o GitHub Actions para rodar automaticamente.

</details>

--- 

### License
<details><summary>click to expand</summary>
This repository is licensed under the MIT License. See [LICENSE](LICENSE) for more information.
</details>

--- 
