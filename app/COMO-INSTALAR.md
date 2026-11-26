# Ofensiva de Dados: como colocar no ar

São três etapas. Só a primeira exige criar algo (um projeto gratuito no Firebase). Você faz uma vez e nunca mais.

Endereço do app depois de publicado: **https://cauefabriziobs.github.io/Data_Analysis_Study_Assist/**

## 1. Firebase (login Google + sincronização), uns 10 minutos

1. Entre em https://console.firebase.google.com com sua conta Google e clique em **Criar um projeto**. Nome: `ofensiva-de-dados`. Pode desligar o Google Analytics.
2. **Login:** menu *Build > Authentication > Get started > Sign-in method > Google > Ativar*. Escolha seu e-mail como e-mail de suporte e salve.
3. **Domínio autorizado:** ainda em *Authentication > Settings > Authorized domains > Add domain*, adicione `cauefabriziobs.github.io`.
4. **Banco:** *Build > Firestore Database > Create database*. Local: `southamerica-east1 (São Paulo)`. Comece em **modo de produção**.
5. **Regras do banco:** na aba *Rules*, apague o que tiver, cole isto e clique em **Publish**:

   ```
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /users/{uid} {
         allow read, write: if request.auth != null && request.auth.uid == uid;
       }
     }
   }
   ```

   Cada pessoa só lê e escreve o próprio progresso.
6. **App da Web:** clique na engrenagem *Configurações do projeto*, role até *Seus apps* e clique no ícone `</>`. Apelido: `ofensiva-web`. **Não** marque Firebase Hosting. Clique em *Registrar app*.
7. Vai aparecer um bloco `const firebaseConfig = { apiKey: "...", ... }`. Copie esse bloco e mande para o Claude (ou cole em `app/firebase-config.js`). Esses valores não são senha: o que protege os dados são as regras do passo 5.

## 2. GitHub Pages (o site), uns 2 minutos

1. No GitHub, abra o repositório *Data_Analysis_Study_Assist > Settings > Pages*.
2. Em *Build and deployment > Source*, escolha **GitHub Actions**.
3. O repositório precisa ser **público** para o Pages funcionar no plano gratuito. As anotações de aula e o guia também ficam visíveis. Se preferir manter privado, o Pages exige um plano pago.
4. A cada `git push` na `main` que mexer no app, nas perguntas ou no guia, o site é atualizado sozinho (aba *Actions*, workflow "Publicar app no GitHub Pages").

## 3. Instalar no celular e no tablet

**Jeito rápido (sem APK):** abra o endereço do app no Chrome do Android, toque nos três pontinhos e em **Instalar app** (ou "Adicionar à tela inicial"). Vira um ícone, abre em tela cheia e funciona sem internet.

**APK:**

1. Abra https://www.pwabuilder.com, cole o endereço do app e clique em *Start*.
2. Clique em *Package for stores > Android > Generate Package*. Nas opções, deixe o *Package ID* como `io.github.cauefabriziobs.ofensiva`.
3. Baixe o `.zip`. Dentro dele tem o `.apk` (para instalar direto) e um arquivo `signing.keystore` com a senha em `signing-key-info.txt`. **Guarde o keystore e a senha:** sem eles você não consegue gerar uma versão nova do mesmo app.
4. Passe o `.apk` para o celular e o tablet (Drive, cabo ou WhatsApp) e abra. O Android vai pedir para permitir instalar de fonte desconhecida.
5. O APK abre o site publicado. Quando o site atualiza, o app atualiza junto, sem gerar APK novo.

## Como funciona a sincronização

- Sem login, o progresso fica salvo só no aparelho.
- Com login Google, cada resposta salva no aparelho e, um segundo depois, na nuvem. Os outros aparelhos recebem na hora.
- Sem internet, continua salvando no aparelho e sincroniza quando voltar.
- Se você estudou em dois aparelhos sem internet, ao conectar o app junta os dois: fica com o maior XP, o melhor estado de cada pergunta e a contagem de cada dia.
