# Documentação do Projeto: Separador de Áudio com Python
Este documento serve como um guia completo para os requisitos, instalação e execução da aplicação de separação de áudio desenvolvida em Python. A aplicação utiliza a biblioteca Spleeter para separar músicas em stems (voz, bateria, baixo, etc.) e o PyQt6 para a interface gráfica.
# 1. Requisitos do Sistema:

Para que a aplicação funcione corretamente, é necessário ter as seguintes ferramentas instaladas:
Python: É crucial utilizar a versão Python 3.11 ou superior, pois as dependências utilizadas, especialmente o PyQt6-Multimedia, têm requisitos de versão específicos.
pip: O gerenciador de pacotes do Python. Ele já vem instalado com o Python.
FFmpeg: Uma ferramenta externa essencial para processar e misturar arquivos de áudio. Ela deve ser baixada e o caminho para o seu executável deve ser adicionado à variável de ambiente PATH do sistema.
Link para Download: https://ffmpeg.org/download.html
Modelos da Spleeter: Os modelos pré-treinados para a separação de áudio, que devem ser baixados separadamente.
Link para Download: https://github.com/deezer/spleeter/releases (Baixar o arquivo 4stems.tar.gz da versão v1.4.0)

# 2. Estrutura do Projeto

A estrutura de diretórios do projeto é organizada para separar a lógica da interface, tornando-a mais fácil de manter.

#### separador_audio/
#### gui/
     init__.py
     main_window.py
#### core/
     init__.py
     audio_processor.py
#### spleeter_models/
     5stems/
     ... (arquivos do modelo)
main.py

requirements.txt



# 3. Instalação e Configuração
Siga estes passos em ordem para configurar o ambiente e instalar todas as dependências.
     Passo 3.1: Criar e Ativar o Ambiente Virtual
Navegue até o diretório do projeto e execute os seguintes comandos no terminal:
### Criar o ambiente virtual com Python 3.11
    py -3.11 -m venv venv_player

### Ativar o ambiente virtual (Windows)
    venv_player\Scripts\activate



## Passo 3.2: Instalar as Dependências
O requirements.txt contém a lista de bibliotecas necessárias. Para contornar os problemas de dependência do spleeter com versões mais recentes do tensorflow, a instalação deve ser feita manualmente.
Conteúdo do requirements.txt:
PyQt6==6.7.1
pydub
simpleaudio



Comandos de instalação:
### Instalar dependências do Spleeter e TensorFlow de forma controlada
    pip install numpy==1.26.4 tensorflow==2.15.0
    pip install spleeter --no-deps

### Instalar as demais bibliotecas do projeto
    pip install -r requirements.txt



## Passo 3.3: Colocar os Modelos da Spleeter
Após baixar o arquivo 4stems.tar.gz, descompacte-o e mova a pasta 4stems para o diretório spleeter_models que você criou. A estrutura da pasta deve ser: spleeter_models/4stems/.
# 4. Execução da Aplicação
Para executar a aplicação, certifique-se de que o ambiente virtual está ativado. Em seguida, navegue até o diretório principal do projeto (separador_audio/) e use o comando:
python main.py


A janela da aplicação irá se abrir, permitindo que você comece a separar e ouvir os stems de áudio.
