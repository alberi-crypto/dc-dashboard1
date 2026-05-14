# Como publicar o Dashboard online (com link e senha)

Tempo total: ~15 minutos · Custo: **gratuito**

Você vai conseguir um **link público** (ex.: `https://dc-dashboard.streamlit.app`) que pode enviar para qualquer pessoa. Quem acessar precisará digitar uma **senha** para ver o conteúdo.

---

## Como vai funcionar

1. O código do app fica hospedado no **GitHub** (gratuito).
2. O **Streamlit Community Cloud** lê esse código e roda o app online (gratuito).
3. A **senha** fica protegida em uma área privada do Streamlit (não vai para o GitHub).
4. Você compartilha o link · a pessoa coloca a senha · acessa.

---

## Passo 1 — Criar conta no GitHub (3 min)

1. Acesse [github.com](https://github.com/signup) e crie uma conta grátis.
2. Confirme o e-mail.

---

## Passo 2 — Subir o código para o GitHub (5 min)

**Opção A — Pelo navegador (mais fácil, sem instalar nada):**

1. No GitHub, clique no botão verde **"New repository"** (ou em [github.com/new](https://github.com/new)).
2. Nome sugerido: `dc-dashboard`
3. Marque **Public** (precisa ser público no plano grátis do Streamlit Cloud — a senha protege os dados).
4. NÃO marque "Add a README file" — deixe vazio.
5. Clique em **Create repository**.
6. Na próxima tela clique em **"uploading an existing file"** (link no meio da página).
7. Arraste TODOS os arquivos da pasta `dc_dashboard` para a área indicada — **menos** o arquivo `.streamlit/secrets.toml` se ele existir (o `.gitignore` já protege).
8. Role até o fim e clique em **Commit changes**.

> ⚠️ Cuidado: NUNCA suba o arquivo `secrets.toml` (com a senha) para o GitHub. O arquivo `.gitignore` já cuida disso, mas confira na hora do upload.

---

## Passo 3 — Publicar no Streamlit Community Cloud (5 min)

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Clique em **"Sign in with GitHub"** e autorize.
3. Clique em **"New app"** (canto superior direito).
4. Preencha:
   - **Repository:** `seu-usuario/dc-dashboard`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** escolha um nome — ex.: `dc-dashboard` (ficará `dc-dashboard.streamlit.app`)
5. Clique em **Advanced settings...**
6. No campo **Secrets** cole exatamente:

```
password = "sua_senha_aqui"
```

   Troque `sua_senha_aqui` por uma senha forte (mínimo 8 caracteres).

7. Clique em **Save** e depois **Deploy!**.
8. Aguarde 2–3 minutos enquanto o app é construído.

Pronto! Seu link está no ar.

---

## Passo 4 — Compartilhar com sua equipe (1 min)

Envie por e-mail / WhatsApp:

> **Acesso ao Dashboard DC**
>
> Link: https://dc-dashboard.streamlit.app
>
> Senha: ********

Cada pessoa que acessar verá a tela de login. Após digitar a senha, o dashboard abre normalmente.

---

## Como atualizar os dados do dashboard

Sempre que quiser adicionar um novo mês:

1. Edite o arquivo local `dados/dados_mensais.xlsx` (adicionar coluna do mês).
2. No GitHub: navegue até `dados/dados_mensais.xlsx` no seu repositório → clique no ícone de lápis ✏️ → faça upload do arquivo atualizado.
3. Em até 1 minuto o app online se atualiza sozinho. Quem estiver com a página aberta só precisa dar F5.

---

## Como trocar a senha

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Clique no app → no menu de 3 pontos (`⋮`) → **Settings** → **Secrets**
3. Edite o valor de `password = "..."` e clique em Save.
4. O app reinicia automaticamente com a nova senha.

---

## Limitações do plano gratuito do Streamlit Cloud

| Item | Limite |
|---|---|
| Apps simultâneos | até 3 apps |
| Memória por app | 1 GB |
| Tráfego | ilimitado |
| Repositório | precisa ser **público** no GitHub |
| HTTPS | incluso (link já com `https://`) |
| Tempo ativo | dorme após 7 dias sem acesso (acorda em ~30s no próximo acesso) |

Para empresa com necessidades maiores (repo privado, mais memória, controle de acesso por SSO), existe o **Snowflake Streamlit** ou alternativas pagas como Render.com, Fly.io e Railway.

---

## Solução de problemas

**"App got into bad state" / erro ao subir**
→ Veja o log no painel. Geralmente é dependência faltando — confira se `requirements.txt` foi enviado.

**Tela de senha não aparece**
→ Confira se o campo Secrets foi preenchido com `password = "..."` (com aspas).

**Esqueceu a senha**
→ Acesse o painel Settings > Secrets e veja a senha definida.

**Quer remover acesso de alguém**
→ Troque a senha e avise as pessoas autorizadas.

---

*Se preferir, posso criar uma versão com múltiplos usuários (cada pessoa com sua senha), tela de cadastro ou autenticação via Google/Microsoft. É só pedir.*
