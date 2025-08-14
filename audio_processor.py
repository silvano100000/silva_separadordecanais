import os
import tempfile
from spleeter.separator import Separator
from pydub import AudioSegment

class AudioProcessor:
    def __init__(self):
        self.separator = Separator('spleeter:4stems')
        self.file_path = None
        self.output_dir = None
        self.stems_paths = {} # Dicionário para armazenar os caminhos de cada stem

    def separate_audio(self, input_file_path, output_dir):
        """
        Carrega um arquivo de áudio e o separa em stems.

        :param input_file_path: Caminho completo para o arquivo de áudio.
        :param output_dir: Diretório onde os stems separados serão salvos.
        :return: True se a separação foi bem-sucedida, False caso contrário.
        """
        try:
            self.file_path = input_file_path
            self.output_dir = output_dir
            
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            
            self.separator.separate_to_file(self.file_path, self.output_dir)
            
            # Armazena os caminhos dos stems separados
            base_filename = os.path.splitext(os.path.basename(self.file_path))[0]
            stem_folder = os.path.join(self.output_dir, base_filename)
            self.stems_paths = {
                'vocals': os.path.join(stem_folder, 'vocals.wav'),
                'drums': os.path.join(stem_folder, 'drums.wav'),
                'bass': os.path.join(stem_folder, 'bass.wav'),
                'other': os.path.join(stem_folder, 'other.wav'),
            }
            
            print(f"Música separada com sucesso. Stems salvos em: {stem_folder}")
            return True
        except Exception as e:
            print(f"Erro ao separar o áudio: {e}")
            self.stems_paths = {}
            return False
    
    def mix_stems(self, stem_volumes):
        """
        Mistura os stems de áudio selecionados e salva em um arquivo temporário.

        :param stem_volumes: Um dicionário com o nome do stem e o ajuste de volume em dB.
        :return: O caminho para o arquivo temporário mixado, ou None se nenhum stem for selecionado.
        """
        enabled_stems = [name for name, volume in stem_volumes.items() if volume is not None]

        if not enabled_stems:
            print("Nenhum stem selecionado para mixar.")
            return None

        try:
            # Carrega o primeiro stem com o volume ajustado
            first_stem_name = enabled_stems[0]
            first_stem = AudioSegment.from_file(self.stems_paths[first_stem_name])
            first_stem_adjusted = first_stem + stem_volumes[first_stem_name]
            mixed_audio = first_stem_adjusted

            # Mistura os stems restantes com seus volumes ajustados
            for stem_name in enabled_stems[1:]:
                next_stem = AudioSegment.from_file(self.stems_paths[stem_name])
                next_stem_adjusted = next_stem + stem_volumes[stem_name]
                mixed_audio = mixed_audio.overlay(next_stem_adjusted)
                
            # Cria um arquivo temporário para a mixagem
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            mixed_audio.export(temp_file.name, format="wav")
            temp_file.close()

            print(f"Stems mixados e salvos temporariamente em: {temp_file.name}")
            return temp_file.name
        except Exception as e:
            print(f"Erro ao misturar os stems: {e}")
            return None
