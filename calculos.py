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
    "Nao realiza pre-oxidacao": [],
    "Cloro (pre-cloracao)": ["2,4,6 Triclorofenol", "2,4-diclorofenol",
                              "Ácidos haloacéticos total", "Clorato", "Clorito"],
    "Ozonio": ["Bromato"],
    "Dioxido de Cloro": ["Clorato", "Clorito"],
    "Permanganato de Potassio": [],
}

DESINFETANTE_KEYS = {
    "Hipoclorito de Sodio (NaOCl)":      "hipoclorito_cloro",
    "Hipoclorito de Calcio [Ca(OCl)2]":  "hipoclorito_cloro",
    "Cloro Gas (Cl2)":                   "hipoclorito_cloro",
    "Isocianuratos Clorados":            "isocianuratos",
    "Cloraminas (cloraminacao)":         "cloraminas",
    "Dioxido de Cloro (ClO2)":           "dioxido_cloro",
    "Ozonio (O3)":                       "ozonio",
    "UV + Cloro residual":               "uv_cloro",
}

DESINFETANTE_OPCOES = list(DESINFETANTE_KEYS.keys())
PREOX_OPCOES = list(PSD_PRE_OXIDACAO.keys())


def calc_params_psd(desinfetante: str, oxidante_preox: str) -> list:
    """
    Retorna PSD exigidos conforme desinfetante principal + oxidante de pre-oxidacao.
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
    # Alfa total e Beta total são monitorados separadamente como
    # Radioatividade – Semestral (Art. 37), não aqui como Trimestral.
    "Alumínio", "Ametrina",
    "Amônia (como N)", "Antimônio", "Arsênio",
    "Atrazina + S-Clorotriazinas",
    "Bário", "Benzeno", "Benzo[a]pireno",
    # Beta total removido – monitorado junto com Alfa total em Radioatividade (Art. 37 / Semestral).
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
    # "Soma das razões de nitrito e nitrato" é critério de cálculo (Art.39),
    # não uma coleta independente – calculado a partir de Nitrato + Nitrito.
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
    # Lista de pontos de captação – cada um com nome, tipo e coordenadas
    captacoes: list = None  # list[Captacao] – preenchida no __post_init__

    escopo: str = "completo"

    tipo: str = "SAA"            # SAA | SAC

    def __post_init__(self):
        """Garante que captacoes seja sempre uma lista, nunca None."""
        if self.captacoes is None:
            # Retrocompatibilidade: se não informou captacoes, cria uma genérica
            self.captacoes = [Captacao(
                nome="Captação – " + self.nome,
                tipo=self.manancial,
            )]

    manancial: str = "Superficial"  # Superficial | Subterrâneo
    tratamento: str = "ETA Convencional (Filtração Rápida)"
    n_filtros: int = 0
    populacao: int = 0
    n_ligacoes: int = 0

    # Condicionais
    fluoretacao: bool = False
    acrilamida: bool = False
    epicloridrina: bool = False
    rede_pvc: bool = True
    # Tipo de desinfetante – define quais parâmetros PSD são obrigatórios (Nota 4, Anexo 9)
    desinfetante: str = "Hipoclorito de Sodio (NaOCl)"
    oxidante_preox: str = "Nao realiza pre-oxidacao"

    # Funcionamento
    horas_funcionamento: float = 24.0  # horas/dia de operação (afeta cálculo de amostras 2h)
    nome_eta: str = ""                 # nome da ETA / unidade de tratamento

    # Responsabilidade
    empresa_responsavel: str = ""      # empresa responsável pelo tratamento
    responsavel_tratamento: str = ""   # pessoa responsável pelo tratamento (operador)
    rt_nome: str = ""                  # responsável técnico habilitado
    rt_conselho: str = "CREA"          # conselho: CREA | CRQ | CRT | Outro
    rt_registro: str = ""              # número de registro no conselho

    # Responsabilidade pela distribuição (quando diferente do tratamento)
    empresa_distribuicao: str = ""
    responsavel_distribuicao: str = ""
    rt_dist_nome: str = ""
    rt_dist_conselho: str = "CREA"
    rt_dist_registro: str = ""

    latitude: str = ""
    longitude: str = ""
    obs: str = ""


# Dias por mês (ano não bissexto como base)
_DIAS_MES = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


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

@dataclass
class Captacao:
    """Um ponto de captação individual (poço, nascente, rio, açude)."""
    nome: str                    # Nome/ID dado pela concessão: ex. "Poço PZA-01", "Rio São Francisco"
    tipo: str = "Subterrâneo"   # "Superficial" | "Subterrâneo"
    latitude: str = ""
    longitude: str = ""
    obs: str = ""

    @property
    def is_superficial(self) -> bool:
        return "superficial" in self.tipo.lower()

    @property
    def label_tipo(self) -> str:
        return "Superficial" if self.is_superficial else "Subterrâneo"




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
    is_sup = "superficial" in manancial.lower() or "misto" in manancial.lower()
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
    """Retorna (frequência_texto, qtd_mensal).
    Misto ou qualquer superficial → frequência mais exigente (2×/semana).
    """
    m = manancial.lower()
    if "superficial" in m or "misto" in m:
        return "2 vezes por semana", 8
    return "Semanal", 4


def gerar_plano(s: Sistema) -> list[LinhaPlano]:
    """
    Gera todas as linhas do plano de amostragem para um sistema.
    Respeita o escopo de responsabilidade da concessão.
    """
    linhas = []
    is_sup = "superficial" in s.manancial.lower() or "misto" in s.manancial.lower()
    is_saa = s.tipo == "SAA"
    n_pts  = calc_anexo14(s.populacao)
    psd    = calc_psd(s.manancial, s.populacao)
    # PSD filtrado pelo desinfetante real do sistema (Nota 4, Anexo 9)
    params_psd = calc_params_psd(s.desinfetante, s.oxidante_preox)

    has_cap  = s.escopo == "completo"
    has_trat = s.escopo in ("completo", "trat_dist")
    # has_dist é sempre True

    nome_sis = f"{s.municipio} – {s.nome}"

    # ── 1. CAPTAÇÃO / ÁGUA BRUTA ─────────────────────────────────────────────
    # Itera sobre cada ponto de captação individualmente.
    # Cada poço ou manancial recebe seu conjunto de parâmetros conforme o tipo.
    # Art. 42 §1º (superficial) e §2º (subterrâneo) – aplicados por ponto.
    if has_cap:
        tem_sup = any(c.is_superficial for c in s.captacoes)
        for cap in s.captacoes:
            desc = f"{cap.nome} – {nome_sis}"
            base_art42 = "Art. 42 §1º" if cap.is_superficial else "Art. 42 §2º"
            base_ecoli  = "Art. 29" if cap.is_superficial else "Art. 31 §5º"

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

            # Parâmetros semestrais comuns a ambos os tipos
            params_comuns = ["Turbidez", "Cor aparente", "pH",
                             "Fósforo Total", "Nitrogênio Amoniacal Total"]

            # Parâmetros específicos por tipo de manancial
            if cap.is_superficial:
                params_extra = ["DQO", "DBO", "OD"]
            else:
                params_extra = ["Condutividade Elétrica"]

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

            # Inorgânicos, Orgânicos e Agrotóxicos – semestral em toda captação
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

            # Cianobactérias / Clorofila-a – somente superficial
            if cap.is_superficial:
                linhas.append(LinhaPlano(
                    etapa="Água Bruta – Captação",
                    grupo="Biológico / Cianobactérias",
                    parametro="Cianobactérias / Clorofila-a",
                    ponto_tipo="Captação",
                    ponto_desc=desc,
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
        # Frequência da saída usa o manancial mais exigente:
        # se qualquer captação for superficial, aplica 2x/semana
        man_saida = "Superficial" if any(c.is_superficial for c in s.captacoes) else "Subterrâneo"
        freq_coli, qtd_coli = freq_coliformes_saida(man_saida)

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

        # PSD na saída (subterrâneo) – apenas parâmetros do desinfetante utilizado
        if not is_sup:
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

        # PSD na rede (superficial) – apenas parâmetros do desinfetante utilizado
        if is_sup:
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
