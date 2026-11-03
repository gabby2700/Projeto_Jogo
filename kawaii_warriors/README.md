# Kawaii Warriors

Protótipo 3D de luta kawaii feito em Python + Panda3D. A arena é uma ilha flutuante com nuvens, cristais e pequenas ilhas ao fundo. Personagens e cenário são construídos proceduralmente com modelos básicos do Panda3D, sem downloads de assets.

## Requisitos
- Python 3.10+
- Panda3D

## Instalação (Windows / VS Code)
Abra o terminal na pasta do projeto e execute:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

Se houver mais de uma instalação do Python, use o mesmo comando `python` para instalar e executar.

## Controles
- `ENTER`: avançar / iniciar / reiniciar
- `C`: abrir ateliê
- `ESC`: voltar ao menu
- `1`, `2`, `3`: escolher personagem
- `A` / `D`: mover para os lados
- `W` / `S`: mover na profundidade
- `ESPAÇO`: pular
- `J`: ataque normal
- `K`: poder especial (consome energia)
- `L`: trocar arma durante a luta
- No ateliê: setas esquerda/direita alteram roupa; `R` também troca roupa e `T` troca arma

## Observação
Este é um protótipo inicial. Os personagens 3D são montados com primitivas geométricas; para um visual de produção, a próxima etapa é substituir essas formas por modelos 3D estilizados em formato GLB/GLTF com animações.
