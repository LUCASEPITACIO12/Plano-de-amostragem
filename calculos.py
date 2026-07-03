"""
calculos.py
Lógica regulatória – Portaria GM/MS nº 888/2021
Toda a inteligência de cálculo fica aqui, desacoplada da UI e do Excel.
"""
from math import ceil
from dataclasses import dataclass, field
from typing import Optional, ClassVar


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

# ── Mapeamento PSD por desinfetante e pré-oxidação ───────────────────────────
# Base legal: Nota (4) Anexo 9 – Portaria 888/2021:
# "Análise exigida de acordo com o desinfetante utilizado e oxidante
#  utilizado para pré-oxidação."

PSD_POR_DESINFETANTE = {
    "hipoclorito_cloro": [
        "2,4,6 Triclorofenol", "2,4-diclorofenol",
        "Ácidos haloacéticos total", "Clorato", "Clorito", "Cloro residual livre",
    ],
    "isocianuratos": [
        "2,4,6 Triclorofenol", "2,4-diclorofenol",
        "Ácidos haloacéticos total", "Clorato", "Clorito", "Cloro residual livre",
    ],
    "cloraminas": [
        "2,4,6 Triclorofenol", "2,4-diclorofenol",
        "Ácidos haloacéticos total", "Cloraminas Total", "Clorato", "Clorito",
        "Cloro residual livre", "N-nitrosodimetilamina", "Trihalometanos Total",
    ],
    "dioxido_cloro": [
        "Clorato", "Clorito",
    ],
    "ozonio": [
        "2,4,6 Triclorofenol", "2,4-diclorofenol",
        "Ácidos haloacéticos total", "Bromato",
        "Clorato", "Clorito", "Cloro residual livre",
    ],
    "uv_cloro": [
        "2,4,6 Triclorofenol", "2,4-diclorofenol",
        "Ácidos haloacéticos total", "Clorato", "Clorito", "Cloro residual livre",
    ],
}

PSD_PRE_OXIDACAO = {
    "Não realiza pré-oxidação": [],
    "Cloro (pré-cloração)": ["2,4,6 Triclorofenol", "2,4-diclorofenol",
                              "Ácidos haloacéticos total", "Clorato", "Clorito"],
    "Ozônio": ["Bromato"],
    "Dióxido de Cloro": ["Clorato", "Clorito"],
    "Permanganato de Potássio": [],
}

DESINFETANTE_KEYS = {
    "Hipoclorito de Sódio (NaOCl)":      "hipoclorito_cloro",
    "Hipoclorito de Cálcio [Ca(OCl)₂]":  "hipoclorito_cloro",
    "Cloro Gás (Cl₂)":                   "hipoclorito_cloro",
    "Isocianuratos Clorados":            "isocianuratos",
    "Cloraminas (cloraminação)":         "cloraminas",
    "Dióxido de Cloro (ClO₂)":           "dioxido_cloro",
    "Ozônio (O₃)":                       "ozonio",
    "UV + Cloro residual":               "uv_cloro",
}

DESINFETANTE_OPCOES = list(DESINFETANTE_KEYS.keys())
PREOX_OPCOES = list(PSD_PRE_OXIDACAO.keys())


def calc_params_psd(desinfetante: str, oxidante_preox: str) -> list:
    """
    Retorna PSD exigidos conforme desinfetante principal + oxidante de pré-oxidação.
    Base legal: Nota (4) do Anexo 9, Portaria 888/2021.
    """
    chave = DESINFETANTE_KEYS.get(desinfetante, "hipoclorito_cloro")
    params_d = PSD_POR_DESINFETANTE.get(chave, [])
    params_p = PSD_PRE_OXIDACAO.get(oxidante_preox, [])
    todos = set(params_d) | set(params_p)
    return [p for p in PARAMS_PSD if p in todos]

PARAMS_DEMAIS = [
    "1,2 Diclorobenzeno", "1,2 Dicloroetano", "1,4 Diclorobenzeno",
    "2,4 D", "Alacloro",
    "Aldicarbe + Aldicarbesulfona + Aldicarbesulfóxido",
    "Aldrin + Dieldrin",
    "Alumínio", "Ametrina",
    "Amônia (como N)", "Antimônio", "Arsênio",
    "Atrazina + S-Clorotriazinas",
    "Bário", "Benzeno", "Benzo[a]pireno",
    "Cádmio",
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
    "Sulfato",
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
MES_ANUAL = [10]  # outubro – padrão SESAU-AL para coletas anuais

# Dias por mês (ano não bissexto como base)
_DIAS_MES = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class Captacao:
    """Um ponto de captação individual (poço, nascente, rio, açude)."""
    nome: str                    # ex: "Poço PZA-01", "Rio São Francisco"
    tipo: str = "Subterrâneo"    # "Superficial" | "Subterrâneo"
    latitude: str = ""
    longitude: str = ""
    obs: str = ""

    @property
    def is_superficial(self) -> bool:
        return "superficial" in self.tipo.lower()

    @property
    def label_tipo(self) -> str:
        return "Superficial" if self.is_superficial else "Subterrâneo"


@dataclass
class Sistema:
    """Representa um SAA ou SAC com todas as suas características."""

    # ── Identificação ───────────────────────────────────────────────────────
    municipio: str
    nome: str
    localidades: str

    # ── Escopo de responsabilidade ──────────────────────────────────────────
    # "rede"      = somente distribuição (recebe água já tratada; opera só a rede)
    # "cap_trat"  = captação + tratamento (produtor; entrega água tratada e NÃO
    #               opera a rede de distribuição)
    # "completo"  = captação + tratamento + distribuição (opera toda a cadeia)
    escopo: str = "completo"

    # ── Pontos de captação ──────────────────────────────────────────────────
    # Lista de Captacao – cada um com nome e tipo. Se None, __post_init__
    # cria uma genérica baseada em self.manancial.
    captacoes: Optional[list] = None

    # ── Características técnicas ────────────────────────────────────────────
    tipo: str = "SAA"                # SAA | SAC
    manancial: str = "Superficial"   # apenas retrocompatibilidade; a verdade está em `captacoes`
    tratamento: str = "ETA Convencional (Filtração Rápida)"
    n_filtros: int = 0
    populacao: int = 0
    n_ligacoes: int = 0

    # ── Condicionais ────────────────────────────────────────────────────────
    fluoretacao: bool = False
    acrilamida: bool = False
    epicloridrina: bool = False
    rede_pvc: bool = True
    desinfetante: str = "Hipoclorito de Sódio (NaOCl)"
    oxidante_preox: str = "Não realiza pré-oxidação"

    # ── Funcionamento ───────────────────────────────────────────────────────
    horas_funcionamento: float = 24.0   # afeta cálculo de amostras 2h
    nome_eta: str = ""

    # ── Responsabilidade pelo tratamento ────────────────────────────────────
    empresa_responsavel: str = ""
    responsavel_tratamento: str = ""    # operador
    rt_nome: str = ""                   # responsável técnico habilitado
    rt_conselho: str = "CREA"           # CREA | CRQ | CRT | Outro
    rt_registro: str = ""

    # ── Responsabilidade pela distribuição ──────────────────────────────────
    empresa_distribuicao: str = ""
    responsavel_distribuicao: str = ""
    rt_dist_nome: str = ""
    rt_dist_conselho: str = "CREA"
    rt_dist_registro: str = ""

    # ── Geo / Observações ───────────────────────────────────────────────────
    latitude: str = ""
    longitude: str = ""
    obs: str = ""

    # Mapeia escopos antigos (salvos em .json) para o novo modelo de 3 opções.
    # "dist"      → "rede"     (era: somente distribuição)
    # "trat_dist" → "completo" (não tem equivalente direto; assume o escopo mais
    #                           abrangente por segurança regulatória — revisar)
    _ESCOPO_LEGADO: ClassVar[dict] = {"dist": "rede", "trat_dist": "completo"}

    def __post_init__(self):
        """Migra escopos antigos e garante que captacoes seja sempre uma lista."""
        if self.escopo in self._ESCOPO_LEGADO:
            self.escopo = self._ESCOPO_LEGADO[self.escopo]
        if self.captacoes is None:
            tipo_default = (
                "Superficial" if "superficial" in self.manancial.lower()
                else "Subterrâneo"
            )
            self.captacoes = [Captacao(
                nome=f"Captação – {self.nome}",
                tipo=tipo_default,
            )]

    # ── Propriedades derivadas (fonte única de verdade) ─────────────────────
    @property
    def tem_superficial(self) -> bool:
        return any(c.is_superficial for c in self.captacoes)

    @property
    def tem_subterraneo(self) -> bool:
        return any(not c.is_superficial for c in self.captacoes)

    @property
    def is_misto(self) -> bool:
        return self.tem_superficial and self.tem_subterraneo

    @property
    def manancial_efetivo(self) -> str:
        """Manancial derivado das captações cadastradas (fonte única de verdade)."""
        if self.is_misto:
            return "Misto"
        return "Superficial" if self.tem_superficial else "Subterrâneo"


@dataclass
class LinhaPlano:
    """Uma linha do plano de amostragem (ponto × parâmetro × frequência)."""
    etapa: str
    grupo: str
    parametro: str
    ponto_tipo: str
    ponto_desc: str
    frequencia: str
    quantidade: int        # amostras por evento (ou por dia para freq. 2h)
    meses_coleta: list     # lista de 1..12 com os meses de coleta
    base_legal: str
    obs_ponto: str = ""
    horas_dia: float = 24.0  # horas/dia de operação (usado para freq. 2h)

    @property
    def is_operacional(self) -> bool:
        """Parâmetros operacionais: 'A cada 2 horas' ou 'Diário'."""
        return self.frequencia in ("A cada 2 horas", "Diário")

    def _amostras_2h_no_mes(self, mes: int) -> int:
        """Calcula amostras 2h baseado nas horas/dia de operação."""
        if mes not in self.meses_coleta:
            return 0
        dias = _DIAS_MES[mes - 1]
        return int(self.horas_dia / 2) * dias

    def _amostras_diario_no_mes(self, mes: int) -> int:
        if mes not in self.meses_coleta:
            return 0
        return _DIAS_MES[mes - 1]

    @property
    def total_anual(self) -> int:
        if self.frequencia == "A cada 2 horas":
            return sum(self._amostras_2h_no_mes(m) for m in self.meses_coleta)
        if self.frequencia == "Diário":
            return sum(self._amostras_diario_no_mes(m) for m in self.meses_coleta)
        return self.quantidade * len(self.meses_coleta)

    def quantidade_no_mes(self, mes: int) -> int:
        """Retorna quantas amostras coletar num mês específico (1-12)."""
        if self.frequencia == "A cada 2 horas":
            return self._amostras_2h_no_mes(mes)
        if self.frequencia == "Diário":
            return self._amostras_diario_no_mes(mes)
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


def calc_psd(tem_superficial: bool, populacao: int) -> dict:
    """
    Produtos Secundários da Desinfecção (Anexo 13).
    Recebe bool `tem_superficial` (derivado das captações) e a população.
    """
    p = int(populacao or 0)
    if tem_superficial:
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


def freq_coliformes_saida(tem_superficial: bool) -> tuple:
    """
    Retorna (frequência_texto, qtd_mensal).
    Qualquer captação superficial → frequência mais exigente (2×/semana = 8/mês).
    """
    if tem_superficial:
        return "2 vezes por semana", 8
    return "Semanal", 4


# ── Helpers internos para gerar_plano ────────────────────────────────────────

def _linhas_captacao(s: Sistema) -> list[LinhaPlano]:
    """
    Linhas de monitoramento da água bruta, uma sub-lista por ponto de captação.
    Art. 42 §1º (superficial) e §2º (subterrâneo) – Portaria 888/2021.
    """
    linhas: list[LinhaPlano] = []
    nome_sis = f"{s.municipio} – {s.nome}"

    for cap in s.captacoes:
        desc = f"{cap.nome} – {nome_sis}"
        base_art42 = "Art. 42 §1º" if cap.is_superficial else "Art. 42 §2º"
        base_ecoli = "Art. 29" if cap.is_superficial else "Art. 31 §5º"

        # E. coli – mensal em toda captação
        linhas.append(LinhaPlano(
            etapa="Água Bruta – Captação",
            grupo="Físico-Químico e Microbiológico",
            parametro="Escherichia coli",
            ponto_tipo="Captação",
            ponto_desc=desc,
            frequencia="Mensal",
            quantidade=1,
            meses_coleta=list(range(1, 13)),
            base_legal=base_ecoli,
            obs_ponto=cap.tipo,
        ))

        params_comuns = ["Turbidez", "Cor aparente", "pH",
                         "Fósforo Total", "Nitrogênio Amoniacal Total"]
        params_extra = ["DQO", "DBO", "OD"] if cap.is_superficial else ["Condutividade Elétrica"]

        for param in params_comuns + params_extra:
            linhas.append(LinhaPlano(
                etapa="Água Bruta – Captação",
                grupo="Físico-Químico e Microbiológico",
                parametro=param,
                ponto_tipo="Captação",
                ponto_desc=desc,
                frequencia="Semestral",
                quantidade=1,
                meses_coleta=MESES_SEMESTRAL,
                base_legal=base_art42,
                obs_ponto=cap.tipo,
            ))

        linhas.append(LinhaPlano(
            etapa="Água Bruta – Captação",
            grupo="Demais Parâmetros",
            parametro="Inorgânicos, Orgânicos e Agrotóxicos (Anexo 9)",
            ponto_tipo="Captação",
            ponto_desc=desc,
            frequencia="Semestral",
            quantidade=1,
            meses_coleta=MESES_SEMESTRAL,
            base_legal=base_art42,
            obs_ponto=cap.tipo,
        ))

        if cap.is_superficial:
            linhas.append(LinhaPlano(
                etapa="Água Bruta – Captação",
                grupo="Biológico / Cianobactérias",
                parametro="Cianobactérias / Clorofila-a",
                ponto_tipo="Captação",
                ponto_desc=desc,
                frequencia="Trimestral",
                quantidade=1,
                meses_coleta=MESES_TRIMESTRAL,
                base_legal="Art. 43 + Anexo 12",
                obs_ponto="Frequência aumenta para Semanal se > 10.000 cél/mL",
            ))

    return linhas


def _linhas_filtros(s: Sistema) -> list[LinhaPlano]:
    """Linhas de turbidez por unidade filtrante (Anexo 2)."""
    linhas: list[LinhaPlano] = []
    freq_tf = freq_turbidez_filtro(s.tratamento)
    if not freq_tf or s.n_filtros <= 0:
        return linhas

    nome_sis = f"{s.municipio} – {s.nome}"
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
            horas_dia=s.horas_funcionamento,
        ))
    return linhas


def _linhas_saida_tratamento(s: Sistema) -> list[LinhaPlano]:
    """Linhas de monitoramento na saída do tratamento (Anexo 13)."""
    linhas: list[LinhaPlano] = []
    nome_sis = f"{s.municipio} – {s.nome}"
    ponto_saida = f"Saída do Tratamento – {nome_sis}"

    tem_sup = s.tem_superficial
    freq_coli, qtd_coli = freq_coliformes_saida(tem_sup)
    params_psd = calc_params_psd(s.desinfetante, s.oxidante_preox)
    psd = calc_psd(tem_sup, s.populacao)

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
            horas_dia=s.horas_funcionamento,
            base_legal="Anexo 13",
            obs_ponto="Monitoramento operacional",
        ))

    linhas.append(LinhaPlano(
        etapa="Saída do Tratamento",
        grupo="Físico-Químico e Microbiológico",
        parametro="Gosto e Odor",
        ponto_tipo="Saída do Tratamento",
        ponto_desc=ponto_saida,
        frequencia="Trimestral" if tem_sup else "Semestral",
        quantidade=1,
        meses_coleta=MESES_TRIMESTRAL if tem_sup else MESES_SEMESTRAL,
        base_legal="Anexo 13",
    ))

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

    # PSD na saída – apenas parâmetros do desinfetante utilizado.
    #  • Subterrâneo: sempre monitorado na saída do tratamento.
    #  • Superficial: normalmente monitorado na REDE (Ponto de Entrega). Porém, se
    #    a concessão é produtora e NÃO opera a rede (escopo "cap_trat"), o PSD é
    #    monitorado na saída — que é o ponto de entrega da água tratada.
    if not tem_sup or not monitora_rede(s):
        obs_psd = ("Subterrâneo – monitorado na saída" if not tem_sup
                   else "Superficial – monitorado na saída (concessão não opera a rede)")
        for param in params_psd:
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
                obs_ponto=obs_psd,
            ))

    return linhas


def _linhas_rede(s: Sistema) -> list[LinhaPlano]:
    """Linhas de monitoramento na rede de distribuição (SAA)."""
    linhas: list[LinhaPlano] = []
    nome_sis = f"{s.municipio} – {s.nome}"
    n_pts = calc_anexo14(s.populacao)
    tem_sup = s.tem_superficial
    params_psd = calc_params_psd(s.desinfetante, s.oxidante_preox)
    psd = calc_psd(tem_sup, s.populacao)

    ponto01 = f"Ponto 01 – {s.municipio} – {s.nome}"

    # FQ básico em todos os pontos (1 = Ponto de Entrega; demais = Rede)
    for pt in range(1, n_pts + 1):
        ponto_n = f"Ponto {pt:02d} – {s.municipio} – {s.nome}"
        tipo_pt = "Ponto de Entrega" if pt == 1 else "Rede"
        for param in PARAMS_FQ_BASICO:
            linhas.append(LinhaPlano(
                etapa="Rede de Distribuição",
                grupo="Físico-Químico e Microbiológico",
                parametro=param,
                ponto_tipo=tipo_pt,
                ponto_desc=ponto_n,
                frequencia="Mensal",
                quantidade=1,
                meses_coleta=list(range(1, 13)),
                base_legal="Anexo 14 + Anexo 13 (corrig.)",
            ))

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

    if tem_sup:
        ponto_psd = f"{ponto01} – PSD"
        for param in params_psd:
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

    return linhas


def _linhas_sac(s: Sistema) -> list[LinhaPlano]:
    """Linhas de monitoramento de Ponto de Consumo (SAC – Anexo 15)."""
    linhas: list[LinhaPlano] = []
    nome_sis = f"{s.municipio} – {s.nome}"
    n_consumo = ceil(s.populacao / 1000) if s.populacao else 1
    freq_sac = "Semanal" if s.tem_superficial else "Mensal"
    meses_sac = list(range(1, 13))

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


# ── Escopo: fonte única de verdade sobre o que a concessão monitora ──────────
# Três opções:
#   "rede"      → só distribuição (opera apenas a rede)
#   "cap_trat"  → captação + tratamento (produtor; NÃO opera a rede)
#   "completo"  → toda a cadeia (captação + tratamento + rede)

def monitora_captacao(s: Sistema) -> bool:
    return s.escopo in ("cap_trat", "completo")


def monitora_tratamento(s: Sistema) -> bool:
    return s.escopo in ("cap_trat", "completo")


def monitora_rede(s: Sistema) -> bool:
    return s.escopo in ("rede", "completo")


def pontos_rede(s: Sistema) -> int:
    """
    Nº de pontos na rede (Anexo 14). Retorna 0 quando a concessão NÃO opera a
    rede (escopo "cap_trat"), pois nesse caso não há monitoramento de rede.
    """
    return calc_anexo14(s.populacao) if monitora_rede(s) else 0


def gerar_plano(s: Sistema) -> list[LinhaPlano]:
    """
    Gera todas as linhas do plano de amostragem para um sistema.
    Respeita o escopo de responsabilidade da concessão.
    A rede NÃO é mais monitorada incondicionalmente: só entra nos escopos
    "rede" e "completo".
    """
    linhas: list[LinhaPlano] = []

    if monitora_captacao(s):
        linhas.extend(_linhas_captacao(s))
    if monitora_tratamento(s):
        linhas.extend(_linhas_filtros(s))
        linhas.extend(_linhas_saida_tratamento(s))
    if monitora_rede(s):
        if s.tipo == "SAA":
            linhas.extend(_linhas_rede(s))
        else:
            linhas.extend(_linhas_sac(s))

    return linhas


def resumo_sistema(s: Sistema) -> dict:
    """Retorna um dicionário com os totais do sistema para exibição rápida."""
    linhas = gerar_plano(s)
    total_ano = sum(l.total_anual for l in linhas if not l.is_operacional)
    n_pts = pontos_rede(s)
    psd = calc_psd(s.tem_superficial, s.populacao)
    return {
        "n_pontos_rede": n_pts,
        "faixa": faixa_populacional(s.populacao),
        "total_amostras_ano": total_ano,
        "psd_freq": psd["freq"],
        "psd_qtd": psd["qtd"],
        "linhas": linhas,
    }


# ── Validações cruzadas ───────────────────────────────────────────────────────

def validar_sistema(s: Sistema) -> list[str]:
    """
    Roda validações cruzadas e devolve uma lista de mensagens de aviso.
    Lista vazia = tudo ok.
    """
    avisos = []
    t = s.tratamento.lower()

    # Filtros incompatíveis com simples desinfecção
    if "desinfecção" in t and "membrana" not in t and s.n_filtros > 0:
        avisos.append(
            f"Tratamento '{s.tratamento}' não tem unidades filtrantes — "
            f"o campo 'Nº de filtros' ({s.n_filtros}) será ignorado."
        )

    # Filtros esperados mas não informados
    if ("rápida" in t or "lenta" in t or "membrana" in t) and s.n_filtros == 0:
        avisos.append(
            f"Tratamento '{s.tratamento}' normalmente exige unidades filtrantes, "
            f"mas 'Nº de filtros' está em 0."
        )

    # Manancial declarado vs. captações cadastradas
    declarado_sup = "superficial" in s.manancial.lower() or "misto" in s.manancial.lower()
    declarado_sub = "subterrâneo" in s.manancial.lower() or "misto" in s.manancial.lower()
    if declarado_sup and not s.tem_superficial:
        avisos.append(
            "Manancial declarado como 'Superficial' mas não há captações superficiais cadastradas."
        )
    if declarado_sub and not s.tem_subterraneo:
        avisos.append(
            "Manancial declarado como 'Subterrâneo' mas não há captações subterrâneas cadastradas."
        )

    # Pré-oxidação com Ozônio exige Bromato
    if s.oxidante_preox == "Ozônio" and "Bromato" not in calc_params_psd(s.desinfetante, s.oxidante_preox):
        avisos.append("Pré-oxidação com Ozônio exige monitoramento de Bromato (Nota 4, Anexo 9).")

    return avisos
