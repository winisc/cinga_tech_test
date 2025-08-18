import pandas as pd
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from engine.rules import (
    calculate_seniority_years,
    calculate_adjustment,
    clamp_discount,
    generate_discounted_proposals,
    filter_eligibility,
)

class DummyConfig:
    SENIORITY_CUTOFF_DATE = "2025-01-01"
    YEARLY_ADJUSTMENT_PP = 0.01
    BASE_DISCOUNT = {"PRE": 0.35, "RPV": 0.25}
    MIN_DISCOUNT = 0.10
    MAX_DISCOUNT = 0.60
    DECIMAL_PLACES = 2
    MIN_FACE_VALUE = 50000

def test_calculate_seniority_years_correct(protocol_date, cut_date, adjustment_pp, pp_expected):

    protocol_date_formater = pd.to_datetime(protocol_date)
    cut_date_formater = pd.to_datetime(cut_date)

    years = calculate_seniority_years(protocol_date_formater, cut_date_formater)
    pp = calculate_adjustment(years, adjustment_pp)

    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"

    if pp == pp_expected:
        print(f"{GREEN}test_calculate_seniority_years_correct: passed\n{RESET}")
    else:
        print(f"{RED}test_calculate_seniority_years_correct: failed")
        print(f"expected: {pp_expected:.2f}\nobtained: {pp:.2f}\n{RESET}")

def test_base_discount_and_adjustment(df, config, expected_desagios, expected_valores_compra):
    result_df = generate_discounted_proposals(df.copy(), config)

    desagio1 = float(result_df.iloc[0]["desagio_pct"])
    desagio2 = float(result_df.iloc[1]["desagio_pct"])
    buy_value1 = float(result_df.iloc[0]["valor_compra"])
    buy_value2 = float(result_df.iloc[1]["valor_compra"])

    result1 = set(expected_desagios) == set([desagio1, desagio2])
    result2 = set(expected_valores_compra) == set([buy_value1, buy_value2])

    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"

    if result1 and result2:
        print(f"{GREEN}test_base_discount_and_adjustment: passed{RESET}\n")
    else:
        print(f"{RED}test_base_discount_and_adjustment: failed")
        if not result1:
            print(f"deságios:\nexpected: {expected_desagios}\nobtained: {[desagio1, desagio2]}\n")
        if not result2:
            print(f"valores_compra:\nexpected: {expected_valores_compra}\nobtained: {[buy_value1, buy_value2]}{RESET}\n")

def test_purchase_value_rounding(df, config, expected_value):
    result = generate_discounted_proposals(df.copy(), config)

    val_compra = result.iloc[0]["valor_compra"]

    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"

    if val_compra == round(val_compra, 2) and val_compra == expected_value:
        print(f"{GREEN}test_purchase_value_rounding: passed\n{RESET}")
    else:
        print(f"{RED}test_purchase_value_rounding: failed")
        print(f"test1:")
        print(f"expected: {round(val_compra, 2)}\nobtained: {val_compra}\n")
        print(f"test2:")
        print(f"expected: {expected_value}\nobtained: {val_compra}\n{RESET}")

def test_filter_eligibility_cutoff(df, config, ellegiblity, not_ellegiblity):
    filtered = filter_eligibility(df.copy(), config.MIN_FACE_VALUE)

    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"

    if not_ellegiblity not in filtered["numero"].values and ellegiblity in filtered["numero"].values:
        print(f"{GREEN}test_filter_eligibility_cutoff: passed\n{RESET}")
    else:
        print(f"{RED}test_filter_eligibility_cutoff: failed{RESET}")

def test_calculate_clap_limits(gross_discount, min_discount, max_discount, discount_expected):
    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"

    discount_value = gross_discount
    expected1 = discount_expected
    result1 = clamp_discount(discount_value, min_discount, max_discount)
    if result1 == expected1:
        print(f"{GREEN}test_calculate_clap_limits: passed\n{RESET}")
    else:
        print(f"{RED}test_calculate_clap_limits: failed{RESET}")
        print(f"expected: {expected1}\nobtained: {result1}\n")

if __name__ == "__main__":
    start_time = time.perf_counter()
    # Anos completos: confirmar +pp correto
    # Parâmetros:
    # protocol_date = (data do protocolo da proposta)
    # cut_date = (data limite para cálculo de senioridade)
    # adjustment_pp = (percentual anual de ajuste)
    # pp_expected = (valor esperado do ajuste para o pp final)
    test_calculate_seniority_years_correct(
        "2023-04-01",
        DummyConfig.SENIORITY_CUTOFF_DATE,
        DummyConfig.YEARLY_ADJUSTMENT_PP,
        0.01
    )

    test_calculate_seniority_years_correct(
        "2001-01-01",
        DummyConfig.SENIORITY_CUTOFF_DATE,
        DummyConfig.YEARLY_ADJUSTMENT_PP,
        0.10
    )

    # PRE vs RPV: bases (35% vs 25%) com ajuste; verificar deságio final e valor_compra
    # df1 = DataFrame com duas propostas:
    #   - numero: identificação da proposta
    #   - tipo: PRE ou RPV 
    #   - valor_face: valor nominal da proposta
    #   - data_protocolo: data do protocolo da proposta
    # expected_desagios = deságio final esperado após ajustes ex:[0.41, 0.31]
    # expected_valores_compra = valores finais de compra esperados ex:[59000.00, 55200.00]
    df1 = pd.DataFrame({
        "numero": ["0001", "0002"],
        "tipo": ["PRE", "RPV"],
        "valor_face": [100000, 80000],
        "data_protocolo": [pd.Timestamp("2019-01-01"), pd.Timestamp("2019-01-01")],
    })
    test_base_discount_and_adjustment(df1, DummyConfig(), [0.41, 0.31], [59000.00, 55200.00])

    # Arredondamento: valor_compra com 2 casas decimais
    # df2 = DataFrame com uma proposta:
    #   - valor_face: valor com casas decimais extras ex:(72000.567)
    # expected_value = valor esperado arredondado para 2 casas ex:(43200.34)
    df2 = pd.DataFrame({
        "numero": ["0003"],
        "tipo": ["PRE"],
        "valor_face": [72000.567],
        "data_protocolo": [pd.Timestamp("2019-06-10")],
    })
    test_purchase_value_rounding(df2, DummyConfig(), 43200.34)

    # Elegibilidade: filtro pelo valor_face mínimo
    # df3 = DataFrame com duas propostas:
    #   - numero "0004" com valor_face 49999 (abaixo do limite, deve ser excluído)
    #   - numero "0005" com valor_face 50000 (igual ao limite, deve ser incluído)
    # ellegiblity = numero esperado a ser incluído no filtro ("0005")
    # not_ellegiblity = numero esperado a ser excluído ("0004")
    df3 = pd.DataFrame({
        "numero": ["0004", "0005"],
        "tipo": ["PRE", "PRE"],
        "valor_face": [49999, 50000],
        "data_protocolo": [pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-01")],
    })
    test_filter_eligibility_cutoff(df3, DummyConfig, "0005", "0004")

    # Clamp de deságio: verificar limites mínimo e máximo
    # gross_discount = deságio bruto antes do clamp
    # min_discount = deságio mínimo permitido
    # max_discount = deságio máximo permitido
    # discount_expected = deságio esperado após aplicar clamp

    # Teste para deságio acima do máximo permitido (0.70 -> 0.60)
    test_calculate_clap_limits(0.70, 0.10, 0.60, 0.60)

    # Teste para deságio abaixo do mínimo permitido (0.07 -> 0.10)
    test_calculate_clap_limits(0.07, 0.10, 0.60, 0.10)

    # Teste para deságio dentro do limite permitido (0.40 -> 0.40)
    test_calculate_clap_limits(0.40, 0.10, 0.60, 0.40)

    elapsed = time.perf_counter() - start_time
    print(f"({elapsed:.2f}s)\n")

