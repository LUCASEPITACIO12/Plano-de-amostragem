"""
app_revisado.py  –  Plano de Amostragem 888/2021
Execute:  streamlit run app_revisado.py
"""
import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path

from calculos import (
    Sistema, Captacao, gerar_plano, resumo_sistema,
    calc_anexo14, faixa_populacional, MESES,
    DESINFETANTE_OPCOES, PREOX_OPCOES,
)
from excel_export import gerar_excel

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"


def first_existing_asset(*names: str) -> Path | None:
    for name in names:
        p = ASSETS_DIR / name
        if p.exists():
            return p
    return None


def reset_captacoes() -> None:
    st.session_state["captacoes_form"] = [{"nome": "", "tipo": "Subterraneo"}]


# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Plano de Amostragem 888/2021",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS customizado ───────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #f8f9fb; }
[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e8ecf0; }
.etapa-header {
    background: #1f3864;
    color: white;
    padding: 8px 14px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    margin: 18px 0 8px;
}
.aviso-escopo {
    background: #fffbeb;
    border-left: 4px solid #f59e0b;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    font-size: 13px;
    color: #92400e;
    margin-bottom: 1rem;
}
.sidebar-card {
    background: linear-gradient(160deg, #0d2d1f 0%, #1a3a5c 100%);
    border-radius: 14px;
    padding: 16px 14px 10px;
    margin-bottom: 12px;
}
.sidebar-title {
    color: white;
    text-align: center;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: .4px;
    margin-top: 8px;
}
.sidebar-subtitle {
    color: rgba(255,255,255,0.72);
    text-align: center;
    font-size: 11px;
    margin-top: 4px;
}
.sidebar-mini {
    color: rgba(255,255,255,0.55);
    text-align: center;
    font-size: 10px;
    margin-top: 2px;
    margin-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)

# ── Estado da sessão ──────────────────────────────────────────────────────────
if "sistemas" not in st.session_state:
    st.session_state.sistemas = []
if "sistema_editando" not in st.session_state:
    st.session_state.sistema_editando = None
if "captacoes_form" not in st.session_state:
    reset_captacoes()
if "escopo_tmp" not in st.session_state:
    st.session_state["escopo_tmp"] = "completo"

# ── Sidebar – cadastro de sistemas ───────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)

    gvam_logo = first_existing_asset("logo_gvam.png", "logo GVAM - sem o fundo branco.png", "logo.png")
    suvisa_logo = first_existing_asset("logo_suvisa.png", "logo suvisa.png")
    al_logo = first_existing_asset("logo_alagoas.png", "logo alagoas.png")

    if gvam_logo:
        st.image(str(gvam_logo), use_container_width=True)

    col_logo1, col_logo2 = st.columns(2)
    with col_logo1:
        if suvisa_logo:
            st.image(str(suvisa_logo), use_container_width=True)
        else:
            st.caption("SUVISA")
    with col_logo2:
        if al_logo:
            st.image(str(al_logo), use_container_width=True)
        else:
            st.caption("ALAGOAS")

    st.markdown('<div class="sidebar-title">💧 Plano de Amostragem</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">Portaria GM/MS nº 888/2021</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-mini">SESAU-AL · GVAM / SUVISA</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if not gvam_logo and not suvisa_logo and not al_logo:
        st.warning(
            f"Nenhuma logo foi encontrada em {ASSETS_DIR}. Verifique se a pasta assets foi enviada no deploy.",
            icon="⚠️",
        )

    st.subheader("➕ Cadastrar Sistema")

    st.markdown("**Escopo de responsabilidade da concessão**")
    escopo_atual = st.radio(
        "A concessão é responsável por:",
        options=["completo", "trat_dist", "dist"],
        index=["completo", "trat_dist", "dist"].index(st.session_state.get("escopo_tmp", "completo")),
        format_func=lambda x: {
            "completo":  "🔵 Completo – captação + tratamento + distribuição",
            "trat_dist": "🟡 Tratamento + distribuição (recebe água bruta de terceiro)",
            "dist":      "🟠 Somente distribuição (recebe água já tratada)",
        }[x],
        key="escopo_tmp",
        help=(
            "Selecione apenas o escopo sob responsabilidade da concessão. "
            "Etapas de terceiros devem ter seus laudos exigidos contratualmente."
        ),
    )

    if escopo_atual == "dist":
        st.info(
            "A concessão monitora apenas a rede. O responsável pelo tratamento deve fornecer os laudos das etapas anteriores.",
            icon="⚠️",
        )

    if escopo_atual == "completo":
        st.markdown("**Pontos de captação**")
        st.caption("Cadastre cada poço, nascente ou tomada d'água. O plano sai com o nome real de cada ponto.")

        captacoes_form = st.session_state["captacoes_form"]
        for idx_c in range(len(captacoes_form)):
            col_n, col_t, col_del = st.columns([4, 2, 1])
            with col_n:
                captacoes_form[idx_c]["nome"] = st.text_input(
                    f"Nome / ID do ponto {idx_c+1}",
                    value=captacoes_form[idx_c].get("nome", ""),
                    placeholder="Ex: Poço PZA-01 / Rio São Francisco",
                    key=f"cap_nome_{idx_c}",
                )
            with col_t:
                opts = ["Subterraneo", "Superficial"]
                cur = captacoes_form[idx_c].get("tipo", "Subterraneo")
                captacoes_form[idx_c]["tipo"] = st.selectbox(
                    "Tipo",
                    opts,
                    index=opts.index(cur) if cur in opts else 0,
                    key=f"cap_tipo_{idx_c}",
                )
            with col_del:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(
                    "✕",
                    key=f"del_cap_{idx_c}",
                    help="Remover este ponto",
                    disabled=len(captacoes_form) == 1,
                ):
                    st.session_state["captacoes_form"].pop(idx_c)
                    st.rerun()

        col_add, _ = st.columns([2, 4])
        with col_add:
            if st.button("＋ Adicionar ponto de captação", key="add_cap"):
                st.session_state["captacoes_form"].append({"nome": "", "tipo": "Subterraneo"})
                st.rerun()

        n_sup = sum(1 for c in captacoes_form if c.get("tipo") == "Superficial")
        n_sub = sum(1 for c in captacoes_form if c.get("tipo") == "Subterraneo")
        if n_sup > 0 and n_sub > 0:
            st.info(
                f"Sistema misto: {n_sup} ponto(s) superficial(is) + {n_sub} subterrâneo(s). Os parâmetros de cada ponto serão gerados conforme o tipo.",
                icon="ℹ️",
            )
    else:
        reset_captacoes()

    st.divider()
    with st.form("form_sistema", clear_on_submit=True):
        st.caption(f"Escopo selecionado: **{ {'completo':'Completo','trat_dist':'Tratamento + Distribuição','dist':'Somente Distribuição'}[escopo_atual] }**")

        # ── Identificação ────────────────────────────────────────────────────
        st.markdown("**Identificação**")
        municipio = st.text_input("Município *", placeholder="Ex: Batalha")
        nome_sis = st.text_input("Nome do sistema *", placeholder="Ex: SAA Bacia Leiteira")
        localidades = st.text_area("Localidade(s) atendida(s)", placeholder="Urbano, Zona Rural...", height=68)

        # ── Características técnicas ─────────────────────────────────────────
        st.markdown("**Características técnicas**")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            tipo = st.selectbox("Tipo de sistema", ["SAA", "SAC"])
        with col_t2:
            manancial = st.selectbox("Manancial", ["Superficial", "Subterrâneo"])

        if escopo_atual != "dist":
            tratamento = st.selectbox("Tipo de tratamento", [
                "ETA Convencional (Filtração Rápida)",
                "Filtração Lenta",
                "Filtração em Membrana",
                "Simples Desinfecção (Superficial – sem ETA)",
                "Somente Desinfecção (Subterrâneo)",
            ])
            n_filtros = st.number_input("Nº de unidades filtrantes", 0, 30, 0, help="0 = sem filtros / simples desinfecção")
            desinfetante = st.selectbox(
                "Desinfetante principal utilizado",
                DESINFETANTE_OPCOES,
                help=(
                    "Define os Produtos Secundários da Desinfecção (PSD) obrigatórios — Nota (4) do Anexo 9 da Portaria 888/2021. "
                    "Cloraminas: exige THM, Cloraminas Total e N-nitrosodimetilamina. "
                    "Ozônio: exige Bromato. Dióxido de Cloro: exige Clorato e Clorito."
                ),
            )
            realiza_pre_oxidacao = st.checkbox("Realiza pré-oxidação")
            oxidante_preox = st.selectbox(
                "Oxidante utilizado na pré-oxidação",
                PREOX_OPCOES,
                disabled=not realiza_pre_oxidacao,
                help=(
                    "Se o sistema realiza pré-oxidação com ozônio, o Bromato se torna obrigatório mesmo que o desinfetante final seja cloro."
                ),
            ) if realiza_pre_oxidacao else "Nao realiza pre-oxidacao"
        else:
            tratamento = "Informado pelo responsável pelo tratamento"
            n_filtros = 0
            desinfetante = "Hipoclorito de Sodio (NaOCl)"
            oxidante_preox = "Nao realiza pre-oxidacao"
            realiza_pre_oxidacao = False

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            populacao = st.number_input("População atendida (hab.)", 0, 5_000_000, 0, step=100)
        with col_p2:
            n_ligacoes = st.number_input("Nº de ligações ativas", 0, 500_000, 0, step=10)

        captacoes_form = st.session_state.get("captacoes_form", [])

        # ── Condicionais ─────────────────────────────────────────────────────
        if escopo_atual != "dist":
            st.markdown("**Parâmetros condicionais**")
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                fluoretacao = st.checkbox("Realiza fluoretação")
                acrilamida = st.checkbox("Usa polímero c/ acrilamida", value=True)
            with col_c2:
                epicloridrina = st.checkbox("Usa epicloridrina", value=True)
                rede_pvc = st.checkbox("Rede com PVC", value=True)
        else:
            fluoretacao = False
            acrilamida = False
            epicloridrina = False
            rede_pvc = False

        # ── Responsável técnico ──────────────────────────────────────────────
        st.markdown("**Responsável técnico**")
        responsavel = st.text_input("Responsável pelo tratamento", placeholder="Ex: CASAL")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            rt_nome = st.text_input("RT – Nome completo")
        with col_r2:
            rt_reg = st.text_input("RT – Nº registro (CREA/CRQ)")

        col_geo1, col_geo2 = st.columns(2)
        with col_geo1:
            lat = st.text_input("Latitude", placeholder="-9.6740")
        with col_geo2:
            lon = st.text_input("Longitude", placeholder="-37.1315")

        obs = st.text_area("Observações", height=56)

        submitted = st.form_submit_button("✅ Adicionar sistema", use_container_width=True, type="primary")

    if submitted:
        if not municipio or not nome_sis:
            st.error("Preencha pelo menos Município e Nome do sistema.")
        elif populacao == 0:
            st.error("Informe a população atendida para calcular o quantitativo.")
        else:
            s = Sistema(
                municipio=municipio.strip(),
                nome=nome_sis.strip(),
                localidades=localidades.strip(),
                escopo=escopo_atual,
                captacoes=[
                    Captacao(
                        nome=c["nome"] if c["nome"] else f"Captacao {i+1}",
                        tipo=c["tipo"],
                    )
                    for i, c in enumerate(captacoes_form)
                ] if escopo_atual == "completo" and captacoes_form else None,
                tipo=tipo,
                manancial=manancial,
                tratamento=tratamento,
                n_filtros=int(n_filtros),
                populacao=int(populacao),
                n_ligacoes=int(n_ligacoes),
                fluoretacao=fluoretacao,
                acrilamida=acrilamida,
                epicloridrina=epicloridrina,
                rede_pvc=rede_pvc,
                desinfetante=desinfetante,
                oxidante_preox=oxidante_preox,
                responsavel=responsavel,
                rt_nome=rt_nome,
                rt_registro=rt_reg,
                latitude=lat,
                longitude=lon,
                obs=obs,
            )
            st.session_state.sistemas.append(s)
            reset_captacoes()
            st.session_state["escopo_tmp"] = "completo"
            st.success(f"Sistema **{nome_sis}** ({municipio}) adicionado!")
            st.rerun()

    # Lista de sistemas cadastrados
    if st.session_state.sistemas:
        st.divider()
        st.subheader(f"📋 Sistemas ({len(st.session_state.sistemas)})")
        for i, s in enumerate(st.session_state.sistemas):
            col_l, col_r = st.columns([3, 1])
            with col_l:
                st.caption(f"**{s.municipio}** – {s.nome}")
                st.caption(f"Pop.: {s.populacao:,} | {s.manancial} | {s.escopo}")
            with col_r:
                if st.button("🗑️", key=f"del_{i}", help="Remover"):
                    st.session_state.sistemas.pop(i)
                    st.rerun()

        st.divider()
        if st.button("🗑️ Limpar todos", use_container_width=True):
            st.session_state.sistemas = []
            reset_captacoes()
            st.session_state["escopo_tmp"] = "completo"
            st.rerun()

# ── Área principal ────────────────────────────────────────────────────────────
st.title("💧 Plano de Amostragem – Portaria 888/2021")

if not st.session_state.sistemas:
    st.markdown("""
    ### Como usar

    1. **Cadastre os sistemas** no painel à esquerda.
    2. Escolha o **escopo de responsabilidade** da concessão.
    3. Os quantitativos mínimos aparecem automaticamente.
    4. Clique em **Baixar Plano de Amostragem (.xlsx)** para exportar.

    ---
    #### O escopo define quais etapas monitorar:

    | Escopo | Captação | Tratamento | Rede |
    |--------|----------|------------|------|
    | Completo | ✅ | ✅ | ✅ |
    | Tratamento + Distribuição | ❌ | ✅ | ✅ |
    | Somente Distribuição | ❌ | ❌ | ✅ |

    > Quando a concessão recebe **água já tratada**, ela monitora apenas a rede —
    > mas deve exigir contratualmente os laudos das etapas anteriores do fornecedor.
    """)
    st.stop()

# ── Métricas gerais ───────────────────────────────────────────────────────────
sistemas = st.session_state.sistemas
ano = st.selectbox("Ano do plano", [2025, 2026, 2027], index=1, label_visibility="collapsed")

total_pop = sum(s.populacao for s in sistemas)
total_pontos = sum(calc_anexo14(s.populacao) for s in sistemas if s.tipo == "SAA")
total_ano = 0
for s in sistemas:
    linhas = gerar_plano(s)
    total_ano += sum(
        l.total_anual for l in linhas
        if l.frequencia not in ("A cada 2 horas", "Diário")
    )

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Sistemas cadastrados", len(sistemas))
with col2:
    st.metric("População total atendida", f"{total_pop:,.0f}".replace(",", ".") + " hab.")
with col3:
    st.metric("Pontos mínimos na rede", total_pontos, help="Soma dos pontos mínimos de todos os SAA (Anexo 14)")
with col4:
    st.metric(
        "Total amostras/ano (lab.)",
        f"{total_ano:,.0f}".replace(",", "."),
        help="Exclui monitoramentos operacionais (a cada 2h, diário)",
    )

st.divider()

# ── Download Excel ────────────────────────────────────────────────────────────
col_dl, col_info = st.columns([2, 4])
with col_dl:
    excel_bytes = gerar_excel(sistemas, ano)
    st.download_button(
        label="📥 Baixar Plano de Amostragem (.xlsx)",
        data=excel_bytes,
        file_name=f"Plano_Amostragem_{ano}_{'_'.join(s.municipio[:6] for s in sistemas[:3])}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        type="primary",
    )
with col_info:
    st.caption(
        "O Excel contém: **PLANO RESUMIDO** (uma linha por sistema), **Plano - Anual** (uma linha por ponto × parâmetro × frequência) e **TAB Resumo** (totais mensais por sistema)."
    )

st.divider()

# ── Detalhamento por sistema ──────────────────────────────────────────────────
st.subheader("Quantitativo mínimo por sistema")

for s in sistemas:
    res = resumo_sistema(s)
    linhas = res["linhas"]

    escopo_texto = {
        "completo": "🔵 Completo",
        "trat_dist": "🟡 Tratamento + Distribuição",
        "dist": "🟠 Somente Distribuição",
    }.get(s.escopo, s.escopo)

    with st.expander(
        f"**{s.municipio} – {s.nome}** | {s.populacao:,} hab. | {escopo_texto}",
        expanded=(len(sistemas) == 1),
    ):
        if s.escopo == "dist":
            st.markdown(
                '<div class="aviso-escopo">⚠️ Escopo: somente distribuição. O monitoramento de captação e tratamento é responsabilidade do fornecedor da água tratada.</div>',
                unsafe_allow_html=True,
            )

        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Pontos mínimos rede (Anx.14)", res["n_pontos_rede"])
        mc2.metric("Faixa populacional", res["faixa"])
        mc3.metric("Amostras/ano (lab.)", f"{res['total_amostras_ano']:,}")
        mc4.metric("PSD", f"{res['psd_qtd']} ponto(s) / {res['psd_freq']}")

        etapas = list(dict.fromkeys(l.etapa for l in linhas))

        for etapa in etapas:
            lins = [l for l in linhas if l.etapa == etapa]
            st.markdown(f'<div class="etapa-header">{etapa}</div>', unsafe_allow_html=True)

            if etapa == "Saída por Filtro":
                n_f = len(set(l.ponto_desc for l in lins))
                freq_f = lins[0].frequencia if lins else "–"
                st.info(
                    f"**Turbidez** – {freq_f} em cada um dos {n_f} filtros (Anexo 2). Monitoramento operacional – não conta no total de laboratório.",
                    icon="🔬",
                )
                continue

            grupos_vis: dict = {}
            for l in lins:
                key = (l.parametro, l.grupo, l.frequencia, l.quantidade, l.total_anual, l.base_legal)
                if key not in grupos_vis:
                    grupos_vis[key] = l

            rows_table = []
            for (param, grupo, freq, qtd, total, base), l in grupos_vis.items():
                tag_map = {
                    "Físico-Químico e Microbiológico": "🔵 FQ e Microbiológico",
                    "Demais Parâmetros": "🟡 Demais Parâmetros",
                    "Prod. Sec. da Desinfecção": "🟣 PSD",
                    "Acrilamida e Epicloridrina": "🔴 A.E.",
                    "Cloreto de Vinila": "🔴 C.V.",
                    "Biológico / Cianobactérias": "🟢 Bio./Ciano.",
                }
                rows_table.append({
                    "Parâmetro": param,
                    "Grupo": tag_map.get(grupo, grupo),
                    "Frequência": freq,
                    "Qtd/evento": qtd if l.frequencia not in ("A cada 2 horas", "Diário") else "operacional",
                    "Total/ano": total if l.frequencia not in ("A cada 2 horas", "Diário") else None,
                    "Base Legal": base,
                })

            if rows_table:
                df = pd.DataFrame(rows_table)
                st.dataframe(
                    df,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "Total/ano": st.column_config.NumberColumn(format="%d"),
                    },
                )

# ── Rodapé ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Portaria GM/MS nº 888/2021 | Portaria de Consolidação nº 05/2017 (Anexo XX) | "
    f"Ofício Circular E:2/2026/SESAU-AL – Gerado em {date.today().strftime('%d/%m/%Y')}"
)
