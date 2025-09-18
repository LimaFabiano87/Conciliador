import pandas as pd
import re
from io import BytesIO

def conciliar_lancamentos(file):
    buffer = BytesIO(file.read())
    df = pd.read_excel(buffer, header=7)

    df['Débito'] = pd.to_numeric(df['Débito'], errors='coerce').fillna(0)
    df['Crédito'] = pd.to_numeric(df['Crédito'], errors='coerce').fillna(0)
    df['Histórico'] = df['Histórico'].astype(str)
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
    df['Valor'] = df['Débito'] + df['Crédito']
    df['Tipo'] = df['Crédito'].apply(lambda x: 'Pagamento' if x > 0 else 'Entrada')

    def extrair_referencia(texto):
        texto = texto.upper()
        match_dup = re.search(r'DUP[\s.:#-]*([A-Z0-9]+)', texto)
        match_nf = re.search(r'NF[\s.:#-]*([0-9]+)', texto)
        if match_dup:
            return 'Duplicata', match_dup.group(1)
        elif match_nf:
            return 'Nota', match_nf.group(1)
        return '', ''

    df[['RefTipo', 'RefNum']] = df['Histórico'].apply(lambda x: pd.Series(extrair_referencia(x)))
    notas = df[(df['Tipo'] == 'Entrada') & (df['Valor'] > 0) & df['Data'].notnull()]
    pagamentos = df[(df['Tipo'] == 'Pagamento') & (df['Valor'] > 0) & df['Data'].notnull()]

    relacionamentos = []
    for _, pag in pagamentos.iterrows():
        candidatos = notas[(abs(notas['Valor'] - pag['Valor']) <= 1)]
        for _, nota in candidatos.iterrows():
            diff = abs(pag['Valor'] - nota['Valor'])
            confiabilidade = 'Alta' if diff == 0 else 'Média'
            relacionamentos.append({
                'Valor Pago': round(pag['Valor'], 2),
                'Data Pagamento': pag['Data'].date(),
                'Texto Pagamento': pag['Histórico'],
                'Valor NF': round(nota['Valor'], 2),
                'Data NF': nota['Data'].date(),
                'Texto NF': nota['Histórico'],
                'Diferença': round(diff, 2),
                'Confiabilidade': confiabilidade
            })

    return pd.DataFrame(relacionamentos)


