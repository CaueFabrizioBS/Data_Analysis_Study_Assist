"""Carteiro do "Colega DA" no Telegram (@DataStudyBuddyBot).

Quem escreve as perguntas e as respostas é o Claude (tarefas agendadas);
este script só entrega e busca mensagens.

    python desk/telegram.py send "texto"     manda uma mensagem para o Cauê
    python desk/telegram.py read             mostra as mensagens novas dele (e marca como lidas)
    python desk/telegram.py peek             mostra as novas sem marcar como lidas
    python desk/telegram.py chat             descobre e guarda o chat do Cauê (ele manda "oi" antes)

O token fica em desk/.telegram.env e o estado (chat, última mensagem lida,
última pergunta enviada) em desk/.telegram-state.json. Os dois ficam fora do Git.
Só mensagens do chat guardado são lidas; o resto é ignorado.
"""
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
ENV = HERE / ".telegram.env"
STATE = HERE / ".telegram-state.json"


def token() -> str:
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if line.startswith("TELEGRAM_TOKEN="):
            return line.split("=", 1)[1].strip()
    sys.exit("token não encontrado em desk/.telegram.env")


def api(method: str, **params):
    url = f"https://api.telegram.org/bot{token()}/{method}"
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(url, data=data, timeout=30) as r:
        res = json.load(r)
    if not res.get("ok"):
        sys.exit(f"Telegram recusou: {res}")
    return res["result"]


def load() -> dict:
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}


def save(st: dict):
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")


def updates(st: dict, commit: bool):
    res = api("getUpdates", offset=st.get("offset", 0), timeout=0)
    msgs = []
    for u in res:
        m = u.get("message") or {}
        if st.get("chat_id") and m.get("chat", {}).get("id") == st["chat_id"] and m.get("text"):
            msgs.append((datetime.fromtimestamp(m["date"]).strftime("%d/%m %H:%M"), m["text"]))
    if commit and res:
        st["offset"] = res[-1]["update_id"] + 1
        save(st)
    return res, msgs


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd, st = sys.argv[1], load()
    if cmd == "chat":
        res = api("getUpdates", timeout=0)
        privs = [u["message"]["chat"] for u in res if u.get("message", {}).get("chat", {}).get("type") == "private"]
        if not privs:
            sys.exit("nenhuma mensagem ainda: mande 'oi' para o robô no Telegram")
        st["chat_id"] = privs[0]["id"]
        save(st)
        print(f"chat guardado: {privs[0].get('first_name', '')}")
    elif cmd == "send":
        if not st.get("chat_id"):
            sys.exit("rode 'chat' primeiro")
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else sys.stdin.read()
        api("sendMessage", chat_id=st["chat_id"], text=text.strip())
        st["last_sent"] = datetime.now().isoformat(timespec="minutes")
        st["last_text"] = text.strip()
        save(st)
        print("enviado")
    elif cmd in ("read", "peek"):
        if not st.get("chat_id"):
            sys.exit("rode 'chat' primeiro")
        _, msgs = updates(st, commit=(cmd == "read"))
        print(f"última pergunta enviada: {st.get('last_sent', '-')}")
        print(st.get("last_text", ""))
        print("---")
        if not msgs:
            print("sem mensagens novas")
        for when, text in msgs:
            print(f"[{when}] {text}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
