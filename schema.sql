CREATE TABLE IF NOT EXISTS cliente (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nome       TEXT NOT NULL,
    telefone   TEXT NOT NULL,
    email      TEXT
);
CREATE TABLE IF NOT EXISTS servico (
    id_servico INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao  TEXT NOT NULL,
    duracao_min INTEGER NOT NULL,
    preco      REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS profissional (
    id_profissional INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS agendamento (
    id_agendamento INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente      INTEGER NOT NULL REFERENCES cliente(id_cliente),
    id_servico      INTEGER NOT NULL REFERENCES servico(id_servico),
    id_profissional INTEGER NOT NULL REFERENCES profissional(id_profissional),
    data_hora       TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'AGENDADO',
    UNIQUE (id_profissional, data_hora)
);
