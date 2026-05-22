# Segurança de Sistemas Computacionais — Projeto Acadêmico

## Sobre o Projeto

Este projeto foi desenvolvido para a disciplina de Segurança de Sistemas Computacionais, com foco em:

- Continuidade operacional
- Disaster Recovery (DR)
- Simulação de incidentes de segurança
- Recuperação de desastres
- Ambientes Linux voltados para servidores

A proposta utiliza Alpine Linux executando via Docker, juntamente com Python para automações e simulações de incidentes.

---

# Objetivos

O projeto busca demonstrar, de forma prática e didática:

- Simulação de ataques cibernéticos
- Impactos na disponibilidade de serviços
- Estratégias de recuperação
- Failover e failback
- Continuidade operacional
- Administração básica de servidores Linux
- Automação de processos com Python

---

# Tecnologias Utilizadas

| Tecnologia | Objetivo |
|---|---|
| Alpine Linux | Sistema operacional leve para servidores |
| Docker | Virtualização baseada em containers |
| Python | Automação e scripts de simulação |
| Git | Controle de versão |
| PuTTY | Acesso remoto via SSH |
| Shell Script | Automação Linux |
| SQLite / CSV | Simulação de dados corporativos |

---

# Arquitetura do Ambiente

```text
Host Linux/Windows
│
├── Docker
│   └── Alpine Linux
│       ├── SSH
│       ├── Python
│       ├── Scripts
│       ├── Backups
│       └── Logs
│
└── PuTTY → Acesso SSH
