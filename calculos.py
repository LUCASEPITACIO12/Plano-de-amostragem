"""
calculos.py
Lógica regulatória – Portaria GM/MS nº 888/2021
Toda a inteligência de cálculo fica aqui, desacoplada da UI e do Excel.
"""
from math import ceil
from dataclasses import dataclass, field
from typing import Optional


# ── Constantes regulatórias ───────────────────────────────────────────────────

PARAMS_FQ_BASICO = [
    "Cloro residual livre",
    "Coliformes totais",
    "Escherichia coli",
    "Cor aparente",
    "pH",
    "Turbidez",
]

PARAMS_PSD = [
    "2,4,6 Triclorofenol",
    "2,4-diclorofenol",
    "Ácidos haloacéticos total",
    "Bromato",
    "Cloraminas Total",
    "Clorato",
    "Clorito",
    "Cloro residual livre",
    "N-nitrosodimetilamina",
    "Trihalometanos Total",
]

PARAMS_DEMAIS = [
    "1,2 Diclorobenzeno", "1,2 Dicloroetano", "1,4 Diclorobenzeno",
    "2,4 D", "Alacloro",
    "Aldicarbe + Aldicarbesulfona + Aldicarbesulfóxido",
    "Aldrin + Dieldrin", "Alfa total", "Alumínio", "Ametrina",
    "Amônia (como N)", "Antimônio", "Arsênio",
    "Atrazina + S-Clorotriazinas",
    "Bário", "Benzeno", "Benzo[a]pireno", "Beta total", "Cádmio",
    "Carbendazim", "Carbofurano", "Chumbo", "Ciproconazol", "Clordano",
    "Cloreto", "Clorotalonil", "Clorpirifós + clorpirifós-oxon",
    "Cobre", "Cromo", "DDT+DDD+DDE", "Di(2-etilhexil) ftalato",
    "Diclorometano", "Difenoconazol", "Dimetoato + ometoato", "Dioxano",
    "Diuron", "Dureza total", "Epoxiconazol", "Etilbenzeno", "Ferro",
    "Fipronil", "Fluoreto", "Flutriafol", "Glifosato + AMPA",
    "Hidroxi-Atrazina", "Lindano (gama HCH)", "Malationa",
    "Mancozebe + ETU", "Manganês", "Mercúrio Total",
    "Metamidofós + Acefato", "Metolacloro", "Metribuzim", "Molinato",
    "Monoclorobenzeno", "Níquel", "Nitrato (como N)", "Nitrito (como N)",
    "Paraquate", "Pentaclorofenol", "Picloram", "Profenofós",
    "Propargito", "Protioconazol + Protioconazol-Destio", "Selênio",
    "Simazina", "Sódio", "Sólidos dissolvidos totais",
    "Soma das razões de nitrito e nitrato", "Sulfato",
    "Sulfeto de hidrogênio", "Tebuconazol", "Terbufós",
    "Tetracloreto de Carbono", "Tetracloroeteno", "Tiametoxam",
    "Tiodicarbe", "Tiram", "Tolueno", "Tricloroeteno", "Trifluralina",
    "Urânio", "Xilenos", "Zinco",
]

MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]

MESES_BIMESTRAL = [1, 3, 5, 7, 9, 11]
MESES_TRIMESTRAL = [1, 4, 7, 10]
MESES_SEMESTRAL = [1, 7]
MES_ANUAL = [10]


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class Sistema:
    """Representa um SAA ou SAC com todas as suas características."""
    municipio: str
    nome: str
    localidades: str

    # Escopo de responsabilidade
    # "completo"  = captação + tratamento + distribuição
    # "trat_dist" = tratamento + distribuição (recebe água bruta de terceiro)
    # "dist"      = somente distribuição (recebe água já tratada)
    escopo: str = "completo"

    tipo: str = "SAA"            # SAA | SAC
    manancial: str = "Superficial"  # Superficial | Subterrâneo
    tratamento: str = "ETA Convencional (Filtração Rápida)"
    n_filtros: int = 0
    populacao: int = 0
    n_ligacoes: int = 0

    # Condicionais
    fluoretacao: bool = False
    pre_oxidacao: bool = False
    acrilamida: bool = False
    epicloridrina: bool = False
    rede_pvc: bool = True

    # Identificação
    responsavel: str = ""
    rt_nome: str = ""
    rt_registro: str = ""
    latitude: str = ""
    longitude: str = ""
    obs: str = ""


@dataclass
class LinhaPlano:
    """Uma linha do plano de amostragem (ponto × parâmetro × frequência)."""
    etapa: str          # Captação / Saída Filtro / Saída Tratamento / Rede
    grupo: str          # Físico-Químico e Microbiológico / Demais Parâmetros / …
    parametro: str
    ponto_tipo: str     # Rede / Ponto de Entrega / Reservatório / Captação
    ponto_desc: str     # descrição do ponto
    frequencia: str     # Mensal / Bimestral / …
    quantidade: int     # amostras por evento de frequência
    meses_coleta: list  # lista de 1..12 com os meses de coleta
    base_legal: str
    obs_ponto: str = ""

    @property
    def total_anual(self) -> int:
        return self.quantidade * len(self.meses_coleta)

    def quantidade_no_mes(self, mes: int) -> int:
        """Retorna quantas amostras coletar num mês específico (1-12)."""
        return self.quantidade if mes in self.meses_coleta else 0


# ── Funções de cálculo ────────────────────────────────────────────────────────

def calc_anexo14(populacao: int) -> int:
    """
    Nº mínimo de amostras mensais de coliformes na rede (Anexo 14).
    11 faixas populacionais, máximo 400.
    """
    p = max(0, int(populacao or 0))
    if p < 5_000:       return 5
    if p < 10_000:      return 10
    if p <= 50_000:     return ceil(p / 1_000)
    if p <= 80_000:     return 25 + ceil(p / 2_000)
    if p <= 130_000:    return 1 + ceil(p / 1_250)
    if p <= 250_000:    return 40 + ceil(p / 2_000)
    if p <= 340_000:    return 115 + ceil(p / 5_000)
    if p <= 400_000:    return 47 + ceil(p / 2_500)
    if p <= 600_000:    return 127 + ceil(p / 5_000)
    if p <= 1_140_000:  return 187 + ceil(p / 10_000)
    return min(400, 244 + ceil(p / 20_000))


def faixa_populacional(populacao: int) -> str:
    p = max(0, int(populacao or 0))
    if p < 5_000:       return "< 5.000 hab."
    if p < 10_000:      return "5.000 a 10.000 hab."
    if p <= 50_000:     return "10.000 a 50.000 hab."
    if p <= 80_000:     return "50.000 a 80.000 hab."
    if p <= 130_000:    return "80.000 a 130.000 hab."
    if p <= 250_000:    return "130.000 a 250.000 hab."
    if p <= 340_000:    return "250.000 a 340.000 hab."
    if p <= 400_000:    return "340.000 a 400.000 hab."
    if p <= 600_000:    return "400.000 a 600.000 hab."
    if p <= 1_140_000:  return "600.000 a 1.140.000 hab."
    return "> 1.140.000 hab. (máx. 400 amostras)"


def calc_psd(manancial: str, populacao: int) -> dict:
    """
    Produtos Secundários da Desinfecção (Anexo 13).
    Retorna qtd por evento e lista de meses de coleta.
    """
    p = int(populacao or 0)
    is_sup = "superficial" in manancial.lower()
    if is_sup:
        if p < 50_000:   return {"qtd": 1, "freq": "Bimestral", "meses": MESES_BIMESTRAL}
        if p <= 250_000: return {"qtd": 4, "freq": "Bimestral", "meses": MESES_BIMESTRAL}
        return               {"qtd": 8, "freq": "Bimestral", "meses": MESES_BIMESTRAL}
    else:
        if p < 50_000:   return {"qtd": 1, "freq": "Anual",     "meses": MES_ANUAL}
        if p <= 250_000: return {"qtd": 2, "freq": "Semestral", "meses": MESES_SEMESTRAL}
        return               {"qtd": 3, "freq": "Semestral", "meses": MESES_SEMESTRAL}


def freq_turbidez_filtro(tratamento: str) -> Optional[str]:
    t = tratamento.lower()
    if "rápida" in t or "membrana" in t:
        return "A cada 2 horas"
    if "lenta" in t:
        return "Diária"
    return None


def freq_coliformes_saida(manancial: str) -> tuple:
    """Retorna (frequência_texto, qtd_mensal)."""
    if "superficial" in manancial.lower():
        return "2 vezes por semana", 8
    return "Semanal", 4


def gerar_plano(s: Sistema) -> list[LinhaPlano]:
    """
    Gera todas as linhas do plano de amostragem para um sistema.
    Respeita o escopo de responsabilidade da concessão.
    """
    linhas = []
    is_sup = "superficial" in s.manancial.lower()
    is_saa = s.tipo == "SAA"
    n_pts  = calc_anexo14(s.populacao)
    psd    = calc_psd(s.manancial, s.populacao)

    has_cap  = s.escopo == "completo"
    has_trat = s.escopo in ("completo", "trat_dist")
    # has_dist é sempre True

    nome_sis = f"{s.municipio} – {s.nome}"

    # ── 1. CAPTAÇÃO / ÁGUA BRUTA ─────────────────────────────────────────────
    if has_cap:
        ponto_cap = f"Captação – {nome_sis}"

        linhas.append(LinhaPlano(
            etapa="Água Bruta – Captação",
            grupo="Físico-Químico e Microbiológico",
            parametro="Escherichia coli",
            ponto_tipo="Captação",
            ponto_desc=ponto_cap,
            frequencia="Mensal",
            quantidade=1,
            meses_coleta=list(range(1, 13)),
            base_legal="Art. 29 / Art. 31 §5º",
            obs_ponto="1 amostra/mês por ponto de captação",
        ))

        params_bruta_fq = ["Turbidez", "Cor aparente", "pH",
                           "Fósforo Total", "Nitrogênio Amoniacal Total"]
        if is_sup:
            params_bruta_fq += ["DQO", "DBO", "OD"]
        else:
            params_bruta_fq += ["Condutividade Elétrica"]

        for param in params_bruta_fq:
            linhas.append(LinhaPlano(
                etapa="Água Bruta – Captação",
                grupo="Físico-Químico e Microbiológico",
                parametro=param,
                ponto_tipo="Captação",
                ponto_desc=ponto_cap,
                frequencia="Semestral",
                quantidade=1,
                meses_coleta=MESES_SEMESTRAL,
                base_legal="Art. 42 §1º" if is_sup else "Art. 42 §2º",
            ))

        linhas.append(LinhaPlano(
            etapa="Água Bruta – Captação",
            grupo="Demais Parâmetros",
            parametro="Inorgânicos, Orgânicos e Agrotóxicos (Anexo 9)",
            ponto_tipo="Captação",
            ponto_desc=ponto_cap,
            frequencia="Semestral",
            quantidade=1,
            meses_coleta=MESES_SEMESTRAL,
            base_legal="Art. 42 §1º / §2º",
        ))

        if is_sup:
            linhas.append(LinhaPlano(
                etapa="Água Bruta – Captação",
                grupo="Biológico / Cianobactérias",
                parametro="Cianobactérias / Clorofila-a",
                ponto_tipo="Captação",
                ponto_desc=ponto_cap,
                frequencia="Trimestral (→ Semanal se > 10.000 cél/mL)",
                quantidade=1,
                meses_coleta=MESES_TRIMESTRAL,
                base_legal="Art. 43 + Anexo 12",
                obs_ponto="Frequência aumenta conforme resultado",
            ))

    # ── 2. SAÍDA POR FILTRO ───────────────────────────────────────────────────
    if has_trat and s.n_filtros > 0:
        freq_tf = freq_turbidez_filtro(s.tratamento)
        if freq_tf:
            for i in range(1, s.n_filtros + 1):
                linhas.append(LinhaPlano(
                    etapa="Saída por Filtro",
                    grupo="Físico-Químico e Microbiológico",
                    parametro="Turbidez",
                    ponto_tipo="Saída do Tratamento",
                    ponto_desc=f"Filtro {i:02d} – {nome_sis}",
                    frequencia=freq_tf,
                    quantidade=1,
                    meses_coleta=list(range(1, 13)),
                    base_legal="Anexo 2",
                    obs_ponto="Efluente individual de cada unidade filtrante",
                ))

    # ── 3. SAÍDA DO TRATAMENTO ────────────────────────────────────────────────
    if has_trat:
        ponto_saida = f"Saída do Tratamento – {nome_sis}"
        freq_coli, qtd_coli = freq_coliformes_saida(s.manancial)

        for param in ["Coliformes totais", "Escherichia coli"]:
            linhas.append(LinhaPlano(
                etapa="Saída do Tratamento",
                grupo="Físico-Químico e Microbiológico",
                parametro=param,
                ponto_tipo="Saída do Tratamento",
                ponto_desc=ponto_saida,
                frequencia=freq_coli,
                quantidade=qtd_coli,
                meses_coleta=list(range(1, 13)),
                base_legal="Anexo 14",
                obs_ponto="Por unidade de tratamento",
            ))

        params_saida_fq = ["Turbidez", "Cor aparente", "pH", "Cloro residual livre"]
        if s.fluoretacao:
            params_saida_fq.append("Fluoreto")

        for param in params_saida_fq:
            linhas.append(LinhaPlano(
                etapa="Saída do Tratamento",
                grupo="Físico-Químico e Microbiológico",
                parametro=param,
                ponto_tipo="Saída do Tratamento",
                ponto_desc=ponto_saida,
                frequencia="A cada 2 horas",
                quantidade=1,
                meses_coleta=list(range(1, 13)),
                base_legal="Anexo 13",
                obs_ponto="Monitoramento operacional",
            ))

        linhas.append(LinhaPlano(
            etapa="Saída do Tratamento",
            grupo="Físico-Químico e Microbiológico",
            parametro="Gosto e Odor",
            ponto_tipo="Saída do Tratamento",
            ponto_desc=ponto_saida,
            frequencia="Trimestral" if is_sup else "Semestral",
            quantidade=1,
            meses_coleta=MESES_TRIMESTRAL if is_sup else MESES_SEMESTRAL,
            base_legal="Anexo 13",
        ))

        # Condicionais saída
        if s.acrilamida:
            linhas.append(LinhaPlano(
                etapa="Saída do Tratamento",
                grupo="Acrilamida e Epicloridrina",
                parametro="Acrilamida",
                ponto_tipo="Saída do Tratamento",
                ponto_desc=ponto_saida,
                frequencia="Mensal",
                quantidade=1,
                meses_coleta=list(range(1, 13)),
                base_legal="Anexo 13",
                obs_ponto="Somente durante uso do polímero",
            ))
        if s.epicloridrina:
            linhas.append(LinhaPlano(
                etapa="Saída do Tratamento",
                grupo="Acrilamida e Epicloridrina",
                parametro="Epicloridrina",
                ponto_tipo="Saída do Tratamento",
                ponto_desc=ponto_saida,
                frequencia="Mensal",
                quantidade=1,
                meses_coleta=list(range(1, 13)),
                base_legal="Anexo 13",
            ))

        linhas.append(LinhaPlano(
            etapa="Saída do Tratamento",
            grupo="Cloreto de Vinila",
            parametro="Cloreto de Vinila",
            ponto_tipo="Saída do Tratamento",
            ponto_desc=ponto_saida,
            frequencia="Semestral",
            quantidade=1,
            meses_coleta=MESES_SEMESTRAL,
            base_legal="Anexo 13",
        ))

        linhas.append(LinhaPlano(
            etapa="Saída do Tratamento",
            grupo="Demais Parâmetros",
            parametro="Demais Parâmetros (incl. E. coli, inorg., org., agrotóx.)",
            ponto_tipo="Saída do Tratamento",
            ponto_desc=ponto_saida,
            frequencia="Semestral",
            quantidade=1,
            meses_coleta=MESES_SEMESTRAL,
            base_legal="Anexo 13",
        ))

        # PSD na saída (subterrâneo)
        if not is_sup:
            for param in PARAMS_PSD:
                linhas.append(LinhaPlano(
                    etapa="Saída do Tratamento",
                    grupo="Prod. Sec. da Desinfecção",
                    parametro=param,
                    ponto_tipo="Saída do Tratamento",
                    ponto_desc=ponto_saida,
                    frequencia=psd["freq"],
                    quantidade=psd["qtd"],
                    meses_coleta=psd["meses"],
                    base_legal="Anexo 13",
                    obs_ponto="Subterrâneo – monitorado na saída",
                ))

    # ── 4. REDE DE DISTRIBUIÇÃO ───────────────────────────────────────────────
    if is_saa:
        # Ponto 01 = ponto de entrega / reservatório (FQ mensal)
        ponto01 = f"Ponto 01 – {s.municipio} – {s.nome}"

        for param in PARAMS_FQ_BASICO:
            linhas.append(LinhaPlano(
                etapa="Rede de Distribuição",
                grupo="Físico-Químico e Microbiológico",
                parametro=param,
                ponto_tipo="Ponto de Entrega",
                ponto_desc=ponto01,
                frequencia="Mensal",
                quantidade=1,
                meses_coleta=list(range(1, 13)),
                base_legal="Anexo 14 + Anexo 13 (corrig.)",
            ))

        # Pontos 02 a N (mínimo regulatório)
        for pt in range(2, n_pts + 1):
            ponto_n = f"Ponto {pt:02d} – {s.municipio} – {s.nome}"
            for param in PARAMS_FQ_BASICO:
                linhas.append(LinhaPlano(
                    etapa="Rede de Distribuição",
                    grupo="Físico-Químico e Microbiológico",
                    parametro=param,
                    ponto_tipo="Rede",
                    ponto_desc=ponto_n,
                    frequencia="Mensal",
                    quantidade=1,
                    meses_coleta=list(range(1, 13)),
                    base_legal="Anexo 14 + Anexo 13 (corrig.)",
                ))

        # PVC – Cloreto de Vinila na rede
        if s.rede_pvc:
            linhas.append(LinhaPlano(
                etapa="Rede de Distribuição",
                grupo="Cloreto de Vinila",
                parametro="Cloreto de Vinila",
                ponto_tipo="Ponto de Entrega",
                ponto_desc=f"{ponto01} – C.V.",
                frequencia="Semestral",
                quantidade=1,
                meses_coleta=MESES_SEMESTRAL,
                base_legal="Anexo 13",
                obs_ponto="Rede PVC – monitorar mesmo sem detecção na saída",
            ))

        # PSD na rede (superficial)
        if is_sup:
            ponto_psd = f"{ponto01} – PSD"
            for param in PARAMS_PSD:
                linhas.append(LinhaPlano(
                    etapa="Rede de Distribuição",
                    grupo="Prod. Sec. da Desinfecção",
                    parametro=param,
                    ponto_tipo="Ponto de Entrega",
                    ponto_desc=ponto_psd,
                    frequencia=psd["freq"],
                    quantidade=psd["qtd"],
                    meses_coleta=psd["meses"],
                    base_legal="Anexo 13",
                ))

        # Acrilamida / Epicloridrina na rede
        if s.acrilamida or s.epicloridrina:
            ponto_ae = f"{ponto01} – A.E."
            for param, flag in [("Acrilamida", s.acrilamida),
                                 ("Epicloridrina", s.epicloridrina)]:
                if flag:
                    linhas.append(LinhaPlano(
                        etapa="Rede de Distribuição",
                        grupo="Acrilamida e Epicloridrina",
                        parametro=param,
                        ponto_tipo="Ponto de Entrega",
                        ponto_desc=ponto_ae,
                        frequencia="Semestral",
                        quantidade=1,
                        meses_coleta=MESES_SEMESTRAL,
                        base_legal="Anexo 13",
                        obs_ponto="Dispensado se não detectado na saída",
                    ))

        # Demais Parâmetros na rede (1 ponto estratégico, trimestral)
        ponto_dp = f"{ponto01} – D.P."
        for param in PARAMS_DEMAIS:
            linhas.append(LinhaPlano(
                etapa="Rede de Distribuição",
                grupo="Demais Parâmetros",
                parametro=param,
                ponto_tipo="Ponto de Entrega",
                ponto_desc=ponto_dp,
                frequencia="Trimestral",
                quantidade=1,
                meses_coleta=MESES_TRIMESTRAL,
                base_legal="Anexo 13",
            ))

        # Radioatividade
        linhas.append(LinhaPlano(
            etapa="Rede de Distribuição",
            grupo="Demais Parâmetros",
            parametro="Radioatividade – Alfa total / Beta total",
            ponto_tipo="Rede",
            ponto_desc=f"Ponto estratégico – {nome_sis}",
            frequencia="Semestral",
            quantidade=1,
            meses_coleta=MESES_SEMESTRAL,
            base_legal="Art. 37",
        ))

    else:
        # SAC – Ponto de Consumo (Anexo 15)
        n_consumo = ceil(s.populacao / 1000) if s.populacao else 1
        freq_sac = "Semanal" if is_sup else "Mensal"
        meses_sac = list(range(1, 13))  # sempre todos os meses

        for param in ["Cor aparente", "pH", "Coliformes totais",
                      "Escherichia coli", "Turbidez"]:
            linhas.append(LinhaPlano(
                etapa="Ponto de Consumo (SAC)",
                grupo="Físico-Químico e Microbiológico",
                parametro=param,
                ponto_tipo="Ponto de Consumo",
                ponto_desc=f"Ponto de Consumo – {nome_sis}",
                frequencia=freq_sac,
                quantidade=n_consumo,
                meses_coleta=meses_sac,
                base_legal="Anexo 15",
                obs_ponto=f"{n_consumo} amostras (1/1.000 hab.)",
            ))
        linhas.append(LinhaPlano(
            etapa="Ponto de Consumo (SAC)",
            grupo="Físico-Químico e Microbiológico",
            parametro="Residual de Desinfetante",
            ponto_tipo="Ponto de Consumo",
            ponto_desc=f"Ponto de Consumo – {nome_sis}",
            frequencia="Diário",
            quantidade=n_consumo,
            meses_coleta=meses_sac,
            base_legal="Anexo 15",
        ))
        linhas.append(LinhaPlano(
            etapa="Ponto de Consumo (SAC)",
            grupo="Demais Parâmetros",
            parametro="Demais Parâmetros",
            ponto_tipo="Ponto de Consumo",
            ponto_desc=f"Ponto de Consumo – {nome_sis}",
            frequencia="Semestral",
            quantidade=1,
            meses_coleta=MESES_SEMESTRAL,
            base_legal="Anexo 15",
        ))

    return linhas


def resumo_sistema(s: Sistema) -> dict:
    """Retorna um dicionário com os totais do sistema para exibição rápida."""
    linhas = gerar_plano(s)
    total_ano = sum(l.total_anual for l in linhas
                    if l.frequencia not in ("A cada 2 horas", "Diário"))
    n_pts = calc_anexo14(s.populacao)
    psd = calc_psd(s.manancial, s.populacao)
    return {
        "n_pontos_rede": n_pts,
        "faixa": faixa_populacional(s.populacao),
        "total_amostras_ano": total_ano,
        "psd_freq": psd["freq"],
        "psd_qtd": psd["qtd"],
        "linhas": linhas,
    }
