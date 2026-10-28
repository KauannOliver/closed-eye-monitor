import pygame
from pygame import mixer

import config

### sistema responsavel pelo audio de alerta ###
class AlertSystem:
    def __init__(self) -> None:
        ### inicializa o sistema de audio do pygame e configura o caminho do som ###
        self.sound_path = config.ALARM_SOUND
        self._audio_ok = False

        try:
            mixer.init()
            self._audio_ok = True
        except Exception as e:
            ### caso o audio falhe, apenas exibe um aviso no console ###
            print(f"[AVISO] Não foi possível inicializar o áudio: {e}")
            self._audio_ok = False

    def play(self) -> None:
        ### toca o som de alerta em loop se o audio estiver disponivel ###
        if not self._audio_ok:
            return

        if not mixer.music.get_busy():
            try:
                mixer.music.load(self.sound_path)
                mixer.music.play(-1)  ### -1 significa repetir indefinidamente ###
            except Exception as e:
                ### se houver erro ao tocar o som, desabilita o audio para evitar loops de erro ###
                print(f"[AVISO] Erro ao tocar o som de alerta: {e}")
                self._audio_ok = False

    def stop(self) -> None:
        ### para o som de alerta se estiver sendo reproduzido ###
        if not self._audio_ok:
            return

        if mixer.music.get_busy():
            mixer.music.stop()
