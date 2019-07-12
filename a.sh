#! /bin/bash
sudo rm -r ForadaMatrix #apaga pastas anteriores deste repositório
git clone https://github.com/foradamatrix/ForadaMatrix.git #clona o repositório
clear
sudo apt install python3 #intala dependências 
cd ForadaMatrix && sudo pip3 install -r requirements.txt #entra na pasta e inicia a instalação das dependências
clear
echo abrindo arquivo para edição interna de variáveis ... #abre o arquivo para edição da "API_TOKEN" e "ADMIN"
gedit foradamatrix.py 
clear
echo executando bot ...
python3 foradamatrix.py #executa o bot após a edição ser fechada
cd ..
