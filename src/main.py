import argparse
import datetime as dt
import time
from typing import Optional

import cv2

import config
from alert import AlertSystem
from detector import EyeDetector

### desenha toda a interface visual sobre o frame ###
def draw_ui(frame, is_closed: bool, timer: float, alert_time: float):
    ### garante que o frame tenha dimensoes validas ###
    if frame is None:
        return frame

    h, w, _ = frame.shape

    ### define a cor e espessura da borda com base no estado de sonolencia ###
    if is_closed and timer >= alert_time:
        border_color = (0, 0, 255)  ### vermelho para alerta critico ###
        border_thickness = 15
    else:
        border_color = (255, 255, 0)  ### amarelo claro para estado normal ###
        border_thickness = 4

    ### desenha a borda ao redor de todo o frame ###
    cv2.rectangle(frame, (0, 0), (w - 1, h - 1), border_color, border_thickness)

    ### desenha a barra superior como um cabecalho escuro ###
    header_height = int(0.12 * h)
    cv2.rectangle(frame, (0, 0), (w, header_height), (30, 30, 30), -1)

    ### desenha o titulo do sistema no cabecalho ###
    title_text = config.WINDOW_TITLE
    cv2.putText(
        frame,
        title_text,
        (20, int(header_height * 0.65)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    ### obtem o horario atual para exibir no cabecalho ###
    now_text = dt.datetime.now().strftime("%H:%M:%S")
    (tw, th), _ = cv2.getTextSize(now_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)

    ### desenha o horario no lado direito do cabecalho ###
    cv2.putText(
        frame,
        now_text,
        (w - tw - 20, int(header_height * 0.65)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (200, 200, 200),
        2,
        cv2.LINE_AA,
    )

    ### define a mensagem de status com base no estado e no tempo ###
    status_y = header_height + 40

    if is_closed and timer >= alert_time:
        status_text = "Status: SONOLÊNCIA CRÍTICA!"
        status_color = (0, 0, 255)
    elif is_closed:
        status_text = "Status: Olhos Fechados"
        status_color = (0, 165, 255)
    else:
        status_text = "Status: Olhos Abertos"
        status_color = (0, 200, 0)

    ### desenha a mensagem de status no centro da tela ###
    cv2.putText(
        frame,
        status_text,
        (20, status_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        status_color,
        2,
        cv2.LINE_AA,
    )

    ### configura a barra de progresso do tempo com olhos fechados ###
    bar_width = int(w * 0.3)
    bar_height = 20
    bar_x = w - bar_width - 20
    bar_y = h - bar_height - 30

    ### desenha a moldura da barra de progresso ###
    cv2.rectangle(
        frame,
        (bar_x, bar_y),
        (bar_x + bar_width, bar_y + bar_height),
        (255, 255, 255),
        2,
    )

    ### calcula o progresso relativo ao tempo de alerta ###
    progress = max(0.0, min(1.0, timer / alert_time))
    filled_width = int(bar_width * progress)

    ### escolhe a cor do preenchimento com base no nivel de progresso ###
    if progress < 0.5:
        bar_color = (0, 200, 200)  ### azul esverdeado ###
    elif progress < 1.0:
        bar_color = (0, 165, 255)  ### laranja ###
    else:
        bar_color = (0, 0, 255)  ### vermelho para tempo excedido ###

    ### desenha a parte preenchida da barra de progresso ###
    cv2.rectangle(
        frame,
        (bar_x, bar_y),
        (bar_x + filled_width, bar_y + bar_height),
        bar_color,
        -1,
    )

    ### texto com o valor numerico do tempo ###
    timer_text = f"{timer:.1f}s / {alert_time:.1f}s"
    cv2.putText(
        frame,
        timer_text,
        (bar_x, bar_y - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )

    ### desenha uma dica de teclado no rodape ###
    help_text = "ESC: Sair  |  F: Alterna tela cheia"
    cv2.putText(
        frame,
        help_text,
        (20, h - 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (220, 220, 220),
        1,
        cv2.LINE_AA,
    )

    ### retorna o frame anotado com a interface ###
    return frame


### alterna o modo de exibicao da janela entre normal e tela cheia ###
def toggle_fullscreen(is_fullscreen: bool) -> bool:
    ### verifica o modo atual e alterna a propriedade da janela ###
    if is_fullscreen:
        cv2.setWindowProperty(
            config.WINDOW_NAME,
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_NORMAL,
        )
    else:
        cv2.setWindowProperty(
            config.WINDOW_NAME,
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_FULLSCREEN,
        )

    ### retorna o novo estado de tela cheia ###
    return not is_fullscreen


### funcao principal do sistema de detecao de sonolencia ###
def main():
    ### configura o parser de argumentos para permitir algumas opcoes via linha de comando ###
    parser = argparse.ArgumentParser(
        description="Sistema de Detecção de Sonolência de Motoristas com YOLO"
    )
    parser.add_argument(
        "-c",
        "--camera",
        type=int,
        default=0,
        help="Índice da câmera a ser usada (padrão: 0).",
    )
    parser.add_argument(
        "-t",
        "--alert-time",
        type=float,
        default=config.ALERT_TIME,
        help="Tempo em segundos com olhos fechados para disparar o alerta.",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=config.CONF_THRESHOLD,
        help="Limiar de confiança do modelo YOLO.",
    )

    args = parser.parse_args()

    ### guarda o tempo de alerta configurado ###
    alert_time = args.alert_time

    ### cria o detector de olhos com o limiar de confianca informado ###
    detector = EyeDetector(conf_threshold=args.conf)

    ### cria o sistema de alerta sonoro ###
    alert = AlertSystem()

    ### abre a captura de video da camera selecionada ###
    cap = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("[ERRO] Não foi possível acessar a câmera.")
        return

    ### cria a janela principal em modo normal ###
    cv2.namedWindow(config.WINDOW_NAME, cv2.WINDOW_NORMAL)
    is_fullscreen = False

    ### armazena o instante em que os olhos foram detectados fechados pela primeira vez ###
    closed_start: Optional[float] = None

    while True:
        ### captura um frame da camera ###
        ret, frame = cap.read()

        if not ret:
            print("[ERRO] Não foi possível ler frame da câmera.")
            break

        ### executa a deteccao de olhos no frame ###
        is_closed, annotated = detector.detect(frame)

        ### calcula o tempo acumulado com olhos fechados ###
        timer = 0.0

        if is_closed:
            ### inicia o contador se ainda nao foi iniciado ###
            if closed_start is None:
                closed_start = time.time()

            ### calcula o tempo decorrido desde que os olhos foram fechados ###
            timer = time.time() - closed_start
        else:
            ### reseta o contador e interrompe o alerta quando os olhos abrem ###
            closed_start = None
            alert.stop()

        ### dispara o alerta sonoro se o tempo exceder o limite configurado ###
        if timer >= alert_time:
            alert.play()

        ### desenha a interface visual sobre o frame anotado ###
        ui_frame = draw_ui(annotated, is_closed, timer, alert_time)

        ### exibe o frame final na janela ###
        cv2.imshow(config.WINDOW_NAME, ui_frame)

        ### captura a tecla pressionada pelo usuario ###
        key = cv2.waitKey(1) & 0xFF

        ### tecla esc encerra o programa ###
        if key == 27:
            break

        ### tecla f alterna o modo de tela cheia ###
        if key == ord("f"):
            is_fullscreen = toggle_fullscreen(is_fullscreen)

    ### libera a camera ao final da execucao ###
    cap.release()

    ### destroi todas as janelas do opencv ###
    cv2.destroyAllWindows()

    ### garante que o alerta sonoro seja interrompido ###
    alert.stop()


### ponto de entrada do script ###
if __name__ == "__main__":
    main()