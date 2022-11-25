import pandas as pd
import numpy as np
from pathlib import Path
import decimal
ctx = decimal.Context()

# prec - precision - количество значащих знаков, не округление до знака
def float_to_str(f, prec = 18): # 18 знаков хватит всем (c) BG
    ctx.prec = prec
    d1 = ctx.create_decimal(repr(f))
    return format(d1, 'f')

pd.set_option('display.max_columns', None)
df = pd.read_csv('ds.csv')
df=df.drop(columns=["ДлинаЕд.1", "ШиринаЕд.1", "ВысотаЕд.1", "ВсегоТовара", "НаВитрине", "Транзит.1"])
df['Цена'] = df['Цена'].replace(np.nan, 0)

df=df[df["ЧастотаПродаж"]>=0.012]

df=df.rename(columns={"Остаток" : "ВсегоТовара", "Количество": "НаВитрине"})
df=df.reset_index()
query = df.groupby('КодКатегории')['Цена'].mean()

meanWidth = df.groupby('КодКатегории')['ШиринаЕд'].mean()
meanHeight = df.groupby('КодКатегории')['ВысотаЕд'].mean()
meanLength = df.groupby('КодКатегории')['ДлинаЕд'].mean()

df['ВсегоТовара'] = df['ВсегоТовара'].replace(np.nan, 0)
df['Транзит'] = df['Транзит'].replace(np.nan, 0)
df=df[(df["Транзит"]>0) | ((df["ВсегоТовара"]>0))]
df = df.reset_index()

df["Объём"]=0.0
df["Площадь"]=0.0
df["Дельта"]=df["Цена"]
df["СреднееПоКатегории"]=df["Цена"]

for i in range(len(df)):
    if not pd.isna(df['ШиринаЕд'].values[i]):
        width = df['ШиринаЕд'].values[i]
    else:
        width = meanWidth[df['КодКатегории'].values[i]]

    if not pd.isna(df['ВысотаЕд'].values[i]):
        height = df['ВысотаЕд'].values[i]
    else:
        height = meanHeight[df['КодКатегории'].values[i]]

    if not pd.isna(df['ДлинаЕд'].values[i]):
        length = df['ДлинаЕд'].values[i]
    else:
        length = meanLength[df['КодКатегории'].values[i]]

    print(i)
    if (pd.isna(width) or pd.isna(height) or pd.isna(length)):
        df['Объём'].values[i]=0
        df['Площадь'].values[i]=0
    else:
        df['Объём'].values[i] = width * height * length
        df['Площадь'].values[i] = width * height * 2 + width * length * 2 + height*length*2
    df['Дельта'].values[i] = df['Цена'].values[i] - query[df['КодКатегории'].values[i]]
    df['СреднееПоКатегории'].values[i] = query[df['КодКатегории'].values[i]]
print(df)

filepath = Path('folder/subfolder/out.csv')
filepath.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(filepath)