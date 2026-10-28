from pathlib import Path

### define o diretorio base do projeto usando o caminho deste arquivo ###
BASE_DIR = Path(__file__).resolve().parents[1]

### define o caminho do modelo yolo treinado para detecao de olhos ###
MODEL_PATH = str(BASE_DIR / "model" / "best.pt")

### define o caminho do arquivo de audio usado no alerta ###
ALARM_SOUND = str(BASE_DIR / "assets" / "alarm.wav")

### define o nome da classe usada para olhos fechados no modelo ###
CLOSED_CLASS = "closed_eye"

### define o nome da classe usada para olhos abertos no modelo ###
OPEN_CLASS = "open_eye"

### define o limiar de confianca padrao para as deteccoes do yolo ###
CONF_THRESHOLD = 0.6

### define o tempo em segundos com olhos fechados para disparar o alerta ###
ALERT_TIME = 3.0

### define o nome da janela principal de exibicao ###
WINDOW_NAME = "Detector Sonolência - YOLO"

### define o titulo que aparece na barra superior da interface ###
WINDOW_TITLE = "Detector Sonolência - YOLO"