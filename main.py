import streamlit as st
import sqlite3

# Inicializa o banco de dados SQLite
conn = sqlite3.connect("ueg_jobs.db", check_same_thread=False)
cursor = conn.cursor()

# Cria as tabelas se não existirem

# tabela de usuários
cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    )
    """)


# tabelas de vagas
cursor.execute("""
    CREATE TABLE IF NOT EXISTS vagas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        descricao TEXT NOT NULL,
        empresa TEXT NOT NULL
    )
    """)

conn.commit()

# Funções auxiliares usando SQLite
def cadastrar_usuario(nome, email, senha):
    try:
        cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
        conn.commit()
    except sqlite3.IntegrityError:
        st.warning("Email já cadastrado.")

def criar_vaga(titulo, descricao, empresa):
    cursor.execute("INSERT INTO vagas (titulo, descricao, empresa) VALUES (?, ?, ?)", (titulo, descricao, empresa))
    conn.commit()

def autenticar(email, senha):
    cursor.execute("SELECT nome, email FROM usuarios WHERE email=? AND senha=?", (email, senha))
    usuario = cursor.fetchone()
    if usuario:
        return {"nome": usuario[0], "email": usuario[1]}
    return None

def listar_vagas():
    cursor.execute("SELECT id,titulo, descricao, empresa FROM vagas")
    return cursor.fetchall()

def delete_vaga(vaga_id):
    cursor.execute("DELETE FROM vagas WHERE id=?", (vaga_id,))
    conn.commit()

# Interface Streamlit
st.set_page_config(page_title="UEG-Jobs", page_icon=":briefcase:")
st.title("UEG-Jobs - Vagas para alunos da UEG")


menu = st.sidebar.selectbox("Menu", ["Cadastro", "Login", "Criar Vaga", "Listar Vagas"])

if menu == "Cadastro":
    st.header("Cadastro de Usuário")
    nome = st.text_input("Nome")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Cadastrar"):
        if nome and email and senha:
            cadastrar_usuario(nome, email, senha)
            st.success("Usuário cadastrado com sucesso!")
        else:
            st.warning("Preencha todos os campos.")

elif menu == "Login":
    st.header("Login")
    email = st.text_input("Email", key="login_email")
    senha = st.text_input("Senha", type="password", key="login_senha")
    if st.button("Entrar"):
        usuario = autenticar(email, senha)
        if usuario:
            st.success(f"Bem-vindo, {usuario['nome']}!")
            st.session_state['autenticado'] = True
        else:
            st.error("Credenciais inválidas.")

elif menu == "Criar Vaga":
    if 'autenticado' not in st.session_state or not st.session_state['autenticado']:
        st.error("Você precisa estar logado para criar uma vaga.")
        st.stop()
    else: 
        st.header("Criar Vaga")
        titulo = st.text_input("Título da Vaga")
        descricao = st.text_area("Descrição")
        empresa = st.text_input("Empresa")
        if st.button("Publicar Vaga"):
            if titulo and descricao and empresa:
                criar_vaga(titulo, descricao, empresa)
                st.success("Vaga criada com sucesso!")
            else:
                st.warning("Preencha todos os campos.")

elif menu == "Listar Vagas":
    st.header("Vagas Disponíveis")
    vagas = listar_vagas()
    if vagas:
        for vaga in vagas:
            id, titulo, descricao, empresa = vaga
            st.subheader(titulo)
            st.write(f"**Empresa:** {empresa}")
            st.write(descricao)
            

            if st.button(f"Aplicar para {titulo}"):

                if 'autenticado' not in st.session_state or not st.session_state['autenticado']:
                    st.error("Você precisa estar logado para se inscrever na vaga.")
                    continue
                else:
                    st.success(f"Você se inscreveu na vaga: {titulo}")
                    st.success("Em até 24 horas você receberá um email com mais informações.")
                    delete_vaga(id)  # Deleta a vaga após a inscrição
            
            st.markdown("---")
    else:
        st.info("Nenhuma vaga cadastrada ainda.")

    