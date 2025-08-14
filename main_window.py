import os
import simpleaudio as sa
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QCheckBox,
                             QGroupBox, QSlider)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt
import time
from core.audio_processor import AudioProcessor

# Classe para rodar a separação de áudio em uma thread separada
# Isso evita que a interface congele durante o processamento
class SpleeterThread(QThread):
    separation_finished = pyqtSignal(bool)
    
    def __init__(self, audio_processor, input_file_path, output_dir):
        super().__init__()
        self.audio_processor = audio_processor
        self.input_file_path = input_file_path
        self.output_dir = output_dir

    def run(self):
        success = self.audio_processor.separate_audio(self.input_file_path, self.output_dir)
        self.separation_finished.emit(success)

# Classe principal da aplicação
class AudioSeparatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.audio_processor = AudioProcessor()
        self.spleeter_thread = None
        self.play_obj = None
        self.temp_mixed_file_path = None
        self.play_timer = None
        self.playback_start_time = 0
        self.current_play_position = 0
        self.audio_duration = 0
        self.app_version = "v1.1"
        
        self.setWindowTitle("SILVA - Separador de canais")
        self.setGeometry(100, 100, 600, 500)
        
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        
        self.create_file_selection_ui()
        self.create_status_ui()
        self.create_stems_control_ui()
        self.create_playback_ui()
        self.create_footer_ui()
        
    def create_file_selection_ui(self):
        """Cria o grupo de UI para seleção de arquivos."""
        file_group = QGroupBox("Seleção de Arquivo")
        group_layout = QVBoxLayout()
        
        h_layout = QHBoxLayout()
        self.file_label = QLabel("Nenhum arquivo selecionado.")
        h_layout.addWidget(self.file_label)
        
        select_button = QPushButton("Selecionar Arquivo")
        select_button.clicked.connect(self.select_file)
        h_layout.addWidget(select_button)
        
        self.separate_button = QPushButton("Separar Áudio")
        self.separate_button.clicked.connect(self.start_separation)
        self.separate_button.setEnabled(False)
        h_layout.addWidget(self.separate_button)
        
        group_layout.addLayout(h_layout)
        file_group.setLayout(group_layout)
        self.main_layout.addWidget(file_group)
        
    def create_status_ui(self):
        """Cria o grupo de UI para exibir o status da aplicação."""
        status_group = QGroupBox("Status da Aplicação")
        group_layout = QVBoxLayout()
        
        self.status_label = QLabel("Aguardando seleção de arquivo...")
        group_layout.addWidget(self.status_label)
        
        status_group.setLayout(group_layout)
        self.main_layout.addWidget(status_group)

    def create_stems_control_ui(self):
        """Cria o grupo de UI para controle de stems com checkboxes."""
        stems_group = QGroupBox("Controle de Stems")
        self.stems_layout = QHBoxLayout()
        
        self.stems_controls = {}
        stem_names = ['vocals', 'drums', 'bass', 'other']
        for name in stem_names:
            checkbox = QCheckBox(name.capitalize())
            checkbox.setChecked(True)
            checkbox.setEnabled(False) # Desabilita inicialmente
            checkbox.stateChanged.connect(self.on_stem_control_changed)
            
            self.stems_controls[name] = {
                'checkbox': checkbox
            }
            self.stems_layout.addWidget(checkbox)
            
        stems_group.setLayout(self.stems_layout)
        self.main_layout.addWidget(stems_group)
        
    def on_stem_control_changed(self):
        """Reinicia a reprodução para aplicar os novos volumes."""
        if self.play_obj and self.play_obj.is_playing():
            self.play_mixed_audio()
            
    def create_playback_ui(self):
        """Cria o grupo de UI para controles de reprodução."""
        playback_group = QGroupBox("Controles de Reprodução")
        group_layout = QVBoxLayout()
        
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.setValue(0)
        self.progress_slider.setEnabled(False)
        self.progress_slider.sliderMoved.connect(self.on_progress_slider_moved)
        group_layout.addWidget(self.progress_slider)
        
        self.playback_controls_layout = QHBoxLayout()
        
        self.play_button = QPushButton("Reproduzir")
        self.play_button.clicked.connect(self.play_mixed_audio)
        self.play_button.setEnabled(False)
        self.playback_controls_layout.addWidget(self.play_button)
        
        self.stop_button = QPushButton("Parar")
        self.stop_button.clicked.connect(self.stop_audio)
        self.stop_button.setEnabled(False)
        self.playback_controls_layout.addWidget(self.stop_button)
        
        group_layout.addLayout(self.playback_controls_layout)
        playback_group.setLayout(group_layout)
        self.main_layout.addWidget(playback_group)
        
    def create_footer_ui(self):
        """Cria um rodapé com a versão da aplicação."""
        footer_layout = QHBoxLayout()
        version_label = QLabel(f"Versão: {self.app_version}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        footer_layout.addStretch(1) # Adiciona espaço flexível à esquerda
        footer_layout.addWidget(version_label)
        self.main_layout.addLayout(footer_layout)

    def select_file(self):
        """Abre o diálogo para selecionar um arquivo de áudio."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo de Áudio", "", "Arquivos de Áudio (*.mp3 *.wav)")
        if file_path:
            self.file_label.setText(f"Arquivo selecionado: {os.path.basename(file_path)}")
            self.status_label.setText("Arquivo pronto para separação.")
            self.audio_processor.file_path = file_path
            self.separate_button.setEnabled(True)
            self.play_button.setEnabled(False)
            self.stop_audio()
            
    def start_separation(self):
        """Inicia o processo de separação de áudio em uma thread."""
        if self.audio_processor.file_path:
            self.status_label.setText("Separando áudio... Por favor, aguarde.")
            self.separate_button.setEnabled(False)
            self.play_button.setEnabled(False)
            
            output_dir = os.path.join(os.path.dirname(self.audio_processor.file_path), "stems_output")
            
            self.spleeter_thread = SpleeterThread(self.audio_processor, self.audio_processor.file_path, output_dir)
            self.spleeter_thread.separation_finished.connect(self.on_separation_finished)
            self.spleeter_thread.start()
            
    def on_separation_finished(self, success):
        """Callback chamado quando a separação termina."""
        self.separate_button.setEnabled(True)
        if success:
            self.status_label.setText("Separação concluída com sucesso! Ajuste os volumes e clique em Reproduzir.")
            self.play_button.setEnabled(True)
            self.progress_slider.setEnabled(True)
            
            # Habilita os controles dos stems
            for control in self.stems_controls.values():
                control['checkbox'].setEnabled(True)
            
            # Obtém a duração do áudio para o slider de progresso
            try:
                from pydub import AudioSegment
                first_stem = AudioSegment.from_file(list(self.audio_processor.stems_paths.values())[0])
                self.audio_duration = len(first_stem) # Duração em milissegundos
                self.progress_slider.setRange(0, self.audio_duration)
            except Exception as e:
                print(f"Erro ao obter a duração do áudio: {e}")
            
        else:
            self.status_label.setText("Erro na separação. Tente novamente.")
            self.play_button.setEnabled(False)
            self.progress_slider.setEnabled(False)
            
    def get_current_stem_volumes(self):
        """Retorna um dicionário com os volumes dos stems selecionados."""
        stem_volumes = {}
        for name, control in self.stems_controls.items():
            if control['checkbox'].isChecked():
                stem_volumes[name] = 0.0 # Volume 0 dB (original) se o checkbox estiver marcado
        return stem_volumes

    def play_mixed_audio(self):
        """Reproduz o áudio mixado a partir dos stems selecionados."""
        self.stop_audio()
        
        stem_volumes = self.get_current_stem_volumes()
        
        if not stem_volumes:
            self.status_label.setText("Por favor, selecione pelo menos um stem para reproduzir.")
            return

        self.temp_mixed_file_path = self.audio_processor.mix_stems(stem_volumes)

        if self.temp_mixed_file_path:
            self.status_label.setText(f"Reproduzindo stems mixados...")
            self.play_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.progress_slider.setValue(0) # Zera o slider
            self.current_play_position = 0
            
            try:
                wave_obj = sa.WaveObject.from_wave_file(self.temp_mixed_file_path)
                self.play_obj = wave_obj.play()
                self.playback_start_time = time.time()
                
                if self.play_timer is None:
                    self.play_timer = QTimer(self)
                    self.play_timer.timeout.connect(self.update_playback_progress)
                self.play_timer.start(50)
                
            except Exception as e:
                self.status_label.setText(f"Erro ao reproduzir o áudio: {e}")
                self.play_button.setEnabled(True)
                self.stop_button.setEnabled(False)

    def on_progress_slider_moved(self, position):
        """Reinicia a reprodução a partir do início com as novas configurações."""
        # A biblioteca simpleaudio não suporta seeking.
        # Portanto, apenas reiniciamos a reprodução com a nova mixagem.
        if self.play_obj and self.play_obj.is_playing():
            self.play_mixed_audio()
    
    def update_playback_progress(self):
        """Atualiza a posição do slider de progresso e para a reprodução quando termina."""
        if self.play_obj and self.play_obj.is_playing():
            elapsed_time_ms = int((time.time() - self.playback_start_time) * 1000)
            self.current_play_position = elapsed_time_ms
            self.progress_slider.setValue(self.current_play_position)
        else:
            self.stop_audio()

    def stop_audio(self):
        """Para a reprodução de áudio e reinicia os controles."""
        if self.play_obj and self.play_obj.is_playing():
            self.play_obj.stop()
        
        if self.play_timer and self.play_timer.isActive():
            self.play_timer.stop()
            
        self.play_obj = None
        self.stop_button.setEnabled(False)
        self.play_button.setEnabled(True)
        self.current_play_position = 0
        self.progress_slider.setValue(0)
        
        if self.audio_processor.stems_paths:
            self.status_label.setText("Reprodução parada. Ajuste os volumes e clique em Reproduzir.")
        else:
            self.status_label.setText("Separação concluída com sucesso! Ajuste os volumes e clique em Reproduzir.")
