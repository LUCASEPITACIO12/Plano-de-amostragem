Plano de Amostragem 888/2021 – Streamlit App
Ferramenta para geração automatizada do Plano de Amostragem conforme
Portaria GM/MS nº 888/2021, desenvolvida para uso pelas concessões de
abastecimento de água de Alagoas (SESAU-AL).
---
Como rodar localmente
```bash
# 1. Baixar os arquivos do projeto:
#    app.py  |  calculos.py  |  excel\_export.py
#    test\_calculos.py  |  requirements.txt
#    (opcional) assets/capa.png

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Rodar
streamlit run app.py
```
O app abre automaticamente no navegador em http://localhost:8501
---
Como publicar no Streamlit Cloud (gratuito)
Crie uma conta em https://streamlit.io/cloud
Suba os arquivos para um repositório GitHub (público ou privado)
Em Streamlit Cloud, clique em "New app" e aponte para o repositório
Pronto – a SESAU pode distribuir o link para todas as concessões
O link fica fixo (ex: `https://plano888al.streamlit.app`) e qualquer
atualização no código é refletida automaticamente para todos os usuários.
---
Estrutura dos arquivos
Arquivo	Função
`app.py`	Interface Streamlit (telas, formulários, botões, save/load)
`calculos.py`	Toda a lógica regulatória (Portaria 888/2021)
`excel\_export.py`	Geração do Excel no formato das concessões
`test\_calculos.py`	Testes automatizados (pytest) da lógica regulatória
`requirements.txt`	Dependências Python
`assets/capa.png`	(Opcional) banner exibido no topo do app
A lógica regulatória (`calculos.py`) fica separada da interface.
Quando a portaria mudar, você atualiza apenas esse arquivo — e roda os
testes para confirmar que nada quebrou.
---
Rodando os testes
```bash
pip install pytest
python -m pytest test\_calculos.py -v
```
Os testes cobrem: faixas populacionais do Anexo 14, PSD por desinfetante
e pré-oxidação (cloraminas exigem NDMA/THM, ozônio exige Bromato),
captações superficiais vs. subterrâneas, os três escopos de
responsabilidade, validações cruzadas e a geração do Excel.
---
Salvar e carregar planos
Na barra lateral, em "💾 Salvar / Carregar plano":
Baixar plano (.json) — exporta todos os sistemas cadastrados para um
arquivo, que pode ser guardado ou compartilhado.
Carregar plano (.json) — restaura um plano salvo anteriormente,
recriando todos os sistemas e seus pontos de captação.
Útil para retomar o trabalho de um dia para o outro sem recadastrar tudo.
---
Escopos de responsabilidade
A pergunta mais importante do formulário é o escopo de responsabilidade
da concessão em cada SAA/SAC:
Escopo	Captação	ETA/Tratamento	Rede
Completo	✅ Monitora	✅ Monitora	✅ Monitora
Tratamento + Distribuição	❌ Exige laudos	✅ Monitora	✅ Monitora
Somente Distribuição	❌ Exige laudos	❌ Exige laudos	✅ Monitora
---
O que o Excel gerado contém
Aba	Conteúdo
PLANO RESUMIDO	Uma linha por sistema, com totais mensais e anuais
Plano - Anual	Uma linha por ponto × parâmetro × frequência
TAB Resumo	Totais mensais por sistema + total geral
Memória de Cálculo	Como cada número foi obtido (auditoria SESAU)
Ref. Anexo 14	Tabela de referência das faixas populacionais
---
Base legal
Portaria GM/MS nº 888, de 4 de maio de 2021
Portaria de Consolidação nº 05/2017 – Anexo XX
Ofício Circular nº E:2/2026/SESAU-AL
Planilha de Quantitativos Corrigidos SESAU-AL
(Anexos 2, 9, 12, 13, 14 e 15)
