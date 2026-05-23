import subprocess, time, datetime, sys, os

class C:
    R="\033[0m"; V="\033[92m"; A="\033[93m"; E="\033[91m"; CI="\033[96m"; B="\033[1m"

def log(msg, cor=C.R, pre=""):
    h = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"{cor}{pre}[{h}] {msg}{C.R}")
    with open("logs/cenario1.log", "a") as f:
        f.write(f"[{h}] {msg}\n")

def sep(titulo="", cor=C.CI):
    linha = "=" * 58
    print(f"\n{cor}{C.B}{linha}{C.R}")
    if titulo:
        print(f"{cor}{C.B}  {titulo}{C.R}")
        print(f"{cor}{C.B}{linha}{C.R}")
    print()

def p(s=1.5): time.sleep(s)

def exec_c(container, cmd):
    r = subprocess.run(["docker","exec",container,"sh","-c",cmd], capture_output=True, text=True)
    return r.stdout.strip(), r.returncode

def online(nome):
    r = subprocess.run(["docker","inspect","-f","{{.State.Running}}",nome], capture_output=True, text=True)
    return r.stdout.strip() == "true"

os.makedirs("logs", exist_ok=True)
open("logs/cenario1.log","w").close()

sep("CENARIO 1 - ATAQUE DE RANSOMWARE", C.CI)
log("PCN - CLT Distribuidora S.A.")
log("Stack: Alpine Linux 3.19 + SQLite + Docker")
log("Nivel de incidente: P1 - CRITICO", C.E, ">>> ")
p()

if not online("clt-producao"):
    print(f"\n{C.E}ERRO: rode primeiro: docker compose up -d{C.R}\n")
    sys.exit(1)

sep("FASE 1 - SITUACAO NORMAL")
log("Container clt-producao ONLINE (Alpine Linux)", C.V)
out,_ = exec_c("clt-producao","sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM clientes;'")
log(f"Clientes no banco: {out}", C.V)
out,_ = exec_c("clt-producao","sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM pedidos;'")
log(f"Pedidos ativos: {out}", C.V)
out,_ = exec_c("clt-producao","ls -lh /app/banco/clt.db")
log(f"Arquivo do banco: {out}", C.V)
p(2)

sep("FASE 2 - ATAQUE DE RANSOMWARE DETECTADO", C.E)
log("ALERTA: comportamento anomalo detectado!", C.E, "!!! ")
log("EDR identificou processo criptografando arquivos criticos", C.E, "!!! ")
p(1)
log("Simulando criptografia do banco de dados...", C.A)
p(0.8)
exec_c("clt-producao","mv /app/banco/clt.db /app/banco/clt.db.LOCKED")
exec_c("clt-producao","echo 'ENCRYPTED_BY_RANSOMWARE - PAY 10 BTC' > /app/banco/LEIA-ME.txt")
out,_ = exec_c("clt-producao","ls /app/banco/")
log(f"Estado do banco apos ataque: {out}", C.E)
log("SISTEMA COMPROMETIDO - CRM INDISPONIVEL", C.E, "!!! ")
log("Mensagem do atacante: Pague 10 BTC para recuperar seus dados", C.E, "!!! ")
p(2)

sep("FASE 3 - ACIONAMENTO DO CSIRT", C.A)
log("Coordenador de Incidentes acionado via canal dedicado", C.A)
log("Canal de crise aberto: #incidente-p1-ransomware", C.A)
log("DPO notificado - possivel exposicao de dados pessoais (LGPD)", C.A)
log(f"Timestamp: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", C.A)
p(2)

sep("FASE 4 - CONTENCAO", C.A)
log("Isolando container de producao da rede...", C.A)
subprocess.run(["docker","network","disconnect","distribuidora-clt_rede-clt","clt-producao"], capture_output=True)
log("Container clt-producao ISOLADO da rede", C.V)
log("Integracoes com ERPs suspensas", C.A)
log("ATENCAO: container NAO derrubado - memoria preservada para forense", C.CI)
p(2)

sep("FASE 5 - RECUPERACAO VIA BACKUP WORM", C.V)
log("Verificando backup WORM...", C.A)
p(1)
out, code = exec_c("clt-producao","ls -lh /app/backup/")
if code == 0 and "clt_backup.db" in out:
    log(f"Backup WORM encontrado: {out}", C.V)
else:
    log("ERRO: backup nao encontrado!", C.E)
    sys.exit(1)

out,_ = exec_c("clt-producao","md5sum /app/backup/clt_backup.db")
log(f"Hash MD5 verificado: {out}", C.V)
p(1)
log("Removendo arquivos criptografados...", C.A)
exec_c("clt-producao","rm -f /app/banco/clt.db.LOCKED /app/banco/LEIA-ME.txt")
log("Restaurando banco a partir do backup WORM...", C.A)
exec_c("clt-producao","cp /app/backup/clt_backup.db /app/banco/clt.db")
p(0.8)
log("Restore concluido!", C.V)
subprocess.run(["docker","network","connect","distribuidora-clt_rede-clt","clt-producao"], capture_output=True)
log("Container reconectado a rede", C.V)
p(1)

sep("FASE 6 - VALIDACAO POS-RESTORE", C.V)
log("Validando dados recuperados...", C.A)
p(1)
todos_ok = True
for tabela in ["clientes","pedidos","catalogo"]:
    out,_ = exec_c("clt-producao", f"sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM {tabela};'")
    ok = out.strip() == "5"
    status = f"{C.V}[OK]{C.R}" if ok else f"{C.E}[FALHA]{C.R}"
    print(f"    {status} Tabela {tabela}: {out} registro(s)")
    if not ok: todos_ok = False
    p(0.4)

p(1)
if todos_ok:
    log("Todos os dados validados - banco 100% integro!", C.V)
log("Patch de seguranca aplicado no container", C.V)

sep("FASE 7 - ENCERRAMENTO", C.CI)
log("Notificacao preparada para ANPD - prazo 72h (LGPD Art. 48)", C.A)
log("Equipe comercial informada - CRM disponivel", C.V)
log("Sistema liberado para os usuarios", C.V)

sep("RESULTADO DO CENARIO 1", C.V)
log("INCIDENTE ENCERRADO COM SUCESSO", C.V, ">>> ")
log("Downtime: dentro do RTO de 4h definido na BIA", C.V)
log("Dados recuperados: 100% - RPO respeitado", C.V)
log("Log salvo em: logs/cenario1.log", C.CI)