import os, tempfile
import app as m

db_file = os.path.join(tempfile.mkdtemp(), "teste.db")
m.app.config["DATABASE"] = db_file
m.init_db()
c = m.app.test_client()
resultados = []

def registrar(id_, desc, esperado, obtido, ok):
    resultados.append((id_, desc, esperado, obtido, "APROVADO" if ok else "REPROVADO"))
    print(f"{id_} | {desc}\n   esperado: {esperado}\n   obtido  : {obtido}\n   => {'APROVADO' if ok else 'REPROVADO'}\n")

def conta(tabela):
    import sqlite3
    d = sqlite3.connect(db_file); n = d.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]; d.close(); return n

# CT01 login inválido
r = c.post("/login", data={"usuario": "x", "senha": "y"})
registrar("CT01", "Login com senha incorreta", "Acesso negado, mensagem de erro",
          "Mensagem exibida" if "inválidos" in r.get_data(as_text=True) else "sem mensagem",
          "inválidos" in r.get_data(as_text=True))
c.post("/login", data={"usuario": "atendente", "senha": "1234"})

# CT02 cadastro válido
r = c.post("/clientes/novo", data={"nome": "Marcos Lima", "telefone": "(11) 91234-5678", "email": ""}, follow_redirects=True)
ok = "Cliente cadastrado" in r.get_data(as_text=True) and conta("cliente") == 1
registrar("CT02", "Cadastro de cliente com dados válidos", "Cliente salvo e listado", "Cliente salvo e listado" if ok else "falhou", ok)

# CT03 sem nome
r = c.post("/clientes/novo", data={"nome": "", "telefone": "(11) 91234-5678"}, follow_redirects=True)
ok = "nome é obrigatório" in r.get_data(as_text=True) and conta("cliente") == 1
registrar("CT03", "Cadastro sem preencher o nome", "Mensagem de erro, nada salvo", "Mensagem de erro, nada salvo" if ok else "falhou", ok)

# CT04 telefone inválido
r = c.post("/clientes/novo", data={"nome": "Ana", "telefone": "123"}, follow_redirects=True)
ok = "Telefone inválido" in r.get_data(as_text=True) and conta("cliente") == 1
registrar("CT04", "Cadastro com telefone inválido (3 dígitos)", "Mensagem de erro, nada salvo", "Mensagem de erro, nada salvo" if ok else "falhou", ok)

# CT05 agendamento válido
dados = {"cliente": 1, "servico": 1, "profissional": 1, "data": "2026-11-05", "hora": "10:00"}
r = c.post("/agendar", data=dados, follow_redirects=True)
ok = "Agendamento confirmado" in r.get_data(as_text=True) and conta("agendamento") == 1
registrar("CT05", "Agendar em horário livre", "Agendamento gravado e exibido na agenda", "Agendamento gravado e exibido" if ok else "falhou", ok)

# CT06 horário ocupado
r = c.post("/agendar", data=dados, follow_redirects=True)
ok = "já ocupado" in r.get_data(as_text=True) and conta("agendamento") == 1
registrar("CT06", "Agendar em horário já ocupado (mesmo profissional)", "Sistema impede e avisa", "Sistema impediu e avisou" if ok else "falhou", ok)

# CT07 outro profissional mesmo horário
d2 = dict(dados, profissional=2)
r = c.post("/agendar", data=d2, follow_redirects=True)
ok = "Agendamento confirmado" in r.get_data(as_text=True) and conta("agendamento") == 2
registrar("CT07", "Mesmo horário com outro profissional", "Agendamento permitido", "Agendamento permitido" if ok else "falhou", ok)

# CT08 consulta agenda do dia
r = c.get("/?data=2026-11-05")
t = r.get_data(as_text=True)
ok = "Marcos Lima" in t and "10:00" in t
registrar("CT08", "Consultar agenda do dia 05/11/2026", "Lista com cliente e horário", "Lista exibida" if ok else "falhou", ok)

# CT09 cancelar
r = c.post("/cancelar/1", data={"data": "2026-11-05"}, follow_redirects=True)
ok = "CANCELADO" in r.get_data(as_text=True)
registrar("CT09", "Cancelar agendamento", "Status alterado para CANCELADO", "Status CANCELADO" if ok else "falhou", ok)

# CT10 acesso sem login
c2 = m.app.test_client()
r = c2.get("/")
ok = r.status_code == 302 and "/login" in r.headers["Location"]
registrar("CT10", "Acessar agenda sem estar logado", "Redireciona para o login", "Redirecionado para /login" if ok else "falhou", ok)

print(f"RESUMO: {sum(1 for x in resultados if x[4]=='APROVADO')}/{len(resultados)} aprovados")
import json; json.dump(resultados, open("/home/claude/work/resultados.json", "w"), ensure_ascii=False)
