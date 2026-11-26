// Configuração do projeto Firebase do Ofensiva de Dados.
// Cole aqui o objeto que o console do Firebase mostra em
// Configurações do projeto > Seus apps > App da Web > "Configuração do SDK".
// Esses valores não são senha: quem protege os dados são as regras do Firestore
// (cada pessoa só lê e escreve o próprio documento em users/<uid>).
//
// Enquanto apiKey estiver vazio, o app funciona só com o progresso salvo no aparelho.
export const firebaseConfig = {
  apiKey: "",
  authDomain: "",
  projectId: "",
  storageBucket: "",
  messagingSenderId: "",
  appId: "",
};
