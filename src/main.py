from output.generator import generate_metrics
from loggers.logger import log_message
from data.validator import validate_and_treat_df
from data.file_manager import load_csv
from engine.processor import processing_eligible_proposals
import config.settings as settings
import time

if __name__ == "__main__":
    start_time = time.perf_counter()
    try:
        log_message((f"Início do processamento"))
        df = load_csv(settings.INPUT_CSV_PATH)
        df = validate_and_treat_df(df)
        total_cases, df_proposals_new = processing_eligible_proposals(df)
        generate_metrics(total_cases, df_proposals_new, settings.OUTPUT_CSV_PATH, settings.INPUT_CSV_PATH, settings.METRICS_JSON_PATH)
        elapsed = time.perf_counter() - start_time
        log_message(f"Fim do processamento ({elapsed:.2f}s)\n")
    except Exception as e:
        log_message(f"Erro: {e}")
        elapsed = time.perf_counter() - start_time
        log_message(f"Fim do processamento ({elapsed:.2f}s)\n")