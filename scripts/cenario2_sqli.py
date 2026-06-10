"""
CENARIO 2 - SQL Injection + Failover + Failback
"""

import subprocess, time, datetime, os

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
    with open("/logs/cenario2.log", "a") as f:
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
    """Uma conexao SSH com um ou varios comandos encadeados."""
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

exec_ssh("srv-producao",
    "mkdir -p /app/logs && > /app/logs/incidente.log")
exec_ssh("srv-dr",
    "mkdir -p /app/logs && > /app/logs/incidente_dr.log")

sep("CENARIO 2 - SQL INJECTION + FAILOVER + FAILBACK", C.CI)
log(f"Atacante: srv-atacante", C.CI)
log(f"Alvo:     srv-producao", C.E, ">>> ")
aguardar("Iniciar...")

# ════════════════════════════════════════════════════════════
# FASE 1 - 1 conexao SSH producao + 1 conexao SSH dr
# ════════════════════════════════════════════════════════════
sep("FASE 1 - SITUACAO NORMAL")

print(f"  srv-producao: {C.V}[ONLINE]{C.R}")
print(f"  srv-dr:       {C.V}[ONLINE]{C.R} (standby)\n")

# Producao: verificar banco e registrar log (1 senha)
CMD_FASE1_PROD = (
    "mkdir -p /app/logs && "
    "echo '[OK] Sistema CRM operando normalmente' >> /app/logs/incidente.log && "
    "echo '[OK] Equipe de vendas registrando pedidos' >> /app/logs/incidente.log && "
    "sqlite3 /app/banco/clt.db 'SELECT id,nome,cnpj FROM clientes;'"
)
out, _ = exec_ssh("srv-producao", CMD_FASE1_PROD)
log(f"Clientes cadastrados em srv-producao:\n{out}", C.V)

# DR: confirmar standby (1 senha)
CMD_FASE1_DR = (
    "mkdir -p /app/logs && "
    "echo '[STANDBY] DR em modo de espera, aguardando failover' >> /app/logs/incidente_dr.log"
)
exec_ssh("srv-dr", CMD_FASE1_DR)
log("srv-dr em standby e sincronizado", C.V)

aguardar("Sistema normal. Podemos começar o ataque de SQL Injection?")

# ════════════════════════════════════════════════════════════
# FASE 2 - 1 conexao SSH producao (ataque + exfiltracao + derrubada)
# ════════════════════════════════════════════════════════════
sep("FASE 2 - ATAQUE DE SQL INJECTION", C.E)
log("Varrendo endpoints do CRM em busca de vulnerabilidades...", C.A)
time.sleep(1)
log("Endpoint vulneravel encontrado: /buscar-peca?nome=", C.E, "!!! ")
time.sleep(0.8)

query = "' OR '1'='1'; SELECT id,nome,cnpj,email FROM clientes; --"
log("Injetando payload malicioso:", C.E, "!!! ")
print(f"\n    {C.E}{query}{C.R}\n")
time.sleep(1)

# 1 conexao SSH: executar SQLi + registrar logs (1 senha)
CMD_SQLI = (
    "sqlite3 /app/banco/clt.db 'SELECT id,nome,cnpj,email FROM clientes;' && "
    "echo '[CRIT] SQL Injection confirmado, tabela clientes invadida!' >> /app/logs/incidente.log && "
    "echo '[CRIT] Dados expostos: nomes, CNPJs e e-mails de 5 clientes B2B' >> /app/logs/incidente.log && "
    "echo '[CRIT] CRM INDISPONIVEL, servidor sobrecarregado!' >> /app/logs/incidente.log"
)
out, _ = exec_ssh("srv-producao", CMD_SQLI)

# Salvar dados vazados como evidencia
with open("/logs/dados_vazados.txt", "w") as f:
    f.write("=" * 50 + "\n")
    f.write("DADOS EXFILTRADOS PELO ATACANTE\n")
    f.write(f"Timestamp: {datetime.datetime.now()}\n")
    f.write("=" * 50 + "\n\n")
    f.write(out)
    f.write("\n\n" + "=" * 50 + "\n")

log("Dados vazados e salvos pelo atacante!", C.E, "!!! ")
log("Expostos: nomes, CNPJs e e-mails de 5 clientes B2B", C.E, "!!! ")
log("Historico salvo em: /logs/dados_vazados.txt", C.A)
time.sleep(0.5)

aguardar("Derrubar o servidor de producao?")

log("Sobrecarregando srv-producao com requisicoes maliciosas...", C.E, "!!! ")
time.sleep(1)
exec_ssh("srv-producao",
    "echo '[CRIT] Servidor sobrecarregado, encerrando servicos...' >> /app/logs/incidente.log && "
    "killall sshd || true"
)
time.sleep(2)
time.sleep(1)
log("PRODUCAO OFFLINE - CRM INDISPONIVEL", C.E, "!!! ")
print(f"\n  srv-producao: {C.E}[OFFLINE]{C.R}")
print(f"  srv-dr:       {C.V}[ONLINE]{C.R}\n")

aguardar("Acionar o CSIRT e ativar o DR?")

# ════════════════════════════════════════════════════════════
# FASE 3 - 1 conexao SSH dr (logs do acionamento)
# ════════════════════════════════════════════════════════════
sep("FASE 3 - ACIONAMENTO", C.A)
log("Confirmado SQL Injection e indisponibilidade total", C.A)
log("Coordenador de Incidentes acionado", C.A)
log("DPO notificado (LGPD)", C.A)
ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
log(f"Prazo de 72h para ANPD iniciado: {ts}", C.A)

CMD_CSIRT_DR = (
    f"echo '[CSIRT] Incidente P1 - SQL Injection confirmado' >> /app/logs/incidente_dr.log && "
    f"echo '[CSIRT] Timestamp: {ts}' >> /app/logs/incidente_dr.log && "
    f"echo '[CSIRT] Prazo ANPD 72h iniciado' >> /app/logs/incidente_dr.log"
)
exec_ssh("srv-dr", CMD_CSIRT_DR)
aguardar("Ativar o Disaster Recovery?")

# ════════════════════════════════════════════════════════════
# FASE 4 - 1 conexao SSH dr (failover)
# ════════════════════════════════════════════════════════════
sep("FASE 4 - FAILOVER", C.A)
log("Producao indisponivel, verificando DR...", C.A)
time.sleep(1)

CMD_FAILOVER = (
    "sqlite3 /app/banco/clt_dr.db 'SELECT COUNT(*) FROM clientes;' && "
    "sqlite3 /app/banco/clt_dr.db 'SELECT COUNT(*) FROM pedidos;' && "
    "echo '[FAILOVER] DR assumiu a operacao, CRM disponivel via DR' >> /app/logs/incidente_dr.log"
)
out, _ = exec_ssh("srv-dr", CMD_FAILOVER)
linhas = out.split("\n")
clientes_dr = linhas[0] if len(linhas) > 0 else "?"
pedidos_dr  = linhas[1] if len(linhas) > 1 else "?"

log(f"DR integro - {clientes_dr} clientes disponiveis", C.V)
log(f"DR integro - {pedidos_dr} pedidos disponiveis", C.V)
time.sleep(0.5)
log("Redirecionando trafego do CRM para srv-dr...", C.A)
time.sleep(1)
log("FAILOVER CONCLUIDO - srv-dr assumiu a operacao!", C.V, ">>> ")

print(f"\n  srv-producao: {C.E}[OFFLINE]{C.R}")
print(f"  srv-dr:       {C.V}[ONLINE]{C.R} {C.V}(ATIVO){C.R}\n")

aguardar("Remediar a vulnerabilidade e restaurar producao?")

# ════════════════════════════════════════════════════════════
# FASE 5 - reiniciar producao + 1 conexao SSH producao (correcao)
# ════════════════════════════════════════════════════════════
sep("FASE 5 - REMEDIACAO", C.A)
log("Corrigindo vulnerabilidade de SQL Injection...", C.A)
time.sleep(1)
log("A causa raiz foi uma concatenacao direta de string na query SQL", C.A)
log("A solução seria queries parametrizadas em todos os endpoints", C.V)
time.sleep(0.8)
log("Regras do WAF atualizadas para bloquear payloads similares", C.V)
log("Reiniciando srv-producao com correcoes aplicadas...", C.A)

exec_ssh("srv-producao",
    "mv /app/banco/clt.db.offline /app/banco/clt.db && "
    "echo '[OK] srv-producao restaurado com correcoes aplicadas' >> /app/logs/incidente.log"
)
time.sleep(1)

# 1 conexao SSH: verificar banco + registrar correcao (1 senha)
CMD_REMEDIAR = (
    "sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM clientes;' && "
    "echo '[OK] Vulnerabilidade solucionada!!' >> /app/logs/incidente.log && "
    "echo '[OK] srv-producao reiniciado e corrigido' >> /app/logs/incidente.log"
)
out, _ = exec_ssh("srv-producao", CMD_REMEDIAR)
log(f"srv-producao reiniciado - {out.split(chr(10))[0]} clientes no banco", C.V)

aguardar("Iniciar o failback?")

# ════════════════════════════════════════════════════════════
# FASE 6 - 1 conexao SSH producao (validar) + 1 conexao SSH dr (sincronizar)
# ════════════════════════════════════════════════════════════
sep("FASE 6 - FAILBACK", C.CI)
log("Ambiente principal corrigido, iniciar failback.", C.V)
time.sleep(1)

# Sincronizar DR -> producao (1 senha no DR)
log("Passo 1: Sincronizando dados do DR para producao...", C.A)
CMD_SINC_DR = (
    "sqlite3 /app/banco/clt_dr.db 'SELECT COUNT(*) FROM pedidos;' && "
    "echo '[FAILBACK] Dados sincronizados do DR para producao' >> /app/logs/incidente_dr.log"
)
out, _ = exec_ssh("srv-dr", CMD_SINC_DR)
log(f"Pedidos sincronizados do DR: {out.split(chr(10))[0]}", C.V)
log("Zero perda de dados confirmada", C.V)
time.sleep(1)

# Validar producao (1 senha na producao)
log("Passo 2: Validando ambiente principal...", C.A)
time.sleep(1)
CMD_VALIDAR = (
    "sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM clientes;' && "
    "sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM pedidos;' && "
    "sqlite3 /app/banco/clt.db 'SELECT COUNT(*) FROM catalogo;' && "
    "echo '[FAILBACK] Validacao concluida - producao pronta' >> /app/logs/incidente.log"
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
    log("Todos os testes passaram!", C.V)

aguardar("Começar a migrar usuarios de volta para producao.")

log("Passo 3: Migrando usuarios de volta de forma gradual...", C.A)
time.sleep(0.8)
log("  Equipe interna migrada com sucesso", C.V)
time.sleep(0.8)
log("  Representantes externos migrados com sucesso", C.V)
time.sleep(0.8)
log("FAILBACK CONCLUIDO!", C.V, ">>> ")
log("Monitoramento intensivo ativado", C.CI)
log("srv-dr retornando ao modo standby", C.CI)

# Registrar encerramento no DR (1 senha)
exec_ssh("srv-dr",
    "echo '[STANDBY] DR retornou ao modo standby' >> /app/logs/incidente_dr.log")

print(f"\n  srv-producao: {C.V}[ONLINE]{C.R} {C.V}(ATIVO){C.R}")
print(f"  srv-dr:       {C.V}[ONLINE]{C.R} (standby)\n")

aguardar("Encerrar o incidente.")

# ════════════════════════════════════════════════════════════
# FASE 7 - 1 conexao SSH producao + 1 conexao SSH dr (logs finais)
# ════════════════════════════════════════════════════════════
sep("FASE 7 - OBRIGACOES LEGAIS", C.CI)

CMD_LGPD_PROD = (
    "echo '[LGPD] Notificacao formal preparada para ANPD (Art. 48)' >> /app/logs/incidente.log && "
    "echo '[LGPD] Dados expostos: nomes, CNPJs e e-mails de 5 clientes' >> /app/logs/incidente.log && "
    "echo '[OK] CRM liberado para os usuarios' >> /app/logs/incidente.log"
)
exec_ssh("srv-producao", CMD_LGPD_PROD)

CMD_LGPD_DR = (
    "echo '[LGPD] Comunicado aos clientes aguardando aprovacao juridica' >> /app/logs/incidente_dr.log && "
    "echo '[OK] Incidente encerrado, operacao normalizada' >> /app/logs/incidente_dr.log"
)
exec_ssh("srv-dr", CMD_LGPD_DR)

log("Notificacao formal preparada para ANPD (LGPD Art. 48)", C.A)
log("Dados expostos: nomes, CNPJs e e-mails de 5 clientes B2B", C.A)
log("Comunicado aos clientes aguardando aprovacao juridica", C.A)

sep("RESULTADO DO CENARIO 2", C.V)
log("INCIDENTE ENCERRADO - OPERACAO NORMALIZADA", C.V, ">>> ")
log("Failover: DR assumiu dentro do RTO de 8h (BIA)", C.V)
log("Failback: retorno seguro ao ambiente principal", C.V)
log("Vulnerabilidade corrigida: queries parametrizadas", C.V)
log("LGPD: notificacao ANPD dentro do prazo de 72h", C.V)
log("Log do atacante:  /logs/cenario2.log", C.CI)
log("Log da producao:  /app/logs/incidente.log", C.CI)
log("Log do DR:        /app/logs/incidente_dr.log", C.CI)
log("Evidencias:       /logs/dados_vazados.txt", C.CI)
print()