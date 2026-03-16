import pandas as pd
from sqlalchemy import create_engine

# %% FASE 2: INTEGRAÇÃO DE SISTEMAS (PYTHON + SQL)

# 1. Definir as credenciais de acesso
USER = 'root'
PASSWORD = '20072004' 
HOST = 'localhost'
DATABASE = 'analise_estocastica'

# 2. Criar o engine entre o Python e o MySQL
engine = create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DATABASE}")

# 3. Ir buscar os dados
query = "SELECT * FROM employee_survey"
df = pd.read_sql(query, engine)

# 4. Confirmar
print("Conexão Estabelecida com Sucesso")
print(f"Total de registos importados: {len(df)}")
print("\nPrimeiras 5 linhas do dataset:")
print(df.head())

# %% FASE 3: AUDITORIA DE QUALIDADE E SANEAMENTO
print("\n--- Fase 3: Auditoria de Dados ---")

# 1. Validação de Integridade Física (Nulos e Duplicados)
print(f"Valores nulos encontrados: {df.isnull().sum().sum()}")
print(f"Registos duplicados encontrados: {df.duplicated().sum()}")

# 2. Validação Idade vs Experiência
inconsistentes_idade = df[df['Experience'] > (df['Age'] - 14)]
print(f"Alerta: {len(inconsistentes_idade)} registos com idade/experiência incoerente.")

# 3. Validação de Hierarquia
inconsistentes_equipa = df[df['NumReports'] > df['TeamSize']]
print(f"Alerta: {len(inconsistentes_equipa)} registos com erros de hierarquia.")

# 4. Verificação de Limites (Outliers básicos)
# Verificar se os valores de sono e stress estão dentro do esperado
print("\nCheque de Sanidade (Mínimos e Máximos):")
print(df[['SleepHours', 'Stress', 'Workload']].agg(['min', 'max']))

# 5. Tratamento de Variáveis Categóricas
df['haveOT_numeric'] = df['haveOT'].map({'TRUE': 1, 'FALSE': 0})

# LIMPEZA: Se houver nulos, vamos eliminá-los (Drop) para não quebrar a simulação
df = df.dropna()

# %% FASE 4: ENGENHARIA DE INDICADORES (KPIs)
print("\n--- Fase 4: Criação de Indicadores Proprietários ---")

# Cálculo do Índice de Dívida Biológica (Bio-Debt)
# Esta fórmula mede o desgaste vs recuperação
df['BioDebt_Index'] = (df['Workload'] + df['Stress'] + (df['haveOT_numeric'] * 1.5)) / \
                      (df['SleepHours'] + (df['PhysicalActivityHours'] / 7) + 1)

# Cálculo da Fricção de Deslocação (Commute Friction)
# Criamos pesos para diferentes modos de transporte
pesos_transporte = {
    'Walk': 1.0, 
    'Bike': 1.2, 
    'Public Transport': 1.6, 
    'Motorbike': 1.7, 
    'Car': 2.0
}
df['Transport_Weight'] = df['CommuteMode'].map(pesos_transporte)
df['Commute_Friction'] = df['CommuteDistance'] * df['Transport_Weight']

print("Novos indicadores calculados com sucesso!")

# Mostrar um resumo estatístico dos novos indicadores
print("\nResumo do Perfil de Risco da Empresa:")
print(df[['BioDebt_Index', 'Commute_Friction']].describe())

# Categorização de Risco (Transformar números em etiquetas acionáveis)
# Criamos 3 níveis de risco baseados nos quartis da Dívida Biológica
df['Risk_Level'] = pd.qcut(df['BioDebt_Index'], q=3, labels=['Baixo', 'Médio', 'Elevado'])

# Validação de Relevância (Correlação)
# Queremos saber se os nossos novos índices têm relação com a satisfação (JobSatisfaction)
correlacao = df[['BioDebt_Index', 'Commute_Friction', 'JobSatisfaction']].corr()

print("\n--- Validação dos Novos Indicadores ---")
print("Correlação com a Satisfação:")
print(correlacao['JobSatisfaction'].sort_values(ascending=False))

print("\nDistribuição dos Níveis de Risco:")
print(df['Risk_Level'].value_counts(normalize=True) * 100)

# %% FASE 5: SIMULAÇÃO DE MONTE CARLO E VISUALIZAÇÃO
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("\n--- Fase 5: Simulação de Monte Carlo (10.000 iterações) ---")

# 1. Configuração da Simulação
n_simulacoes = 10000
historico_biodebt_simulado = []

# Guardamos a média atual para comparar
media_atual = df['BioDebt_Index'].mean()

# 2. Execução do Loop de Monte Carlo
for i in range(n_simulacoes):
    # Simulamos variações baseadas no cenário de Trabalho Híbrido:
    
    # Incerteza 1: Redução de Commute (entre 50% e 70% menos viagem)
    fator_reducao_commute = np.random.uniform(0.3, 0.5) 
    
    # Incerteza 2: Recuperação de Sono (ganho de 0.5 a 1.5 horas)
    ganho_sono = np.random.uniform(0.5, 1.5)
    
    # Incerteza 3: Aumento de Carga (pode subir entre 0% a 10%)
    fator_workload = np.random.uniform(1.0, 1.1)
    
    # Calculamos o novo BioDebt médio da empresa nesta "realidade alternativa"
    # Usamos a fórmula que criaste na Fase 4, mas com as novas variáveis simuladas
    novo_biodebt_media = ( (df['Workload'] * fator_workload) + df['Stress'] + (df['haveOT_numeric'] * 1.5) ) / \
                         ( (df['SleepHours'] + ganho_sono) + (df['PhysicalActivityHours'] / 7) + 1 )
    
    historico_biodebt_simulado.append(novo_biodebt_media.mean())

# 3. Cálculo de Probabilidades
media_simulada_final = np.mean(historico_biodebt_simulado)
probabilidade_sucesso = (np.array(historico_biodebt_simulado) < media_atual).mean() * 100

print(f"Simulação completa")
print(f"Dívida Biológica Atual: {media_atual:.3f}")
print(f"Dívida Biológica Preditiva (Média): {media_simulada_final:.3f}")
print(f"Probabilidade de melhoria no bem-estar: {probabilidade_sucesso:.1f}%")

# 4. Visualização dos Resultados (O gráfico para o Docs)
plt.figure(figsize=(10, 6))
sns.histplot(historico_biodebt_simulado, kde=True, color='skyblue', label='Cenário Simulado (Híbrido)')
plt.axvline(media_atual, color='red', linestyle='--', label=f'Média Atual ({media_atual:.3f})')
plt.title('Distribuição de Probabilidade: Impacto do Trabalho Híbrido no Bio-Debt')
plt.xlabel('Índice de Dívida Biológica (Média da Empresa)')
plt.ylabel('Frequência (Iterações)')
plt.legend()
plt.show()

# %% FASE 6: EXPORTAÇÃO E CONCLUSÕES FINAIS

print("\n--- Fase 6: Finalização e Exportação ---")

# 1. Guardar os novos dados (com os KPIs) de volta no SQL
try:
    df.to_sql('employee_analytics_results', engine, if_exists='replace', index=False)
    print("Sucesso: Indicadores exportados para a base de dados SQL!")
except Exception as e:
    print(f"Erro ao exportar para SQL: {e}")

# 2. Resumo para a Gestão (O "Elevator Pitch")
print("\n--- RESUMO EXECUTIVO ---")
print(f"1. Relação Stress/Satisfação: Validada (Correlação {correlacao['JobSatisfaction']['BioDebt_Index']:.2f})")
print(f"2. Eficácia do Trabalho Híbrido: {probabilidade_sucesso}% de probabilidade de sucesso.")
print(f"3. Impacto Estimado: Redução média de {((media_atual - media_simulada_final)/media_atual)*100:.1f}% na Dívida Biológica.")

print("\nPROJETO CONCLUÍDO COM SUCESSO.")