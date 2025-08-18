from data.file_manager import load_csv
from engine.rules import filter_eligibility, generate_discounted_proposals
import config.settings as settings

def processing_eligible_proposals(df):
    df_eligibility = filter_eligibility(df, settings.MIN_FACE_VALUE)
    if df_eligibility.empty:
        raise ValueError("Nenhum caso elegível encontrado para gerar propostas.")

    total_lines = len(df)
    df_proposals_new = generate_discounted_proposals(df_eligibility, settings)

    return total_lines, df_proposals_new