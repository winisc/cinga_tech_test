import pandas as pd

def validate_and_treat_df(df):
    if df.isnull().values.any():
        missing_indices = df[df.isnull().any(axis=1)].index.tolist()
        raise ValueError(f"DataFrame contém dados faltantes na linha de índice: {missing_indices}")

    duplicated = df['numero'].duplicated()
    if duplicated.any():
        duplicated_values = df.loc[duplicated, 'numero'].unique()
        raise ValueError(f"Valor duplicado para numero na linha de índice: '{duplicated_values}'")

    try:
        df['id'] = df['id'].astype(int)
        df['numero'] = df['numero'].astype(str)
        df['tipo'] = df['tipo'].astype(str)
        df['valor_face'] = df['valor_face'].astype(int)
        df['data_protocolo'] = pd.to_datetime(df['data_protocolo'], errors='raise')
        df['origem'] = df['origem'].astype(str)
    except Exception as e:
        raise ValueError(f"Erro ao ajustar tipos das colunas: {e}")

    return df