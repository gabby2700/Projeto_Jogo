# AGENTS.md — Kawaii Warriors

## Objetivo
Desenvolver um jogo de luta 3D casual em Python/Panda3D, ambientado em ilhas flutuantes. O visual deve ser kawaii, colorido e não gráfico.

## Arquitetura
- `main.py`: protótipo jogável, arena procedural, personagens, menus e combate.
- `requirements.txt`: dependência Panda3D.
- `README.md`: instalação, execução e controles.

## Diretrizes
1. Preserve a estética fofa, pastel e fantástica; não adicione sangue ou violência gráfica.
2. Mantenha movimentação responsiva e combate legível.
3. Personagens devem ter nome, paleta, poder e opções de roupa/acessório.
4. Prefira módulos e classes pequenas ao expandir o protótipo.
5. Evite dependências adicionais sem necessidade; documente novas dependências.
6. Valide alterações com `python -m py_compile main.py` e teste a inicialização quando possível.
7. Atualize o README sempre que controles, telas ou instalação mudarem.

## Próximas melhorias
- Animações esqueléticas e modelos 3D externos (GLB).
- Telas de loja e inventário com itens desbloqueáveis.
- Combos, bloqueio, barra de energia e modo para dois jogadores.
- Áudio, opções gráficas e remapeamento de controles.
