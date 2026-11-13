# Citizen Assist AI: módulo de Energias Renováveis e Sustentáveis 
> 1CCPI

## Integrantes
- Gustavo Kunitaki - RM: 571400
- Pedro Santos - 571017
- Pedro Ferreras - 568713

## Público e problema
Moradores de comunidades em São Paulo (SP) que usam chuveiro elétrico e sentem o peso da conta de luz. O assistente estima o consumo do banho, compara alternativas e orienta o usuário, com fontes e limitações.

## Funcionalidades de energia
1. Estima consumo (kWh/mês) e custo (R$/mês) do chuveiro a partir de pessoas, minutos de banho e potência.
2. Compara: Base x **A) hábitos e regulagem** x **B) aquecedor solar (fonte renovável)**, com custo, payback, viabilidade e CO₂.
3. Responde perguntas simples (economia, solar, bandeira tarifária, CO₂), sempre com fontes e limitações.

## Como executar
```bash
python src/assistente.py      # assistente no terminal
python src/calculos.py        # regenera docs/comparacao_alternativas.md
```


## Estrutura
- `dados/premissas.csv`: dados e estimativas, com tipo e fonte
- `src/calculos.py`, `src/assistente.py`: cálculos e assistente
- `docs/comparacao_alternativas.md`: resultados e sensibilidade
- `docs/justificativas.md`: custos, viabilidade e impactos
- `docs/referencias.md`: fontes
- `testes_usuarios/registro_testes.md`: testes e ajustes
- `docs/roteiro_video.md`: roteiro do vídeo

## Limitações
Os resultados são estimativas, não garantias. A tarifa, a bandeira, o uso real e o custo do aquecedor solar mudam o resultado. Premissas marcadas como "estimativa" devem ser substituídas por dados verificados.
