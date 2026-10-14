```markdown
# Relatório Técnico - SCIC (Sistema de Comunicação Interplanetária da Colônia)
**Missão Aurora Siger - Marte**  
**Autor:** André Victor Cunha de Souza (RM: 574035) — FIAP

---

## 1. Contexto da Solução
Com a expansão da infraestrutura na colônia Aurora Siger em Marte, a comunicação interplanetária tornou-se vital. O **SCIC** foi desenvolvido como uma camada computacional para monitorar a latência dos sensores, prever instabilidades de transmissão, priorizar alertas de emergência e inspecionar a integridade elétrica dos módulos.

---

## 2. Organização dos Dados Operacionais
A base de dados simulada (`dados_aurora_siger.csv`) armazena a telemetria dos módulos da colônia (Comunicação, Habitação, Agricultura, Laboratório, Suporte Médico e Armazenamento).

### Campos Estruturados:
* `nome_modulo`: Identificação do setor.
* `tipo_modulo`: Categoria operacional do módulo.
* `latencia_observada_ms`: Tempo real de resposta (ms).
* `latencia_prevista_ms`: Tempo ideal estimado de resposta (ms).
* `tensao_v` e `corrente_a`: Parâmetros de energia (Volts e Ampères).
* `status_operacional`: Estado funcional (Ativo, Alerta, Manutenção).
* `nivel_prioridade`: Criticidade (1 = Prioridade Máxima/Urgente, 5 = Normal).
* `codigo_sensor_hex`: Código de identificação em formato Hexadecimal (`0x1F3A`).
* `mensagem_alerta`: Resumo descritivo da condição do sinal.
* `ciclo_registro`: Período de amostragem da telemetria.

---

## 3. Análise Numérica e Avaliação de Erros
Para avaliar a precisão das transmissões, o sistema calcula duas métricas fundamentais de erro numérico:

1. **Erro Absoluto (MAE):**  
   Mede a variação direta em milissegundos entre o tempo previsto e o real.  
   $$\text{Erro Absoluto} = \vert{}\text{Latência Observada} - \text{Latência Prevista}\vert{}$$

2. **Erro Relativo (MRE):**  
   Avalia a proporção do erro em relação à escala de latência esperada.  
   $$\text{Erro Relativo} = \frac{\vert{}\text{Latência Observada} - \text{Latência Prevista}\vert{}}{\text{Latência Prevista}}$$

### Análise dos Resultados:
Pequenas variações ocorrem devido a oscilações térmicas e arredondamentos em ponto flutuante. Erros relativos elevados em módulos críticos (como Suporte Médico) disparam ações imediatas de reencaminhamento de tráfego.

---

## 4. Modelo Preditivo e Métricas de Performance
O SCIC implementa um modelo de **Regressão Linear** (`scikit-learn`) que treina os dados de corrente e tensão elétrica para estimar a latência futura das conexões.

### Métricas de Avaliação:
* **MAE (Erro Absoluto Médio):** Indica a média dos erros na unidade original (ms).
* **MSE (Erro Quadrático Médio):** Penaliza com maior intensidade os erros maiores.
* **RMSE (Raiz do Erro Quadrático Médio):** Retorna o erro quadrático para a escala interpretável de milissegundos.
* **$R^2$ (Coeficiente de Determinação):** Mede a proporção da variabilidade da latência explicada pelas variáveis elétricas.

---

## 5. Estruturas de Dados Avançadas

### 5.1 Priorização de Alertas com Min-Heap
* **Aplicação:** Fila de prioridade para gerenciamento de alertas.
* **Funcionamento:** O evento com o menor número de prioridade (nível 1 = crítico) fica no topo do nó principal.
* **Vantagem:** A consulta ao alerta mais urgente ocorre em tempo $O(1)$ e inserções/remoções em $O(\log n)$, superando a busca linear $O(n)$ de listas simples.

### 5.2 Busca por Prefixo com Árvore Trie
* **Aplicação:** Localização rápida de módulos e identificadores de sensores.
* **Funcionamento:** Navegação baseada em prefixos. Ao buscar `MOD`, o sistema percorre os nós da árvore e retorna os módulos correspondentes.
* **Vantagem:** O tempo de busca depende do comprimento da palavra procurada $O(k)$, mantendo alta eficiência mesmo com o aumento no volume de dados.

---

## 6. Arquitetura de Computadores e Eletricidade Básica
* **Dispositivos de Entrada e Saída:** Sensores de telemetria atuam na entrada de dados, e o terminal do VS Code/dashboard funciona como saída.
* **Bases Numéricas:** O sistema converte os códigos hexadecimais dos sensores (ex.: `0x1F3A`) para representações binárias e decimais.
* **Eletricidade Básica (Lei de Ohm):** Aplica a Primeira Lei de Ohm ($R = V / I$) para calcular a resistência operacional dos transmissores e diagnosticar riscos de sobrecarga ($P = V \times I$).

---

## 7. Gerenciamento Inteligente da Comunicação
O protótipo reflete conceitos de Redes Inteligentes (Smart Grids / IoT):
* **Monitoramento Contínuo:** Previne a perda de pacotes de dados vitais.
* **Manutenção Preditiva:** O modelo preditivo avisa sobre variações de sinal antes que o enlace caia.
* **Redundância:** Identifica pontos de gargalo e possibilita o desvio de tráfego para redes secundárias.

---

## 8. Reflexão Social, Cultural e Sustentável
1. **Sustentabilidade:** O monitoramento elétrico otimiza o consumo energético dos transmissores, evitando desperdício de energia na colônia.
2. **Conhecimentos Tradicionais e Respeito aos Recursos:** A filosofia das culturas indígenas brasileiras inspira a gestão equilibrada de recursos escassos em Marte.
3. **Supervisão Humana e Diversidade:** As previsões de Inteligência Artificial servem apenas como auxílio à decisão, mantendo a validação e responsabilidade final com a equipe humana para garantir decisões transparentes e não excludentes.

---

## 9. Limitações e Trabalhos Futuros
* **Limitações:** O sistema opera sobre simulações simplificadas de telemetria.
* **Melhorias:** Integração de modelos de regressão não-linear e desenvolvimento de uma interface web gráfica interativa.
