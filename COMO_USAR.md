# DC Distribuidora — Dashboard Gerencial Executivo

Aplicativo **Streamlit** para análise mensal de DRE, Balanço Patrimonial e indicadores financeiros.
Estruturado para receber **novos meses** sem reescrever código — basta atualizar a planilha de dados.

---

## 1. Instalação (uma única vez)

Pré-requisito: **Python 3.10+** instalado.

Abra o terminal (PowerShell ou Prompt de Comando) na pasta `dc_dashboard` e rode:

```bash
pip install -r requirements.txt
```

Se preferir um ambiente virtual isolado:

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
```

---

## 2. Como rodar o app

Na mesma pasta `dc_dashboard`, execute:

```bash
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`.
Para encerrar: feche o navegador ou pressione `Ctrl+C` no terminal.

---

## 3. Estrutura de arquivos

```
dc_dashboard/
├── app.py                       Aplicativo principal (Streamlit)
├── requirements.txt             Dependências
├── COMO_USAR.md                 Este arquivo
└── dados/
    └── dados_mensais.xlsx       Planilha de dados (3 abas + instruções)
```

---

## 4. Como adicionar novos meses

1. Abra `dados/dados_mensais.xlsx`.
2. Em **cada uma das 3 abas (DRE, Balanco, Indicadores)**, adicione uma nova coluna ao lado da última (ex.: depois de `abr/26`, crie `mai/26`).
3. Preencha os valores nas linhas existentes.
4. **Não renomeie** as abas nem altere a coluna **Bloco/Grupo/Indicador**.
5. Salve o arquivo e atualize o navegador (F5).

A aba **Instruções** dentro do Excel lista os rótulos válidos.

---

## 5. O que o app calcula automaticamente

- KPIs do mês de referência (com variação vs. mês anterior).
- Margens (1, Bruta, EBITDA, Líquida) sobre a **Receita Líquida base Excel** (RB − cancelamentos/devoluções), conforme padrão.
- Totalizações do Balanço Patrimonial (Ativo, Passivo, PL).
- Composição percentual em gráficos de rosca (Ativo / Passivo).
- Evolução temporal de Faturamento, EBITDA, Lucro Líquido, Despesas.
- Indicadores de liquidez, endividamento, capital de giro (NCG, CDG, ST).
- Prazos médios e ciclo financeiro.
- DRE completa filtrável + exportação CSV.

---

## 6. Recursos do app

**Barra lateral:**
- Upload de arquivo .xlsx alternativo (caso queira testar outro cenário).
- Filtro de período (multiseleção de meses).
- Seleção do mês de referência para KPIs.

**Abas:**
1. **Faturamento & Margens** — receita, margem 1, tabela de margens, insight automático.
2. **Resultado & EBITDA** — EBITDA, lucro líquido, acumulado do período.
3. **Despesas** — comerciais, logística, administrativas + % RL.
4. **Balanço** — composição do ativo/passivo, check automático de divergência.
5. **Liquidez & Endividamento** — LC, LG, LI, endividamento, NCG/CDG/ST.
6. **Ciclo Financeiro** — PMR, PMP, PME, ciclo operacional e financeiro.
7. **DRE Completa** — tabela completa + download CSV.

---

## 7. Personalização

- Cores: editar a paleta no início de `app.py` (NAVY, GOLD, etc.).
- Logo: substituir a frase no header HTML em `app.py` por uma `<img>`.
- Novos indicadores: adicionar linha em `Indicadores` no Excel e referenciá-la em `app.py` via `serie_indicador('Nome')`.

---

## 8. Solução de problemas

| Problema | Solução |
|---|---|
| "ModuleNotFoundError" | Rode `pip install -r requirements.txt` novamente |
| "Arquivo padrão não encontrado" | Confira que `dados/dados_mensais.xlsx` existe |
| Tela em branco após atualizar Excel | Pressione F5 no navegador |
| Cálculo de margem fica "-" | Verifique se a linha "Receita Líquida (base Excel)" está preenchida |

---

*Desenvolvido para a Controladoria Estratégica · DC Distribuidora.*
