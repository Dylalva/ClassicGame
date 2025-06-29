"""
Gestor de sonidos del juego
"""

import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.load_sounds()
    
    def load_sounds(self):
        """Carga todos los sonidos del juego"""
        sound_files = {
            'jump': 'jump.wav',
            'damage': 'damage.wav',
            'point': 'point.wav',
            'game_over': 'game_over.wav',
            'menu_select': 'menu_select.wav',
            'background': 'background.mp3'
        }
        
        for sound_name, filename in sound_files.items():
            filepath = os.path.join('assets', 'sounds', filename)
            try:
                if filename.endswith('.mp3'):
                    # Para música de fondo
                    self.sounds[sound_name] = filepath
                else:
                    # Para efectos de sonido
                    sound = pygame.mixer.Sound(filepath)
                    sound.set_volume(self.sfx_volume)
                    self.sounds[sound_name] = sound
            except (pygame.error, FileNotFoundError):
                # Si no existe el archivo, crear un sonido silencioso
                print(f"Sonido no encontrado: {filepath}")
                if not filename.endswith('.mp3'):
                    self.sounds[sound_name] = None
    
    def play_sound(self, sound_name):
        """Reproduce un efecto de sonido"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except:
                pass
    
    def play_music(self, music_name, loop=-1):
        """Reproduce música de fondo"""
        if music_name in self.sounds:
            try:
                pygame.mixer.music.load(self.sounds[music_name])
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loop)
            except:
                pass
    
    def stop_music(self):
        """Detiene la música"""
        pygame.mixer.music.stop()
    
    def set_music_volume(self, volume):
        """Ajusta el volumen de la música (0.0 - 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        """Ajusta el volumen de efectos (0.0 - 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound_name, sound in self.sounds.items():
            if sound and hasattr(sound, 'set_volume'):
                sound.set_volume(self.sfx_volume)