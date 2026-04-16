# Plano de Amostragem 888/2021 – Streamlit App

Ferramenta para geração automatizada do Plano de Amostragem conforme
Portaria GM/MS nº 888/2021, desenvolvida para uso pelas concessões de
abastecimento de água de Alagoas (SESAU-AL).

---

## Como rodar localmente

```bash
# 1. Clonar / baixar os 3 arquivos principais:
#    app.py  |  calculos.py  |  excel_export.py  |  requirements.txt

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Rodar
streamlit run app.py
```

O app abre automaticamente no navegador em [http://localhost:8501](https://plano-amostragem-888.streamlit.app/)

---

## Como publicar no Streamlit Cloud (gratuito)

1. Crie uma conta em https://streamlit.io/cloud
2. Suba os arquivos para um repositório GitHub (público ou privado)
3. Em Streamlit Cloud, clique em **"New app"** e aponte para o repositório
4. Pronto – a SESAU pode distribuir o link para todas as concessões

O link fica fixo (ex: `https://plano888al.streamlit.app`) e qualquer
atualização no código é refletida automaticamente para todos os usuários.

---

## Estrutura dos arquivos

| Arquivo | Função |
|---------|--------|
| `app.py` | Interface Streamlit (telas, formulários, botões) |
| `calculos.py` | Toda a lógica regulatória (Portaria 888/2021) |
| `excel_export.py` | Geração do Excel no formato das concessões |
| `requirements.txt` | Dependências Python |

**A lógica regulatória (`calculos.py`) fica separada da interface.**
Quando a portaria mudar, você atualiza apenas esse arquivo.

---

## Escopos de responsabilidade

A pergunta mais importante do formulário é o **escopo de responsabilidade**
da concessão em cada SAA/SAC:

| Escopo | Captação | ETA/Tratamento | Rede |
|--------|----------|----------------|------|
| Completo | ✅ Monitora | ✅ Monitora | ✅ Monitora |
| Tratamento + Distribuição | ❌ Exige laudos | ✅ Monitora | ✅ Monitora |
| Somente Distribuição | ❌ Exige laudos | ❌ Exige laudos | ✅ Monitora |

---

## Base legal

- Portaria GM/MS nº 888, de 4 de maio de 2021
- Portaria de Consolidação nº 05/2017 – Anexo XX
- Ofício Circular nº E:2/2026/SESAU-AL
- Planilha de Quantitativos Corrigidos SESAU-AL
  (Anexos 2, 13, 14 e 15)
