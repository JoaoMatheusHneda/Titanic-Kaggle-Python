import os
import numpy as np
import pandas as pd
import sklearn as sl #sl.__version__
from plotnine import *

#############
# METADADOS #
#############

def tabela_metadados(tabela_de_entrada,sufixo_da_tabela_saída,lista_vars_drop):
    
    print('___________________________________________________________________')
    print("O shape da tabela de entrada é: ") 
    print(tabela_de_entrada.shape)

    # Nome das colunas
    metadata_table = pd.DataFrame(tabela_de_entrada.columns)
    metadata_table = metadata_table.rename(columns={0:'columns'})
    
    # Tipo do dado de cada coluna
    metadata_table['dtypes'] = tabela_de_entrada.dtypes.values

    # Número de valores únicos (Cardinalidade)
    metadata_table['nunique'] = tabela_de_entrada.nunique().values
    
    # Número de valores nulos e Porcentagem de valores nulos
    metadata_table['null_value_count'] = tabela_de_entrada.isnull().sum().values
    metadata_table['p_null_value_count'] = (tabela_de_entrada.isnull().sum()/tabela_de_entrada.shape[0]).values
    
    # Porcentagem de valores repetidos da moda em relação aos valores não nulos
    metadata_table['p_max_duplicated_value'] = np.NaN
    for j in range(0,tabela_de_entrada.shape[1]):
        lista = list(tabela_de_entrada.iloc[:,j]) # Transforma a coluna em uma lista
        moda = max(lista,key=lista.count) # Encontra a moda
        maximo_percentage = tabela_de_entrada[tabela_de_entrada.iloc[:,j]==moda].shape[0]/tabela_de_entrada.count()[j]
        metadata_table.loc[j,'p_max_duplicated_value'] = maximo_percentage
    
     # Número de valores únicos (Cardinalidade) (+ 1 se tiver valor nulo)
    metadata_table['nunique_with_null'] = tabela_de_entrada.nunique().values
    nunique_with_null_aux = metadata_table.loc[metadata_table['null_value_count'] > 0].nunique_with_null + 1
    metadata_table.loc[nunique_with_null_aux.index,'nunique_with_null'] = nunique_with_null_aux.values
    
    # Reorganiza a ordem das colunas
    metadata_table = metadata_table[['columns','dtypes','nunique','nunique_with_null','null_value_count','p_null_value_count','p_max_duplicated_value']]
    
    metadata_table['drop'] = metadata_table['columns'].isin(lista_vars_drop)

    # Salva a tabela na memória
    globals()['metadata_table_' + sufixo_da_tabela_saída] = metadata_table
    print('Tabela ' + 'metadata_table_' + sufixo_da_tabela_saída + ' criada!')
    return globals()['metadata_table_' + sufixo_da_tabela_saída]

######################
# ANÁLISE UNIVARIADA #
######################

##### Distribuição de Frequências (Variável Qualitativa)

def calcula_tab_frequencia(tabela_de_entrada,nome_variavel):
    
    globals()['table_count_prop' + nome_variavel] = pd.DataFrame(tabela_de_entrada[nome_variavel].value_counts(sort=False))
    globals()['table_count_prop' + nome_variavel][nome_variavel+'_P'] = round((globals()['table_count_prop' + nome_variavel][nome_variavel]/globals()['table_count_prop' + nome_variavel][nome_variavel].sum())*100,2)
    globals()['table_count_prop' + nome_variavel].reset_index(inplace=True)
    globals()['table_count_prop' + nome_variavel] = globals()['table_count_prop' + nome_variavel].sort_values(by='index',ascending=False)
    print('Tabela ' + 'table_count_prop' + nome_variavel + ' criada!')
    return globals()['table_count_prop' + nome_variavel]

def grafico_tab_frequencia(tabela_de_entrada,nome_variavel,cor_grafico,nudge_x_e,nudge_x_d,nudge_y):

    globals()['gg_count_prop' + nome_variavel] = ggplot(aes(x='index',y=nome_variavel),data=globals()['table_count_prop' + nome_variavel]) + \
                                                        geom_col(fill=cor_grafico) + \
                                                        geom_text(aes(label=nome_variavel),                                   
                                                                va='bottom',nudge_x = nudge_x_e, nudge_y = nudge_y, 
                                                                size=12, format_string='{} ') + \
                                                        geom_text(aes(label=nome_variavel+'_P'),                                 
                                                                va='bottom',nudge_x = nudge_x_d, nudge_y = nudge_y, 
                                                                size=12, format_string='({}%)')
    print('Gráfico ' + 'gg_count_prop' + nome_variavel + ' criado!')
    return globals()['gg_count_prop' + nome_variavel]


def grafico_tab_frequencia2(tabela_de_entrada,nome_variavel,cor_grafico,size=12):
    globals()['gg_count_prop' + nome_variavel] = ggplot(aes(x='index',y=nome_variavel),data=globals()['table_count_prop' + nome_variavel]) + \
                                                        geom_col(fill=cor_grafico) + theme(axis_text_x=element_text(angle=45)) + \
                                                        geom_text(aes(label=nome_variavel+'_P'),                                 
                                                                va='bottom',size=size, format_string='{}%')
    print('Gráfico ' + 'gg_count_prop' + nome_variavel + ' criado!')
    return globals()['gg_count_prop' + nome_variavel]



##### Distribuição de Frequências (Variável Quantitativa)

# Cálculo do número de categorias (Sturges)
def calcula_num_categorias(n):
    global k
    k = int(round(1 + 3.322 * np.log10(n), 0))
    return (n,k)

# Definindo os intervalos de um histograma
def binning_quantities(dados_entrada,dados_aplicacao_saida,nome_variavel):
    #global dados_saida

    # dados_entrada # Dados para calculo dos intervalos
    #dados_entrada = df[df.Sample == 'train']['variavel']

    interval = pd.cut(dados_entrada, k, include_lowest=True,retbins=True)

    # Inclui os valores np.-inf e np.inf nos intervalos
    interval = interval[1] # limites
    interval = interval[1:interval.shape[0]-1]
    limites_intervalos = list([-np.Inf] + list(interval) + [np.Inf])
    limites_intervalos = [round(i,2) for i in limites_intervalos]
    bins = pd.IntervalIndex.from_breaks(limites_intervalos)
    #bins

    #-------------------------------------------------------------------------

    # dados_aplicacao_saida # Dados que serão utilizados para a aplicação dos intervalos calculados
    #dados_aplicacao_saida = df['variavel']

    # dados_saida # Dados alterados com a aplicação dos intervalos calculados
    dados_saida =  pd.cut(dados_aplicacao_saida, bins) # Faz a aplicação de acordo com os intervalos calculados

    # # Adicionando a categoria Missing aos intervalos
    dados_saida = dados_saida.cat.add_categories(['Missing'])

    # # Reorganizando os intervalos
    categorias = list(dados_saida.cat.categories.values)
    categorias_missing = [dados_saida.cat.categories.values[-1]]
    categorias_missing.extend(list(dados_saida.cat.categories.values[:-1]))

    # dados_saida = dados_saida.cat.reorder_categories(categorias_missing)

    # # # Substitui os valores nulos por 'Missing'
    dados_saida = dados_saida.fillna('Missing')
    print(dados_saida)

    print('--------------------------------------------------------------------------------------------------')
    dados_saida = pd.DataFrame(dados_saida)
    print(dados_saida.dtypes)
    
    print('-------------------------------------------------')
    print('Tabela dados_saida' + nome_variavel + ' criada!')

    globals()['dados_saida' + nome_variavel] = dados_saida
    return globals()['dados_saida' + nome_variavel]

