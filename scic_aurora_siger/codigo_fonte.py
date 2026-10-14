"""
===============================================================================
SISTEMA DE COMUNICAÇÃO INTERPLANETÁRIA DA COLÔNIA (SCIC)
Fase 6 - Projeto Integrador (PBL) - Missão Aurora Siger
Autor: André Victor Cunha de Souza (RM574035)
Instituição: FIAP - Faculdade de Informática e Administração Paulista
===============================================================================
"""

import os
import heapq
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class NoTrie:
    """Nó individual para a construção da árvore de prefixos (Trie)."""
    def __init__(self):
        self.filhos = {}
        self.fim_da_chave = False
        self.dados_registro = None


class TrieRegistros:
    """Estrutura Trie para consulta e busca rápida por prefixos."""
    def __init__(self):
        self.raiz = NoTrie()

    def inserir(self, chave: str, dados: dict = None):
        no = self.raiz
        for caractere in chave.upper():
            if caractere not in no.filhos:
                no.filhos[caractere] = NoTrie()
            no = no.filhos[caractere]
        no.fim_da_chave = True
        no.dados_registro = dados

    def buscar_por_prefixo(self, prefixo: str) -> list:
        no = self.raiz
        for caractere in prefixo.upper():
            if caractere not in no.filhos:
                return []
            no = no.filhos[caractere]

        resultados = []
        self._coletar_recursivo(no, prefixo.upper(), resultados)
        return resultados

    def _coletar_recursivo(self, no: NoTrie, prefixo_atual: str, resultados: list):
        if no.fim_da_chave:
            resultados.append((prefixo_atual, no.dados_registro))
        for caractere, no_filho in no.filhos.items():
            self._coletar_recursivo(no_filho, prefixo_atual + caractere, resultados)


class GerenciadorAlertasHeap:
    """Estrutura de Fila de Prioridade utilizando Min-Heap (heapq)."""
    def __init__(self):
        self.heap = []

    def adicionar_alerta(self, prioridade: int, modulo: str, mensagem: str, latencia: float):
        heapq.heappush(self.heap, (prioridade, modulo, mensagem, latencia))

    def extrair_mais_critico(self):
        if self.heap:
            return heapq.heappop(self.heap)
        return None

    def esta_vazio(self) -> bool:
        return len(self.heap) == 0


class SistemaSCIC:
    """Classe principal de gerenciamento do protótipo SCIC."""
    def __init__(self, caminho_csv: str = "dados_aurora_siger.csv"):
        self.caminho_csv = caminho_csv
        self.dataframe = None
        self.trie = TrieRegistros()
        self.heap_alertas = GerenciadorAlertasHeap()
        self.modelo_regressao = None

    def carregar_dados(self) -> bool:
        if not os.path.exists(self.caminho_csv):
            print(f"Erro: O arquivo {self.caminho_csv} nao foi encontrado no diretorio.")
            return False

        self.dataframe = pd.read_csv(self.caminho_csv)

        for _, linha in self.dataframe.iterrows():
            dados_dict = dict(linha)
            self.trie.inserir(linha['nome_modulo'], dados_dict)
            self.trie.inserir(linha['codigo_sensor_hex'], dados_dict)

            if linha['status_operacional'] in ['Alerta', 'Manutenção']:
                self.heap_alertas.adicionar_alerta(
                    prioridade=int(linha['nivel_prioridade']),
                    modulo=linha['nome_modulo'],
                    mensagem=linha['mensagem_alerta'],
                    latencia=float(linha['latencia_observada_ms'])
                )
        return True

    def analisar_erros_numericos(self):
        """Calcula Erro Absoluto e Relativo com análise de precisão de ponto flutuante."""
        if self.dataframe is None:
            print("Erro: Nenhum dado foi carregado.")
            return

        self.dataframe['potencia_w'] = self.dataframe['tensao_v'] * self.dataframe['corrente_a']
        self.dataframe['erro_absoluto_ms'] = np.abs(
            self.dataframe['latencia_observada_ms'] - self.dataframe['latencia_prevista_ms']
        )
        self.dataframe['erro_relativo_pct'] = (
            self.dataframe['erro_absoluto_ms'] / self.dataframe['latencia_observada_ms']
        ) * 100

        print("\n--- ANALISE NUMERICA E AVALIACAO DE ERROS ---")
        colunas = ['nome_modulo', 'latencia_observada_ms', 'latencia_prevista_ms', 'erro_absoluto_ms', 'erro_relativo_pct']
        print(self.dataframe[colunas].to_string(index=False))

        mae_global = self.dataframe['erro_absoluto_ms'].mean()
        mre_global = self.dataframe['erro_relativo_pct'].mean()

        print("\n[Resumo Estatistico da Base]")
        print(f"Erro Absoluto Medio (MAE da base): {mae_global:.2f} ms")
        print(f"Erro Relativo Medio (MRE da base): {mre_global:.2f}%")
        print("Nota de Precisao Computacional: A representacao em ponto flutuante obedece ao padrao IEEE 754 (float64).")

    def treinar_modelo_preditivo(self):
        """Treina e avalia modelo de Regressao Linear para estimativa de latencia."""
        if self.dataframe is None:
            print("Erro: Carregue os dados primeiro.")
            return

        X = self.dataframe[['tensao_v', 'corrente_a', 'potencia_w', 'latencia_prevista_ms']]
        y = self.dataframe['latencia_observada_ms']

        X_treino, X_teste, y_treino, y_teste = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.modelo_regressao = LinearRegression()
        self.modelo_regressao.fit(X_treino, y_treino)

        y_pred = self.modelo_regressao.predict(X_teste)

        mae = mean_absolute_error(y_teste, y_pred)
        mse = mean_squared_error(y_teste, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_teste, y_pred)

        print("\n--- MODELO PREDITIVO E METRICAS DE PERFORMANCE ---")
        print(f"Erro Absoluto Medio (MAE):       {mae:.3f} ms")
        print(f"Erro Quadratico Medio (MSE):     {mse:.3f}")
        print(f"Raiz do Erro Quadratico (RMSE):  {rmse:.3f} ms")
        print(f"Coeficiente de Determinacao (R2): {r2:.3f}")
        print("\nInterpretacao: O modelo avalia a relacao entre os parametros de alimentacao eletrica e a latencia do sinal.")

    def processar_alertas_prioritarios(self):
        """Exibe o processamento em ordem de criticidade usando o Min-Heap."""
        print("\n--- PRIORIZACAO DE ALERTAS OPERACIONAIS (MIN-HEAP) ---")
        if self.heap_alertas.esta_vazio():
            print("Nenhum alerta pendente no sistema.")
            return

        heap_temporaria = GerenciadorAlertasHeap()
        heap_temporaria.heap = list(self.heap_alertas.heap)

        print("Ordem de atendimento dos alertas (Prioridade 1 = Critica):")
        while not heap_temporaria.esta_vazio():
            prio, mod, msg, lat = heap_temporaria.extrair_mais_critico()
            print(f"[Prioridade {prio}] Modulo: {mod:<12} | Latencia: {lat:6.1f} ms | Alerta: {msg}")

    def buscar_registro_trie(self):
        """Permite a consulta por prefixo no terminal."""
        prefixo = input("\nDigite o prefixo do Modulo ou Codigo do Sensor (ex: MOD, 0x1F, 0x4F): ").strip()
        resultados = self.trie.buscar_por_prefixo(prefixo)

        print(f"\n--- BUSCA POR PREFIXO '{prefixo.upper()}' (TRIE) ---")
        if not resultados:
            print("Nenhum registro encontrado para o prefixo informado.")
            return

        for chave, dados in resultados:
            print(f"Chave: {chave:<12} | Modulo: {dados['nome_modulo']} | Status: {dados['status_operacional']} | Cod. Sensor: {dados['codigo_sensor_hex']}")

    def demonstrar_arquitetura_e_eletricidade(self):
        """Exibe conversões de base e aplicação de Lei de Ohm e Potência."""
        print("\n--- ORGANIZACAO DE COMPUTADORES E ELETRICIDADE BASICA ---")
        print("1. Conversao de Bases Numericas (Identificadores de Hardware):")
        for _, linha in self.dataframe.head(3).iterrows():
            code_hex = linha['codigo_sensor_hex']
            val_dec = int(code_hex, 16)
            val_bin = bin(val_dec)
            print(f"   Hexadecimal: {code_hex} -> Decimal: {val_dec:5d} -> Binario: {val_bin}")

        print("\n2. Eletricidade Basica Aplicada aos Radiotransmissores:")
        for _, linha in self.dataframe.head(3).iterrows():
            v = linha['tensao_v']
            i = linha['corrente_a']
            p = v * i
            r = v / i if i > 0 else 0
            print(f"   {linha['nome_modulo']}: Tensao = {v}V | Corrente = {i}A -> Potencia = {p:.1f}W | Resistencia = {r:.2f} Ohms")


def menu_principal():
    sistema = SistemaSCIC()
    if not sistema.carregar_dados():
        return

    while True:
        print("\n=================================================================")
        print("    SISTEMA DE COMUNICAÇÃO INTERPLANETÁRIA DA COLÔNIA (SCIC)    ")
        print("                   COLÔNIA AURORA SIGER - MARTE                  ")
        print("=================================================================")
        print("1. Analise Numerica e Avaliacao de Erros (MAE/MRE)")
        print("2. Treinamento e Avaliacao de Modelo Preditivo (ML)")
        print("3. Processamento de Alertas Prioritarios (Min-Heap)")
        print("4. Busca de Registros por Prefixo (Trie)")
        print("5. Diagnostico de Arquitetura e Eletricidade Basica")
        print("0. Sair")
        print("=================================================================")
        opcao = input("Selecione uma opcao [0-5]: ").strip()

        if opcao == "1":
            sistema.analisar_erros_numericos()
        elif opcao == "2":
            sistema.treinar_modelo_preditivo()
        elif opcao == "3":
            sistema.processar_alertas_prioritarios()
        elif opcao == "4":
            sistema.buscar_registro_trie()
        elif opcao == "5":
            sistema.demonstrar_arquitetura_e_eletricidade()
        elif opcao == "0":
            print("\nEncerrando o sistema SCIC. Conexao com a Colônia mantida.")
            break
        else:
            print("\nOpcao invalida. Tente novamente.")


if __name__ == "__main__":
    menu_principal()