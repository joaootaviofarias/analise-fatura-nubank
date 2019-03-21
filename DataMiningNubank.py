import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import numpy as np
import os
from sqlalchemy import create_engine 
from matplotlib.pyplot import figure

# define tamanho do gráfico
figure(num=None, figsize=(12, 10), dpi=1000, facecolor='w', edgecolor='k')

# conexões com o banco de dados 
engine = create_engine('postgresql://user:pass@host:5432/database')
conn = psycopg2.connect(host='host', database='database', user='user', password='pass')
cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

# lê o nome dos arquivos na pasta
fileName = os.listdir("Caminho da pasta das Faturas")

# Lê os arquivos csv e salva em uma lista
nubank = []
for i in fileName:
    nubank.append(pd.read_csv("Caminho da pasta das Faturas"+i))

# Tira as colunas que nao são interessantes para a análise
nubankL = []
for j in range(len(fileName)):
    nubankL.append(nubank[j].drop(nubank[j].columns[[0,2]], 1))

# Tira a linha com o valor do pagamento e salva no banco a tabela
nubankSemP = []
for j in range(len(fileName)):
    temp = nubankL[j]
    temp = temp[temp.category != "Pagamento"]
    nubankSemP.append(temp)
    temp.to_sql(fileName[j], engine)
    
# Faz select no banco de dados e gera um dictionary com os dados
ans2 = []
date = []
for file in fileName:
    fileDate = file.split("-")
    year = fileDate[1]
    temp = fileDate[2].split(".")
    month = temp[0]
    query = 'SELECT category ,SUM(amount) AS Totalamount FROM "'+year+'-'+month+'" GROUP BY category'
    cur.execute(query)
    result = cur.fetchall()
    ans1 = {}
    dateStr = month+"/"+year
    date.append(dateStr)
    for row in result:
        ans1.update({row[0]:row[1]})
    ans2.append(ans1)

# Cria um dataframe com os dados selecionados para gerar o gráfico    
df = pd.DataFrame.from_dict(ans2, orient='columns')
df['x'] = pd.Series(date, index=df.index)
df = df.drop('Ajuste', 1)
df = df.fillna(0)
col = list(df.columns.values)
del col[-1]

# Gera um gráfico de linha com os valores das categorias por mes
for c in col:
    plt.plot( 'x', c, data=df, marker='o', color=np.random.rand(3,), linewidth=2)
    plt.xticks(rotation=90)
    plt.legend()
    plt.show()

# Gera um gráfico de barras com o valor total gasto por categoria
total = []
color= []
for c in col:
    total.append(df[c].sum())
    color.append(np.random.rand(3,))
y_pos = np.arange(len(col))
plt.bar(y_pos, total, color=color)
plt.xticks(y_pos, col)
plt.xticks(rotation=90)
plt.show()




