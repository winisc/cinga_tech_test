import os
import json
import pandas as pd
from loggers.logger import log_message

def load_csv(path_csv):
    if not os.path.exists(path_csv):
        raise FileNotFoundError(f"Arquivo não encontrado: {path_csv}")
    try:
        df = pd.read_csv(path_csv, encoding="utf-8")
        log_message("Arquivo '%s' carregado com sucesso." % path_csv)
    except Exception as e:
        raise IOError(f"Erro ao ler CSV: {e}")
    return df

def save_csv(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    log_message(f"CSV salvo com sucesso em '{path}'.")

def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        log_message(f"JSON salvo com sucesso em '{path}'.")
    except Exception as e:
        raise IOError(f"Erro ao salvar JSON: {e}")

