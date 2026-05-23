import sqlite3, time

DB_PATH = "/app/banco/clt_dr.db"

def criar_banco_dr(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY, nome TEXT NOT NULL,
            cnpj TEXT NOT NULL, email TEXT, telefone TEXT);
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY, cliente_id INTEGER,
            produto TEXT NOT NULL, quantidade INTEGER,
            valor REAL, status TEXT);
        CREATE TABLE IF NOT EXISTS catalogo (
            id INTEGER PRIMARY KEY, codigo TEXT NOT NULL,
            descricao TEXT NOT NULL, preco REAL, estoque INTEGER);
        INSERT OR IGNORE INTO clientes VALUES
            (1,"Auto Pecas Nobre","12.345.678/0001-99","nobre@email.com","(71)99999-0001"),
            (2,"Oficina Central","23.456.789/0001-88","central@email.com","(71)99999-0002"),
            (3,"Concessionaria Sul","34.567.890/0001-77","sul@email.com","(71)99999-0003"),
            (4,"Mecanica Rapida","45.678.901/0001-66","rapida@email.com","(71)99999-0004"),
            (5,"Distribuidora Norte","56.789.012/0001-55","norte@email.com","(71)99999-0005");
        INSERT OR IGNORE INTO pedidos VALUES
            (1001,1,"Filtro de Oleo Bosch",10,850.00,"EM TRANSITO"),
            (1002,2,"Pastilha de Freio Jurid",20,1200.00,"APROVADO"),
            (1003,3,"Correia Dentada Gates",5,625.00,"AGUARDANDO"),
            (1004,4,"Vela de Ignicao NGK",50,750.00,"EM TRANSITO"),
            (1005,5,"Amortecedor Cofap",8,2400.00,"APROVADO");
        INSERT OR IGNORE INTO catalogo VALUES
            (1,"FO-001","Filtro de Oleo Bosch",85.00,150),
            (2,"PF-002","Pastilha de Freio Jurid",60.00,200),
            (3,"CD-003","Correia Dentada Gates",125.00,80),
            (4,"VI-004","Vela de Ignicao NGK",15.00,500),
            (5,"AM-005","Amortecedor Cofap",300.00,60);
    """)
    conn.commit()
    conn.close()
    print(f"[OK] Banco DR criado: {path}")

criar_banco_dr(DB_PATH)
print("[STANDBY] Container DR ONLINE - aguardando failover...")
while True:
    time.sleep(60)