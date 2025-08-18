import pandas as pd

def calculate_seniority_years(protocol_date, cut_time_date):
    diff = cut_time_date - protocol_date
    if diff < pd.Timedelta(0):
        raise ValueError(f"Data corte inválida identificada")
    years = diff.days // 365
    return years

def calculate_adjustment(years_completed, yearly_adjustment_pp):
    limited_years = min(years_completed, 10)
    return round(limited_years * yearly_adjustment_pp, 2)

def map_base_discount(case_type, base_discount_map):
    base = base_discount_map.get(case_type)
    if base is None:
        raise ValueError(
            f"Tipo inválido encontrado: {case_type}. "
            f"Tipos válidos: {list(base_discount_map.keys())}"
        )
    return base

def clamp_discount(discount_value, min_discount, max_discount):
    upper_limited = min(discount_value, max_discount)
    clamped_value = max(min_discount, upper_limited)
    return clamped_value

def generate_discounted_proposals(df, config):
    cut_time_date = pd.to_datetime(config.SENIORITY_CUTOFF_DATE)

    df["anos_completos"] = df["data_protocolo"].apply(
        lambda date: calculate_seniority_years(date, cut_time_date)
    )

    df["ajuste_pp"] = df["anos_completos"].apply(
        lambda years: calculate_adjustment(years, config.YEARLY_ADJUSTMENT_PP)
    )

    df["desagio_base"] = df["tipo"].apply(
        lambda type: map_base_discount(type, config.BASE_DISCOUNT)
    )

    df["desagio_bruto"] = df["desagio_base"] + df["ajuste_pp"]

    df["desagio_pct"] = df["desagio_bruto"].apply(
        lambda pct: round(
            clamp_discount(pct, config.MIN_DISCOUNT, config.MAX_DISCOUNT),
            config.DECIMAL_PLACES
        )
    )

    df["valor_compra"] = (df["valor_face"] * (1 - df["desagio_pct"])).round(config.DECIMAL_PLACES)

    df["numero"] = df["numero"].str.zfill(4)

    return df[["numero", "desagio_pct", "valor_compra"]]

def filter_eligibility(df, min_face_value):
    return df[df["valor_face"] >= min_face_value].copy()
