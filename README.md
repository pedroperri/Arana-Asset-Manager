# 🕷️ Arana System - Enterprise Asset Manager

> Sistema de gestão de inventário de T.I. e Arquivo Morto com controle de acesso e design moderno.

## 🚀 Sobre o Projeto
Desenvolvi o **Arana System** para resolver um problema real de organização de ativos corporativos. O sistema permite gerenciar caixas de arquivo morto e inventário de equipamentos de T.I. em uma única interface, garantindo integridade de dados e facilidade de uso.

O diferencial é o **Controle de Acesso (RBAC)**, onde diferentes perfis (Admin, T.I., Escritório) visualizam apenas o que é pertinente à sua função.

## 🛠️ Tecnologias Utilizadas
- **Linguagem:** Python 3.12
- **Interface Gráfica (GUI):** CustomTkinter (Design System moderno)
- **Banco de Dados:** SQLite3 (Local e robusto)
- **Segurança:** Hash de senhas com SHA-256
- **Build:** PyInstaller (Compilação para .exe)

## ✨ Funcionalidades Principais
- **Login Seguro:** Autenticação com hash e proteção contra SQL Injection.
- **Sistema de Cargos:**
  - 🛡️ **Admin:** Acesso total + Painel de Configurações e Logs.
  - 💻 **T.I.:** Acesso exclusivo ao inventário de tecnologia.
  - 📂 **Escritório:** Acesso exclusivo ao arquivo morto.
- **Auditoria:** Logs automáticos de quem entrou, criou ou deletou itens.
- **UI/UX:** Interface Dark Mode inspirada no ecossistema Apple/GitHub, com foco em usabilidade.
- **Busca Inteligente:** Filtragem em tempo real por múltiplos critérios (ID, Tag, Nome).

## 📦 Como Rodar o Projeto
```bash
# Clone este repositório
git clone [https://github.com/pedroperri/Arana-Asset-Manager.git](https://github.com/pedroperri/Arana-Asset-Manager.git)

# Instale as dependências
pip install customtkinter packaging

# Execute o sistema
python sistema_estoque.py
