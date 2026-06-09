# CLT Distribuidora S.A.

> **UNIFACS - Engenharia de Software**  
> UC: Segurança em Sistemas Computacionais  
> Orientador: Prof. Sérgio Spinola  
> Avaliação: A3

---

## Resumo do Projeto

Este repositório contém a demonstração prática do **Plano de Continuidade de Negócios (PCN)** da CLT Distribuidora S.A., empresa fictícia de distribuição de peças automotivas com operação 100% em nuvem.

O projeto simula dois cenários reais de ataque cibernético e recuperação de desastres, executados em containers Alpine Linux comunicando-se por uma rede Docker interna. Os ataques são executados a partir de um container atacante e impactam um container de produção com banco de dados real (SQLite). Um terceiro container simula o ambiente de Disaster Recovery (DR).

---

## Arquitetura

```
Windows (VS Code + Docker Desktop)
│
└── Docker Compose
    │
    ├── clt-atacante  (Alpine Linux 3.19)
    │   ├── SSH porta 2221
    │   ├── Python 3 + Fernet (AES-128)
    │   └── Scripts de ataque em /scripts/
    │
    ├── clt-producao  (Alpine Linux 3.19)
    │   ├── SSH porta 2222
    │   ├── Python 3 + SQLite
    │   ├── Banco de dados: /app/banco/clt.db
    │   ├── Backup WORM:    /app/backup/clt_backup.db
    │   └── Logs:           /app/logs/incidente.log
    │
    └── clt-dr        (Alpine Linux 3.19)
        ├── SSH porta 2223
        ├── Python 3 + SQLite
        ├── Banco DR: /app/banco/clt_dr.db
        └── Logs:     /app/logs/incidente_dr.log

Rede interna: distribuidora-clt_rede-clt (bridge)
```

---

## Stack

| Tecnologia | Versão | Função |
|---|---|---|
| Alpine Linux | 3.19 | Sistema operacional dos três servidores |
| Docker Desktop | 29+ | Orquestração dos containers |
| Docker Compose | v2 | Definição da infraestrutura |
| Python | 3.11 | Scripts de ataque e recuperação |
| Fernet (cryptography) | 48.0 | Criptografia AES-128 real (ransomware) |
| SQLite | 3.44 | Banco de dados da CLT Distribuidora |
| OpenSSH | 9.6 | Acesso remoto via PuTTY |
| PuTTY | - | Cliente SSH para acesso aos containers |
| Git + GitHub | - | Versionamento do projeto |

---

## Estrutura do Repo

```
distribuidora-clt/
│
├── docker/
│   ├── atacante/
│   │   ├── Dockerfile        ← Alpine + SSH + Python + Fernet
│   │   └── (scripts montados via volume)
│   │
│   ├── producao/
│   │   ├── Dockerfile        ← Alpine + SSH + Python + SQLite
│   │   └── init_banco.py     ← Cria banco SQLite com dados da CLT
│   │
│   └── dr/
│       ├── Dockerfile        ← Alpine + SSH + Python + SQLite
│       └── init_dr.py        ← Cria réplica do banco no DR
│
├── scripts/
│   ├── cenario1_ransomware.py  ← Cenário 1: Ransomware + Restore
│   └── cenario2_sqli.py        ← Cenário 2: SQL Injection + Failover + Failback
│
├── logs/                       ← Gerado em execução (evidências)
├── docker-compose.yml
└── README.md
```

---

## Banco de Dados

O banco SQLite da CLT Distribuidora contém três tabelas:

**clientes:** 5 registros (oficinas e concessionárias B2B)  
**pedidos:** 5 pedidos ativos de peças automotivas  
**catalogo:** 5 peças com código, preço e estoque

---

## Cenários Demonstrados

### Cenário 1 — Ataque de Ransomware

| Fase | Descrição |
|---|---|
| 1. Situação normal | Banco consultado ao vivo via SSH |
| 2. Ataque | Fernet AES-128 criptografa o banco — `clt.db` vira `clt.db.locked` |
| 3. Acionamento | CSIRT notificado, timestamp registrado |
| 4. Contenção | Container isolado via `iptables DROP` |
| 5. Restore | Backup WORM restaurado com verificação MD5 |
| 6. Validação | 3 tabelas validadas — 5 registros cada |
| 7. Encerramento | Notificação ANPD (LGPD Art. 48, prazo 72h) |

**Ferramenta de criptografia:** Fernet (AES-128 + HMAC-SHA256)  
**Evidências geradas:** `cenario1.log`, `chave_ransomware.key`, `incidente.log`

---

### Cenário 2 — SQL Injection + Failover + Failback

| Fase | Descrição |
|---|---|
| 1. Situação normal | Produção e DR online monitorados ao vivo |
| 2. SQL Injection | Query maliciosa exfiltra tabela de clientes |
| 3. Acionamento | SIEM confirma ataque, prazo ANPD iniciado |
| 4. Failover | DR assume a operação com 5 clientes e 5 pedidos |
| 5. Remediação | Queries parametrizadas aplicadas, produção reinicia |
| 6. Failback | Dados sincronizados, usuários migrados gradualmente |
| 7. Encerramento | Notificação ANPD, DR retorna ao standby |

**Evidências geradas:** `cenario2.log`, `dados_vazados.txt`, `incidente.log`, `incidente_dr.log`

---

## Como Executar

### Pré-requisitos

- Docker Desktop instalado e funcionando
- Python 3.10+
- PuTTY instalado
- Git

### Subir o ambiente

```powershell
docker compose down -v
docker compose up -d --build
docker ps
```

### Conectar via PuTTY

| Sessão | Host | Porta | Login | Senha |
|---|---|---|---|---|
| CLT-Atacante | localhost | 2221 | root | clt2026 |
| CLT-Producao | localhost | 2222 | root | clt2026 |
| CLT-DR | localhost | 2223 | root | clt2026 |

### Preparar monitoramento

**Na produção:**
```bash
mkdir -p /app/logs && touch /app/logs/incidente.log && tail -f /app/logs/incidente.log
```

**No DR:**
```bash
mkdir -p /app/logs && touch /app/logs/incidente_dr.log && tail -f /app/logs/incidente_dr.log
```

### Executar os cenários

**Cenário 1 | No atacante:**
```bash
python3 /scripts/cenario1_ransomware.py
```

**Resetar entre cenários:**
```powershell
docker compose down -v
docker compose up -d --build
```

**Cenário 2 | No atacante:**
```bash
python3 /scripts/cenario2_sqli.py
```

---

## Relação com o PCN

| Elemento do PCN | Demonstrado em |
|---|---|
| BIA — processos críticos identificados | Banco com clientes, pedidos e catálogo |
| RTO — tempo máximo de indisponibilidade | Cenário 1 (4h) e Cenário 2 (8h) |
| RPO — perda máxima de dados | Backup WORM incremental a cada hora |
| Backup WORM imutável | Cenário 1 — restore via `/app/backup/` |
| Disaster Recovery | Cenário 2 — failover para `clt-dr` |
| Failback seguro | Cenário 2 — retorno gradual à produção |
| LGPD — notificação ANPD 72h | Ambos os cenários |
| Isolamento de rede | Cenário 1 — `iptables DROP` |
| Criptografia AES | Cenário 1 — Fernet AES-128 |
