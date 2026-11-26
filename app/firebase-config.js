// Configuração do projeto Firebase do Ofensiva de Dados.
// Cole aqui o objeto que o console do Firebase mostra em
// Configurações do projeto > Seus apps > App da Web > "Configuração do SDK".
// Esses valores não são senha: quem protege os dados são as regras do Firestore
// (cada pessoa só lê e escreve o próprio documento em users/<uid>).
//
// Enquanto apiKey estiver vazio, o app funciona só com o progresso salvo no aparelho.
export const firebaseConfig = {
  apiKey: "AIzaSyA781neDV3ywb3rhT_Fzwb0QrPmFdIzU60",
  authDomain: "quiz-da-91ede.firebaseapp.com",
  projectId: "quiz-da-91ede",
  storageBucket: "quiz-da-91ede.firebasestorage.app",
  messagingSenderId: "507927089006",
  appId: "1:507927089006:web:1a2a36735eabbb99747b7f",
  measurementId: "G-Z0KP66ZLHB",
};
