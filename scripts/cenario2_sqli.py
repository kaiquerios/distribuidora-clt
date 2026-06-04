"""CENARIO 2 - SQL Injection + Failover + Failback
Executa via PuTTY: python3 /scripts/cenario2_sqli.py"""

import subprocess, time, datetime, os

class C:
    R="\033[0m"; V="\033[92m"; A="\033[93m"; E="\033[91m"
    CI="\033[96m"; B="\033[1m"

def log(msg, cor=C.R, pre=""):
    h = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"{cor}{pre}[{h}] {msg}{C.R}")
    with open("/logs/cenario2.log", "a") as f:
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

def exec_host(container, cmd):
    """Executa comando num container via docker exec (do host Windows)."""
    r = subprocess.run(
        ["docker", "exec", container, "sh", "-c", cmd],
        capture_output=True, text=True
    )
    return r.stdout.strip(), r.returncode

def exec_ssh(host, cmd):
    """Executa comando via SSH interno entre containers."""
    r = subprocess.run(
        ["ssh", "-o", "StrictHostKeyChecking=no",
         "-p", "22", f"root@{host}", cmd],
        capture_output=True, text=True
    )
    return r.stdout.strip(), r.returncode

def container_online(nome):
    r = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", nome],
        capture_output=True, text=True
    )
    return r.stdout.strip() == "true"

def status(nome):
    return f"{C.V}[ONLINE]{C.R}" if container_online(nome) else f"{C.E}[OFFLINE]{C.R}"

os.makedirs("/logs", exist_ok=True)
open("/logs/cenario2.log", "w").close()

sep("CENARIO 2 - SQL INJECTION + FAILOVER + FAILBACK", C.CI)
log("CLT Distribuidora S.A. - Simulacao de Incidente P1")
log("Stack: Alpine Linux 3.19 + SQLite + Docker")
log("Executando a partir do container: srv-atacante", C.CI)
log("Alvo: srv-producao (endpoint de busca de pecas)", C.E, ">>> ")

aguardar("Pressione ENTER para iniciar o cenario...")

sep("FASE 1 - SITUACAO NORMAL")
print(f"  srv-producao: {status('clt-producao')}")
print(f"  srv-dr:       {status('clt-dr')} (standby)\n")

out, _ = exec_ssh("srv-producao",
    "sqlite3 /app/banco/clt.db 'SELECT id,nome,cnpj FROM clientes;'")
log(f"Clientes cadastrados em srv-producao:\n{out}", C.V)

aguardar("Sistema normal. ENTER para simular o ataque de SQL Injection...")

sep("FASE 2 - ATAQUE DE SQL INJECTION", C.E)
log("Varrendo endpoints do CRM em busca de vulnerabilidades...", C.A)
time.sleep(1)
log("Endpoint vulneravel encontrado: /buscar-peca?nome=", C.E, "!!! ")
time.sleep(0.8)

query_maliciosa = "' OR '1'='1'; SELECT id,nome,cnpj,email FROM clientes; --"
log("Injetando payload malicioso no endpoint:", C.E, "!!! ")
print(f"\n    {C.E}{query_maliciosa}{C.R}\n")
time.sleep(1)

log("Query bypassa autenticacao e acessa tabela de clientes!", C.E, "!!! ")
time.sleep(0.5)

# Executar a query no banco de producao
out, _ = exec_ssh("srv-producao",
    "sqlite3 /app/banco/clt.db 'SELECT id,nome,cnpj,email FROM clientes;'")

# Salvar dados vazados como evidencia
with open("/logs/dados_vazados.txt", "w") as f:
    f.write("=" * 50 + "\n")
    f.write("DADOS EXFILTRADOS PELO ATACANTE\n")
    f.write(f"Timestamp: {datetime.datetime.now()}\n")
    f.write("=" * 50 + "\n\n")
    f.write(out)
    f.write("\n\n" + "=" * 50 + "\n")

log("DADOS VAZADOS e salvos pelo atacante!", C.E, "!!! ")
log("Expostos: nomes, CNPJs e e-mails de 5 clientes B2B", C.E, "!!! ")
log("Evidencia salva em: /logs/dados_vazados.txt", C.A)
time.sleep(0.5)

aguardar("ENTER para derrubar o servidor de producao...")

log("Sobrecarregando srv-producao com requisicoes maliciosas...", C.E, "!!! ")
time.sleep(1)
subprocess.run(["docker", "stop", "clt-producao"], capture_output=True)
time.sleep(1)
log("PRODUCAO OFFLINE - CRM INDISPONIVEL", C.E, "!!! ")
print(f"\n  srv-producao: {status('clt-producao')}")
print(f"  srv-dr:       {status('clt-dr')}\n")

aguardar("ENTER para acionar o CSIRT e ativar o DR...")

sep("FASE 3 - ACIONAMENTO", C.A)
log("SIEM confirmou: SQL Injection + indisponibilidade total", C.A)
log("Coordenador de Incidentes acionado", C.A)
log("DPO notificado - dados pessoais de clientes expostos (LGPD)", C.A)
log("Prazo de 72h para notificar ANPD iniciado (Art. 48)", C.A)
log(f"Timestamp: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", C.A)

aguardar("ENTER para ativar o Disaster Recovery...")

sep("FASE 4 - FAILOVER: ATIVANDO DR", C.A)
log("Producao indisponivel - verificando DR...", C.A)
time.sleep(1)

out, _ = exec_ssh("srv-dr",
    "sqlite3 /app/banco/clt_dr.db 'SELECT COUNT(*) FROM clientes;'")
log(f"DR integro - {out} clientes disponiveis no banco de DR", C.V)
time.sleep(0.5)

log("Redirecionando trafego do CRM para srv-dr...", C.A)
time.sleep(1)
log("FAILOVER CONCLUIDO - srv-dr assumiu a operacao!", C.V, ">>> ")

print(f"\n  srv-producao: {status('clt-producao')}")
print(f"  srv-dr:       {status('clt-dr')} {C.V}(ATIVO){C.R}\n")

aguardar("ENTER para remediar a vulnerabilidade e restaurar producao...")

sep("FASE 5 - REMEDIACAO", C.A)
log("Corrigindo vulnerabilidade de SQL Injection...", C.A)
time.sleep(1)
log("Causa raiz: concatenacao direta de string na query SQL", C.A)
log("Correcao aplicada: queries parametrizadas em todos endpoints", C.V)
time.sleep(0.8)
log("Regras do WAF atualizadas para bloquear payloads similares", C.V)
log("Reiniciando srv-producao com correcoes aplicadas...", C.A)

subprocess.run(["docker", "start", "clt-producao"], capture_output=True)
time.sleep(4)

log("srv-producao reiniciado e corrigido!", C.V)
out, _ = exec_ssh("srv-producao",
    "sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM clientes;'")
log(f"Banco de producao ok - {out} clientes", C.V)

aguardar("ENTER para iniciar o failback...")

sep("FASE 6 - FAILBACK: RETORNO A PRODUCAO", C.CI)
log("Ambiente principal corrigido - iniciando failback...", C.V)
time.sleep(1)

log("Passo 1: Sincronizando dados do DR para producao...", C.A)
time.sleep(1)
out, _ = exec_ssh("srv-dr",
    "sqlite3 /app/banco/clt_dr.db 'SELECT COUNT(*) FROM pedidos;'")
log(f"Pedidos no DR sincronizados: {out}", C.V)
log("Zero perda de dados confirmada", C.V)
time.sleep(1)

log("Passo 2: Validando ambiente principal...", C.A)
time.sleep(1)
todos_ok = True
for tabela in ["clientes", "pedidos", "catalogo"]:
    out, _ = exec_ssh("srv-producao",
        f"sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM {tabela};'")
    ok = out.strip() == "5"
    st = f"{C.V}[OK]{C.R}" if ok else f"{C.E}[FALHA]{C.R}"
    print(f"    {st} Tabela {tabela}: {out} registro(s)")
    if not ok:
        todos_ok = False
    time.sleep(0.4)

if todos_ok:
    log("Todos os testes passaram - producao pronta!", C.V)

aguardar("ENTER para migrar usuarios de volta para producao...")

log("Passo 3: Migrando usuarios de volta (gradual)...", C.A)
time.sleep(0.8)
log("  Equipe interna migrada com sucesso", C.V)
time.sleep(0.8)
log("  Representantes externos migrados com sucesso", C.V)
time.sleep(0.8)
log("FAILBACK CONCLUIDO!", C.V, ">>> ")
log("Passo 4: Monitoramento intensivo ativado (48 horas)", C.CI)
log("Passo 5: srv-dr retornando ao modo standby", C.CI)

print(f"\n  srv-producao: {status('clt-producao')} {C.V}(ATIVO){C.R}")
print(f"  srv-dr:       {status('clt-dr')} (standby)\n")

aguardar("ENTER para encerrar o incidente...")

sep("FASE 7 - OBRIGACOES LEGAIS", C.CI)
log("Notificacao formal preparada para ANPD (LGPD Art. 48)", C.A)
log("Dados expostos: nomes, CNPJs e e-mails de 5 clientes B2B", C.A)
log("Comunicado aos clientes aguardando aprovacao juridica", C.A)
log("Relatorio encaminhado ao Comite de Gestao de Risco", C.A)

sep("RESULTADO DO CENARIO 2", C.V)
log("INCIDENTE ENCERRADO - OPERACAO NORMALIZADA", C.V, ">>> ")
log("Failover: DR assumiu dentro do RTO de 8h (BIA)", C.V)
log("Failback: retorno seguro ao ambiente principal", C.V)
log("Vulnerabilidade corrigida: queries parametrizadas", C.V)
log("LGPD: notificacao ANPD dentro do prazo de 72h", C.V)
log("Evidencias: /logs/cenario2.log e /logs/dados_vazados.txt", C.CI)
print()