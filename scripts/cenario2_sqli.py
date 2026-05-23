import subprocess, time, datetime, sys, os

class C:
    R="\033[0m"; V="\033[92m"; A="\033[93m"; E="\033[91m"; CI="\033[96m"; B="\033[1m"

def log(msg, cor=C.R, pre=""):
    h = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"{cor}{pre}[{h}] {msg}{C.R}")
    with open("logs/cenario2.log", "a") as f:
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

def status(nome):
    return f"{C.V}[ONLINE]{C.R}" if online(nome) else f"{C.E}[OFFLINE]{C.R}"

os.makedirs("logs", exist_ok=True)
open("logs/cenario2.log","w").close()

sep("CENARIO 2 - SQL INJECTION + FAILOVER + FAILBACK", C.CI)
log("PCN - CLT Distribuidora S.A.")
log("Stack: Alpine Linux 3.19 + SQLite + Docker")
log("Nivel de incidente: P1 - CRITICO", C.E, ">>> ")
p()

for nome in ["clt-producao","clt-dr"]:
    if not online(nome):
        print(f"\n{C.E}ERRO: rode primeiro: docker compose up -d{C.R}\n")
        sys.exit(1)

sep("FASE 1 - SITUACAO NORMAL")
print(f"  clt-producao: {status('clt-producao')}")
print(f"  clt-dr:       {status('clt-dr')} (standby)\n")
out,_ = exec_c("clt-producao","sqlite3 /app/banco/clt.db 'SELECT id,nome,cnpj FROM clientes;'")
log(f"Clientes em producao:\n{out}", C.V)
p(2)

sep("FASE 2 - ATAQUE DE SQL INJECTION", C.E)
log("WAF detectou requisicao maliciosa no endpoint /buscar-peca", C.E, "!!! ")
p(0.8)
query = "' OR '1'='1'; SELECT id,nome,cnpj,email FROM clientes; --"
log("Query maliciosa interceptada:", C.E, "!!! ")
print(f"\n    {C.E}{query}{C.R}\n")
p(1)
log("Query bypassa autenticacao e acessa tabela de clientes!", C.E, "!!! ")
p(0.8)
out,_ = exec_c("clt-producao","sqlite3 /app/banco/clt.db 'SELECT id,nome,cnpj,email FROM clientes;'")
with open("logs/dados_vazados.txt","w") as f:
    f.write("=== DADOS EXFILTRADOS PELO ATACANTE ===\n\n")
    f.write(out)
    f.write("\n\n=== FIM DO VAZAMENTO ===\n")
log("DADOS VAZADOS: tabela de clientes exfiltrada!", C.E, "!!! ")
log("Expostos: nomes, CNPJs e e-mails de 5 clientes B2B", C.E, "!!! ")
log("Evidencia salva em: logs/dados_vazados.txt", C.A)
p(1)
log("Servidor sobrecarregado - derrubando container de producao...", C.E, "!!! ")
subprocess.run(["docker","stop","clt-producao"], capture_output=True)
p(1)
log("PRODUCAO OFFLINE - CRM INDISPONIVEL", C.E, "!!! ")
print(f"\n  clt-producao: {status('clt-producao')}")
print(f"  clt-dr:       {status('clt-dr')}\n")
p(2)

sep("FASE 3 - ACIONAMENTO", C.A)
log("SIEM confirmou: SQL Injection + indisponibilidade total", C.A)
log("Coordenador de Incidentes acionado", C.A)
log("DPO notificado - dados pessoais expostos (LGPD)", C.A)
log("Prazo de 72h para notificar a ANPD iniciado (Art. 48)", C.A)
log(f"Timestamp: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", C.A)
p(2)

sep("FASE 4 - FAILOVER: ATIVANDO DR", C.A)
log("Producao indisponivel - ativando DR...", C.A)
p(1)
out,_ = exec_c("clt-dr","sqlite3 /app/banco/clt_dr.db 'SELECT COUNT(*) FROM clientes;'")
log(f"DR integro - {out} clientes disponiveis", C.V)
p(0.5)
log("Redirecionando trafego do CRM para o DR...", C.A)
p(1)
log("FAILOVER CONCLUIDO - clt-dr assumiu a operacao!", C.V, ">>> ")
print(f"\n  clt-producao: {status('clt-producao')}")
print(f"  clt-dr:       {status('clt-dr')} {C.V}(ATIVO){C.R}\n")
p(2)

sep("FASE 5 - REMEDIACAO", C.A)
log("Corrigindo vulnerabilidade de SQL Injection...", C.A)
p(1)
log("Causa raiz: concatenacao direta de string na query", C.A)
log("Correcao: queries parametrizadas em todos os endpoints", C.V)
p(0.8)
log("Regras do WAF atualizadas", C.V)
log("Reiniciando container de producao com correcoes...", C.A)
subprocess.run(["docker","start","clt-producao"], capture_output=True)
p(4)
log("Container clt-producao reiniciado e corrigido!", C.V)
out,_ = exec_c("clt-producao","sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM clientes;'")
log(f"Banco de producao ok - {out} clientes", C.V)
p(1)

sep("FASE 6 - FAILBACK: RETORNO A PRODUCAO", C.CI)
log("Ambiente principal corrigido - iniciando failback...", C.V)
p(1)
log("Passo 1: Sincronizando dados do DR para producao...", C.A)
p(1)
out,_ = exec_c("clt-dr","sqlite3 /app/banco/clt_dr.db 'SELECT COUNT(*) FROM pedidos;'")
log(f"Pedidos no DR sincronizados: {out}", C.V)
log("Sincronizacao concluida - zero perda de dados", C.V)
p(1)
log("Passo 2: Validando ambiente principal...", C.A)
p(1)
todos_ok = True
for tabela in ["clientes","pedidos","catalogo"]:
    out,_ = exec_c("clt-producao", f"sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM {tabela};'")
    ok = out.strip() == "5"
    st = f"{C.V}[OK]{C.R}" if ok else f"{C.E}[FALHA]{C.R}"
    print(f"    {st} Tabela {tabela}: {out} registro(s)")
    if not ok: todos_ok = False
    p(0.4)
if todos_ok:
    log("Todos os testes passaram - producao pronta!", C.V)
p(1)
log("Passo 3: Migrando usuarios de volta (gradual)...", C.A)
p(0.8)
log("  Equipe interna migrada", C.V)
p(0.8)
log("  Representantes externos migrados", C.V)
p(0.8)
log("FAILBACK CONCLUIDO!", C.V, ">>> ")
log("Passo 4: Monitoramento intensivo iniciado (48 horas)", C.CI)
log("Passo 5: DR retornando ao modo standby", C.CI)
print(f"\n  clt-producao: {status('clt-producao')} {C.V}(ATIVO){C.R}")
print(f"  clt-dr:       {status('clt-dr')} (standby)\n")
p(2)

sep("FASE 7 - OBRIGACOES LEGAIS", C.CI)
log("Notificacao formal preparada para ANPD (LGPD Art. 48)", C.A)
log("Dados expostos: nomes, CNPJs e e-mails de 5 clientes", C.A)
log("Comunicado aos clientes aguardando aprovacao juridica", C.A)

sep("RESULTADO DO CENARIO 2", C.V)
log("INCIDENTE ENCERRADO - OPERACAO NORMALIZADA", C.V, ">>> ")
log("Failover: DR assumiu dentro do RTO de 8h (BIA)", C.V)
log("Failback: retorno seguro ao ambiente principal", C.V)
log("Vulnerabilidade corrigida: queries parametrizadas", C.V)
log("LGPD: notificacao ANPD dentro do prazo de 72h", C.V)
log("Logs salvos em: logs/cenario2.log e logs/dados_vazados.txt", C.CI)