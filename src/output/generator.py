import pandas as pd
import os
import datetime
from data.file_manager import save_csv, save_json
from loggers.logger import log_message

def load_existing_proposals(path):
    if os.path.exists(path):
        try:
            df_existing = pd.read_csv(path, encoding="utf-8", dtype={"numero": str})
            return df_existing
        except Exception as e:
            print(f"Erro ao ler propostas existentes: {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def update_existing_proposals(existing_df, new_df):
    updated = 0

    existing_numbers = set(existing_df["numero"])
    new_numbers = set(new_df["numero"])

    for numero in existing_numbers & new_numbers:
        old_values = existing_df.loc[existing_df["numero"] == numero, ["desagio_pct", "valor_compra"]].astype(float).round(2).values
        new_values = new_df.loc[new_df["numero"] == numero, ["desagio_pct", "valor_compra"]].astype(float).round(2).values

        if not (old_values == new_values).all():
            existing_df.loc[existing_df["numero"] == numero, ["desagio_pct", "valor_compra"]] = new_values
            updated += 1

    to_remove = existing_numbers - new_numbers
    if to_remove:
        existing_df = existing_df[~existing_df["numero"].isin(to_remove)]
        updated += len(to_remove)

    return existing_df, updated

def add_new_proposals(existing_df, new_df):
    generated = 0
    existing_numbers = set(existing_df["numero"])
    to_add = new_df[~new_df["numero"].isin(existing_numbers)]
    if not to_add.empty:
        existing_df = pd.concat([existing_df, to_add], ignore_index=True)
        generated = len(to_add)
    return existing_df, generated

def save_proposals_with_idempotency(new_df, path):
    existing_df = load_existing_proposals(path)
    existing = len(existing_df)

    if existing_df.empty:
        existing_df = new_df.copy()
        save_csv(existing_df, path)
        return len(new_df), 0, 0

    existing_df["numero"] = existing_df["numero"].astype(str).str.strip()
    new_df["numero"] = new_df["numero"].astype(str).str.strip()

    existing_df, updated = update_existing_proposals(existing_df, new_df)
    existing_df, generated = add_new_proposals(existing_df, new_df)

    save_csv(existing_df, path)
    return generated, updated, existing

def generate_metrics(total_lines, df_proposals, outoput_csv_path, input_csv_path, metrics_json_path):
    try:
        generates, updated, existing = save_proposals_with_idempotency(df_proposals, outoput_csv_path)
    
        now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        timestamp = now.isoformat().replace("+00:00", "Z")

        metrics = {
            "timestamp": timestamp,
            "input": input_csv_path,
            "lidos": total_lines,
            "elegiveis": len(df_proposals),
            "gerados": generates,
            "ja_existentes": existing,
            "atualizados": updated
        }
        save_json(metrics, metrics_json_path)
        log_message(metrics)
    except Exception as e:
        raise RuntimeError(f"Erro ao gerar métricas: {e}") from e