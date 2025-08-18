# config.py

# Regras de elegibilidade
MIN_FACE_VALUE = 50000  # valor_face mínimo para ser elegível

# Deságio base por tipo de caso
BASE_DISCOUNT = {
    "PRE": 0.35,
    "RPV": 0.25,
}

# Data de corte para cálculo de antiguidade (ano-mês-dia)
SENIORITY_CUTOFF_DATE = "2025-01-01"

# Ajuste por ano completo de antiguidade (em pontos percentuais)
YEARLY_ADJUSTMENT_PP = 0.01  # 1 ponto percentual = 0.01

# Ajuste máximo permitido (limite superior de pontos percentuais)
MAX_ADJUSTMENT_PP = 0.10  # máximo de +10 pontos percentuais = 0.10

# Limites mínimo e máximo para o deságio final
MIN_DISCOUNT = 0.10  # mínimo de 10%
MAX_DISCOUNT = 0.60  # máximo de 60%

# Número de casas decimais para arredondar o valor_compra
DECIMAL_PLACES = 2

# Caminhos padrão para arquivos de entrada e saída
INPUT_CSV_PATH = "../data/casos.csv"
OUTPUT_CSV_PATH = "../out/propostas.csv"
METRICS_JSON_PATH = "../out/metrics.json"
LOG_PATH = "../out/run.log"
