from typing import Optional, Union

import cv2
from ultralytics import YOLO
from pathlib import Path

import config

### classe responsavel por carregar o modelo yolo e fazer a deteccao dos olhos ###
class EyeDetector:
    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        conf_threshold: Optional[float] = None,
    ) -> None:
        ### define o caminho do modelo yolo a partir do parametro ou da configuracao padrao ###
        self.model_path = str(model_path or config.MODEL_PATH)

        ### define o limiar de confianca a partir do parametro ou da configuracao padrao ###
        self.conf_threshold = conf_threshold if conf_threshold is not None else config.CONF_THRESHOLD

        ### carrega o modelo yolo treinado ###
        self.model = YOLO(self.model_path)

    def detect(self, frame):
        ### executa o modelo yolo no frame com o limiar de confianca configurado ###
        results = self.model(frame, conf=self.conf_threshold, verbose=False)

        eye_closed = False
        annotated_frame = frame

        ### itera sobre os resultados retornados pelo modelo ###
        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes:
                ### extrai coordenadas da caixa delimitadora ###
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                ### extrai o id da classe e a confianca da deteccao ###
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])

                ### obtem o nome da classe em letras minusculas ###
                label = self.model.names[cls_id].lower()

                ### define a cor padrao da caixa como verde ###
                color = (0, 255, 0)

                ### se a classe detectada for olho fechado, ajusta a cor e o estado ###
                if label == config.CLOSED_CLASS:
                    eye_closed = True
                    color = (0, 0, 255)

                ### desenha a caixa delimitadora ao redor do olho ###
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)

                ### monta o texto com o nome da classe e a confianca ###
                text = f"{label} {conf:.2f}"

                ### calcula a posicao do texto acima da caixa garantindo que fique dentro da imagem ###
                text_y = y1 - 10 if y1 - 10 > 10 else y1 + 20

                ### desenha o texto com o nome da classe e o valor da confianca ###
                cv2.putText(
                    annotated_frame,
                    text,
                    (x1, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2,
                    cv2.LINE_AA,
                )

        ### retorna se ha olhos fechados e o frame anotado ###
        return eye_closed, annotated_frame
