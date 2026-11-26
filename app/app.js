// Ofensiva de Dados — versão independente (GitHub Pages / APK).
// Progresso salvo no aparelho (localStorage) e, com login Google, no Firestore
// em users/<uid>, sincronizando entre celular e tablet.
import { firebaseConfig } from './firebase-config.js';

const GOAL = 15;                       // perguntas por dia
const LESSON = 12;                     // perguntas por lição
const BOX_DAYS = [0, 1, 2, 4, 8, 16];  // repetição espaçada: dias até rever, por caixa
const LS = 'ofensiva-dados-v1';

const $ = s => document.querySelector(s);
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const md = s => esc(s).replace(/`([^`]+)`/g, '<code>$1</code>');
const today = () => { const d = new Date(); d.setMinutes(d.getMinutes() - d.getTimezoneOffset()); return d.toISOString().slice(0, 10); };
const addDays = (iso, n) => { const d = new Date(iso + 'T12:00:00'); d.setDate(d.getDate() + n); return d.toISOString().slice(0, 10); };

let Q = [];
let state = { xp: 0, streak: 0, best: 0, lastDay: null, days: {}, cards: {}, topics: [], updatedAt: 0 };
let L = null; // lição em andamento

/* ---------------- persistência local ---------------- */
function lsLoad() { try { const v = localStorage.getItem(LS); return v ? JSON.parse(v) : null; } catch { return null; } }
function lsSave() { try { localStorage.setItem(LS, JSON.stringify(state)); } catch { } }

/* ---------------- sincronização (Firebase) ---------------- */
const cloud = { enabled: !!firebaseConfig.apiKey, user: null, ref: null, api: null, timer: null, status: '' };

// Junta dois progressos sem perder nada: fica com o mais avançado de cada parte.
function merge(a, b) {
  a = a || {}; b = b || {};
  const out = { ...a, ...b };
  out.xp = Math.max(a.xp || 0, b.xp || 0);
  out.best = Math.max(a.best || 0, b.best || 0);
  out.days = { ...(a.days || {}) };
  for (const [d, n] of Object.entries(b.days || {})) out.days[d] = Math.max(out.days[d] || 0, n);
  out.cards = { ...(a.cards || {}) };
  for (const [id, c] of Object.entries(b.cards || {})) {
    const o = out.cards[id];
    if (!o || (c.seen || 0) > (o.seen || 0) || ((c.seen || 0) === (o.seen || 0) && (c.due || '') > (o.due || ''))) out.cards[id] = c;
  }
  const la = a.lastDay || '', lb = b.lastDay || '';
  if (la > lb) { out.lastDay = a.lastDay; out.streak = a.streak; }
  else if (lb > la) { out.lastDay = b.lastDay; out.streak = b.streak; }
  else out.streak = Math.max(a.streak || 0, b.streak || 0);
  out.topics = (a.updatedAt || 0) >= (b.updatedAt || 0) ? (a.topics || []) : (b.topics || []);
  out.updatedAt = Math.max(a.updatedAt || 0, b.updatedAt || 0);
  return out;
}

function save() {
  state.updatedAt = Date.now();
  lsSave();
  if (!cloud.ref) return;
  clearTimeout(cloud.timer);
  cloud.timer = setTimeout(pushCloud, 1200);
}
async function pushCloud() {
  if (!cloud.ref) return;
  try { await cloud.api.setDoc(cloud.ref, JSON.parse(JSON.stringify(state))); setStatus('Sincronizado'); }
  catch { setStatus('Sem internet: salvo no aparelho, sincroniza quando voltar'); }
}

async function initCloud() {
  if (!cloud.enabled) { renderAccount(); return; }
  try {
    const V = '10.12.2';
    const [appM, authM, fsM] = await Promise.all([
      import(`https://www.gstatic.com/firebasejs/${V}/firebase-app.js`),
      import(`https://www.gstatic.com/firebasejs/${V}/firebase-auth.js`),
      import(`https://www.gstatic.com/firebasejs/${V}/firebase-firestore.js`),
    ]);
    const app = appM.initializeApp(firebaseConfig);
    const auth = authM.getAuth(app);
    const db = fsM.initializeFirestore(app, { localCache: fsM.persistentLocalCache() });
    cloud.api = { ...authM, ...fsM, auth, db };
    try { await authM.getRedirectResult(auth); } catch (e) { setStatus(authMsg(e && e.code)); }
    let unsub = null;
    authM.onAuthStateChanged(auth, user => {
      cloud.user = user;
      if (unsub) { unsub(); unsub = null; }
      cloud.ref = user ? fsM.doc(db, 'users', user.uid) : null;
      renderAccount();
      if (!user) return;
      setStatus('Sincronizando…');
      unsub = fsM.onSnapshot(cloud.ref, snap => {
        const remote = snap.exists() ? snap.data() : null;
        const merged = merge(state, remote);
        const changedLocal = JSON.stringify(merged) !== JSON.stringify(state);
        state = merged; lsSave();
        if (changedLocal && !L) render();
        if (!remote || JSON.stringify(merged) !== JSON.stringify(remote)) pushCloud();
        else setStatus('Sincronizado');
      }, () => setStatus('Não consegui sincronizar agora'));
    });
  } catch {
    cloud.enabled = false;
    renderAccount('Sem conexão com o servidor de login. O progresso fica salvo no aparelho.');
  }
}

async function signIn() {
  const { GoogleAuthProvider, signInWithPopup, signInWithRedirect, auth } = cloud.api;
  const provider = new GoogleAuthProvider();
  try { await signInWithPopup(auth, provider); }
  catch (e) {
    if (e && (e.code === 'auth/popup-blocked' || e.code === 'auth/operation-not-supported-in-this-environment' || e.code === 'auth/cancelled-popup-request')) await signInWithRedirect(auth, provider);
    else if (!(e && e.code === 'auth/popup-closed-by-user')) setStatus(authMsg(e && e.code));
  }
}
function authMsg(code) {
  const m = {
    'auth/operation-not-allowed': 'O login com Google não está ativado no Firebase (Authentication > Método de login > Google).',
    'auth/configuration-not-found': 'O login com Google não está ativado no Firebase (Authentication > Método de login > Google).',
    'auth/unauthorized-domain': 'Este endereço não está nos domínios autorizados do Firebase.',
    'auth/network-request-failed': 'Sem internet para entrar agora.',
  };
  return 'Não deu para entrar: ' + (m[code] || code || 'erro desconhecido');
}

function setStatus(t) { cloud.status = t; const el = $('#sync'); if (el) el.textContent = t; }
function renderAccount(msg) {
  const el = $('#account');
  if (!cloud.enabled) { el.innerHTML = `<span>${esc(msg || 'Progresso salvo neste aparelho.')}</span>`; return; }
  if (!cloud.api) { el.innerHTML = '<span>Conectando…</span>'; return; }
  if (!cloud.user) {
    el.innerHTML = `<button class="gbtn" id="login"><svg viewBox="0 0 48 48" aria-hidden="true"><path fill="#4285F4" d="M45 24.5c0-1.6-.1-3.1-.4-4.5H24v8.5h11.8c-.5 2.7-2.1 5-4.4 6.6v5.5h7.1c4.2-3.9 6.5-9.6 6.5-16.1z"/><path fill="#34A853" d="M24 46c5.9 0 10.9-2 14.5-5.4l-7.1-5.5c-2 1.3-4.5 2.1-7.4 2.1-5.7 0-10.5-3.8-12.2-9H4.5v5.7C8.1 41.1 15.5 46 24 46z"/><path fill="#FBBC05" d="M11.8 28.2c-.4-1.3-.7-2.7-.7-4.2s.3-2.9.7-4.2v-5.7H4.5A21.9 21.9 0 0 0 2 24c0 3.5.8 6.9 2.5 9.9l7.3-5.7z"/><path fill="#EA4335" d="M24 10.8c3.2 0 6.1 1.1 8.4 3.3l6.3-6.3C34.9 4.2 29.9 2 24 2 15.5 2 8.1 6.9 4.5 14.1l7.3 5.7c1.7-5.2 6.5-9 12.2-9z"/></svg>Entrar com Google para sincronizar</button><span id="sync" class="authmsg">${esc(cloud.status || '')}</span>`;
    $('#login').onclick = signIn;
    return;
  }
  const u = cloud.user;
  el.innerHTML = `${u.photoURL && u.photoURL.startsWith('https://') ? `<img src="${esc(u.photoURL)}" alt="">` : ''}<span>${esc(u.displayName || u.email || 'Conectado')} · <span id="sync">${esc(cloud.status)}</span></span><button class="link" id="logout">Sair</button>`;
  $('#logout').onclick = () => cloud.api.signOut(cloud.api.auth);
}

/* ---------------- lógica do quiz ---------------- */
const topicsAll = () => [...new Set(Q.map(q => q.t))];
const activeTopics = () => (state.topics && state.topics.length ? state.topics : topicsAll());
function shuffle(a) { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }

function buildLesson(mode) {
  const t = today(), act = new Set(activeTopics());
  const pool = Q.filter(q => act.has(q.t));
  if (mode === 'errors') return shuffle(pool.filter(q => state.cards[q.id] && state.cards[q.id].box <= 1 && state.cards[q.id].seen)).slice(0, LESSON);
  const due = shuffle(pool.filter(q => state.cards[q.id] && state.cards[q.id].due <= t));
  const fresh = shuffle(pool.filter(q => !state.cards[q.id]));
  const later = pool.filter(q => state.cards[q.id] && state.cards[q.id].due > t).sort((a, b) => state.cards[a.id].due.localeCompare(state.cards[b.id].due));
  const nNew = Math.max(4, LESSON - due.length);
  let pick = [...due.slice(0, LESSON - Math.min(nNew, fresh.length)), ...fresh.slice(0, nNew)];
  if (pick.length < LESSON) pick = pick.concat(later.slice(0, LESSON - pick.length));
  return shuffle(pick.slice(0, LESSON));
}
function grade(q, right) {
  const t = today(), c = state.cards[q.id] || { box: 0 };
  c.seen = (c.seen || 0) + 1;
  c.box = right ? Math.min(5, (c.box || 0) + 1) : 1;
  c.due = right ? addDays(t, BOX_DAYS[c.box]) : t;
  state.cards[q.id] = c;
  state.days[t] = (state.days[t] || 0) + 1;
}
function bumpStreak() {
  const t = today();
  if (state.lastDay === t) return false;
  state.streak = state.lastDay === addDays(t, -1) ? state.streak + 1 : 1;
  state.best = Math.max(state.best || 0, state.streak);
  state.lastDay = t;
  return true;
}
const liveStreak = () => { const t = today(); return (state.lastDay === t || state.lastDay === addDays(t, -1)) ? state.streak : 0; };

/* ---------------- telas ---------------- */
function header() { $('#streak').textContent = liveStreak(); $('#xp').textContent = state.xp; }

function render() {
  header();
  if (!Q.length) { $('#app').innerHTML = '<div class="card">Carregando perguntas…</div>'; return; }
  const t = today(), done = state.days[t] || 0, pct = Math.min(1, done / GOAL), C = 2 * Math.PI * 40;
  const act = new Set(activeTopics()), pool = Q.filter(q => act.has(q.t));
  const dueN = pool.filter(q => state.cards[q.id] && state.cards[q.id].due <= t).length;
  const newN = pool.filter(q => !state.cards[q.id]).length;
  const errN = pool.filter(q => state.cards[q.id] && state.cards[q.id].box <= 1 && state.cards[q.id].seen).length;
  const ls = liveStreak();
  const msg = state.lastDay === t ? (done >= GOAL ? 'Meta de hoje batida. Quer adiantar a revisão de amanhã?' : 'Ofensiva garantida hoje. Falta pouco para a meta.')
    : ls ? `Faça uma lição hoje para manter a ofensiva de ${ls} dia${ls > 1 ? 's' : ''}.` : 'Comece uma ofensiva nova: uma lição por dia.';
  const topics = topicsAll().map(tp => {
    const qs = Q.filter(q => q.t === tp), m = qs.filter(q => (state.cards[q.id]?.box || 0) >= 3).length;
    return `<div class="topic"><b>${esc(tp)}</b><div class="bar"><i style="width:${Math.round(100 * m / qs.length)}%"></i></div><small>${m} de ${qs.length} dominadas</small></div>`;
  }).join('');
  let heat = ''; for (let i = 55; i >= 0; i--) { const d = addDays(t, -i), n = state.days[d] || 0; heat += `<i title="${d}: ${n}" class="${n >= GOAL ? 'l3' : n >= 8 ? 'l2' : n ? 'l1' : ''}"></i>`; }
  $('#app').innerHTML = `
  <div class="stack">
    <section class="card hero">
      <svg class="ring" viewBox="0 0 100 100" role="img" aria-label="${done} de ${GOAL} perguntas hoje">
        <circle class="bgc" cx="50" cy="50" r="40"/>
        <circle class="fgc" cx="50" cy="50" r="40" stroke-dasharray="${C}" stroke-dashoffset="${C * (1 - pct)}" transform="rotate(-90 50 50)"/>
        <text x="50" y="50" text-anchor="middle" dominant-baseline="central" font-size="22">${Math.min(done, 99)}/${GOAL}</text>
      </svg>
      <div><h2 style="font-size:22px">Meta do dia</h2><p class="lead">${esc(msg)}</p></div>
    </section>
    <div class="row">
      <button class="btn" id="go">Começar lição · ${LESSON} perguntas</button>
      <button class="btn ghost" id="errs" ${errN ? '' : 'disabled'}>Refazer erros (${errN})</button>
    </div>
    <p class="note">${dueN} para revisar hoje · ${newN} novas no banco. Perguntas que você erra voltam no mesmo dia; as que acerta voltam em 1, 2, 4, 8 e 16 dias.</p>
    <section class="card stack">
      <div class="label">Assuntos da lição</div>
      <div class="chips" id="chips">${topicsAll().map(tp => `<button class="chip" aria-pressed="${act.has(tp)}" data-t="${esc(tp)}">${esc(tp)}</button>`).join('')}</div>
    </section>
    <section class="card stack"><div class="label">Domínio por assunto</div><div class="topics">${topics}</div></section>
    <section class="card stack"><div class="label">Últimas 8 semanas · recorde de ${state.best || 0} dias</div><div class="heat">${heat}</div></section>
  </div>`;
  $('#go').onclick = () => start('lesson');
  $('#errs').onclick = () => start('errors');
  $('#chips').onclick = e => {
    const b = e.target.closest('.chip'); if (!b) return;
    const cur = new Set(activeTopics()), tp = b.dataset.t;
    if (cur.has(tp)) { if (cur.size === 1) return; cur.delete(tp); } else cur.add(tp);
    state.topics = cur.size === topicsAll().length ? [] : [...cur];
    save(); render();
  };
}

function start(mode) {
  const qs = buildLesson(mode);
  if (!qs.length) return;
  L = { queue: qs.map(q => ({ q, redo: false })), total: qs.length, i: 0, right: 0, answered: 0, xp: 0, combo: 0, missed: new Set() };
  ask();
}
function ask() {
  const item = L.queue[L.i], q = item.q, order = shuffle(q.o.map((_, k) => k));
  L.sel = null;
  const pct = Math.round(100 * L.answered / (L.total + L.missed.size));
  $('#app').innerHTML = `
  <div class="qhead"><button class="close" id="quit" aria-label="Sair da lição">✕</button><div class="prog"><i style="width:${pct}%"></i></div>${L.combo >= 3 ? `<span class="combo">${L.combo}× seguidas</span>` : ''}</div>
  <section class="card">
    <span class="tag ${item.redo ? 'redo' : ''}">${item.redo ? 'Revendo erro · ' : ''}${esc(q.t)} · cap. ${esc(q.cap)}</span>
    <p class="qtext">${md(q.q)}</p>
    ${q.code ? `<pre class="qcode">${esc(q.code)}</pre>` : ''}
    <div class="opts" id="opts">${order.map((k, n) => `<button class="opt" data-k="${k}"><span class="k">${'ABCD'[n]}</span><span>${md(q.o[k])}</span></button>`).join('')}</div>
    <div id="fb"></div>
  </section>
  <div class="row" style="margin-top:14px"><button class="btn" id="check" disabled>Verificar</button></div>`;
  $('#quit').onclick = () => { L = null; render(); };
  $('#opts').onclick = e => {
    const b = e.target.closest('.opt'); if (!b || b.disabled) return;
    document.querySelectorAll('.opt').forEach(o => o.classList.remove('sel'));
    b.classList.add('sel'); L.sel = +b.dataset.k; $('#check').disabled = false;
  };
  $('#check').onclick = check;
}
function check() {
  const item = L.queue[L.i], q = item.q, right = L.sel === q.a;
  document.querySelectorAll('.opt').forEach(o => { o.disabled = true; const k = +o.dataset.k; if (k === q.a) o.classList.add('right'); else if (k === L.sel) o.classList.add('wrong'); });
  L.answered++;
  if (right) { L.right += item.redo ? 0 : 1; L.combo++; L.xp += item.redo ? 5 : 10 + (L.combo >= 3 ? 5 : 0); }
  else { L.combo = 0; if (!item.redo) { L.missed.add(q.id); L.queue.push({ q, redo: true }); } }
  if (!item.redo) grade(q, right); else if (right) state.cards[q.id].due = addDays(today(), 1);
  save();
  $('#fb').innerHTML = `<div class="fb ${right ? 'ok' : 'bad'}"><h3>${right ? 'Isso!' : 'Quase.'}</h3>
    ${right ? '' : `<p>Resposta: <b>${md(q.o[q.a])}</b></p>`}${q.e ? `<p>${md(q.e)}</p>` : ''}
    <p class="gotoguide">No guia: capítulo ${esc(q.cap)}</p></div>`;
  const b = $('#check'); b.textContent = 'Continuar'; b.className = 'btn ' + (right ? 'ok' : 'bad'); b.disabled = false;
  b.onclick = next; b.focus();
}
function next() {
  L.i++;
  if (L.i < L.queue.length) return ask();
  const first = bumpStreak();
  state.xp += L.xp;
  save(); header();
  const acc = Math.round(100 * L.right / L.total);
  $('#app').innerHTML = `
  <section class="card stack" style="text-align:center">
    <div class="label">Lição concluída</div>
    <div class="big">+${L.xp} XP</div>
    <p class="lead">${first ? `Ofensiva de ${state.streak} dia${state.streak > 1 ? 's' : ''}. 🔥` : 'Ofensiva de hoje já estava garantida.'}</p>
    <div class="grid3">
      <div class="topic"><small>Acertos de primeira</small><b>${acc}%</b></div>
      <div class="topic"><small>Erros revistos</small><b>${L.missed.size}</b></div>
      <div class="topic"><small>Hoje</small><b>${state.days[today()] || 0}/${GOAL}</b></div>
    </div>
    ${L.missed.size ? '<p class="note">As que você errou voltam na lista "Refazer erros" e na revisão de amanhã.</p>' : ''}
    <div class="row"><button class="btn" id="again">Mais uma lição</button><button class="btn ghost" id="home">Voltar ao início</button></div>
  </section>`;
  L = null;
  $('#again').onclick = () => start('lesson');
  $('#home').onclick = render;
}

/* ---------------- início ---------------- */
const local = lsLoad(); if (local) state = { ...state, ...local };
render();
fetch('questions.json', { cache: 'no-cache' }).then(r => r.json()).then(data => { Q = data; if (!L) render(); })
  .catch(() => { $('#app').innerHTML = '<div class="card">Não consegui carregar as perguntas. Confira a internet e abra de novo.</div>'; });
initCloud();
if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => { });
// Botão "Instalar app": aparece quando o Chrome diz que dá para instalar.
let installEvt = null;
window.addEventListener('beforeinstallprompt', e => {
  e.preventDefault(); installEvt = e;
  const b = $('#install'); b.hidden = false;
  b.onclick = async () => { installEvt.prompt(); await installEvt.userChoice; installEvt = null; b.hidden = true; };
});
window.addEventListener('appinstalled', () => { $('#install').hidden = true; });
document.addEventListener('keydown', e => {
  if (!L) return;
  const k = '1234abcd'.indexOf(e.key.toLowerCase());
  if (k >= 0) { const b = document.querySelectorAll('.opt')[k % 4]; if (b && !b.disabled) b.click(); }
  if (e.key === 'Enter') { const b = $('#check'); if (b && !b.disabled) { e.preventDefault(); b.click(); } }
});
