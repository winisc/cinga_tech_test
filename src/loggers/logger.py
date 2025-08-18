import os
import datetime
import config.settings as config

def log_message(message, use_utc=True):
    logfile_path = config.LOG_PATH
    
    now = datetime.datetime.now(datetime.timezone.utc) if use_utc else datetime.datetime.now()
    timestamp = now.isoformat() + "Z" if use_utc else now.isoformat()
    
    log_line = "[%s] %s" % (timestamp, message)
    
    print(log_line)
    
    try:
        os.makedirs(os.path.dirname(logfile_path), exist_ok=True)
        with open(logfile_path, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except Exception as e:
        print(f"Falha ao gravar log em {logfile_path}: {e}")
