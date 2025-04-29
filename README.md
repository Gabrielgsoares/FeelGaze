# FeelGaze - Eye Tracking Assistivo

**FeelGaze** é um projeto de acessibilidade que permite o controle do computador através do movimento dos olhos e da boca, ideal para pessoas com limitações motoras severas.

## 🚀 Funcionalidades

- Rastreamento do rosto e dos olhos usando MediaPipe
- Detecção da boca aberta para ativar/desativar o clique assistido
- Cursor do mouse controlado pelos olhos
- Clique automático por fixação visual
- Interface de configurações acessível com o olhar
- Preferências de sensibilidade e tempo de clique salvas automaticamente (`settings/config.json`)

## 🛠️ Requisitos

- Python 3.10 ou superior
- macOS (por enquanto, o executável para Mac está com limitações técnicas devido ao uso do MediaPipe)

## 📦 Instalação e execução

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/FeelGaze.git
cd FeelGaze
```

2. Crie um ambiente virtual:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o sistema:
```bash
python tracking.py
```

## 📁 Estrutura do Projeto

```
FeelGaze/
├── tracking.py              # Código principal de rastreamento
├── settings_window.py       # Interface gráfica de configurações
├── menu_indicator.py        # Barra visual de carregamento
├── settings/
│   └── config.json          # Arquivo com preferências do usuário
├── requirements.txt
└── README.md
```

## 📌 Observações

- O projeto ainda está em fase de testes.
- O empacotamento para Mac (.app) enfrenta limitações por conta do MediaPipe.
- Funciona perfeitamente ao rodar diretamente com Python.

## ✨ Desenvolvido por

Gabriel Gonçalves Soares
