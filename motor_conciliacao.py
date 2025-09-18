import pandas as pd
import re
from io import BytesIO

def extrair_referencia(texto):
    texto = texto.upper()
    match_dup = re.search(r'DUP[\s.:#-]*([A-Z0-9]+)', texto)
    match_nf = re.search(r'NF[\s.:#-]*([0-9]+)', texto)
    if match_dup:
        return 'Duplicata', match_dup.group(1)
    elif match_nf:
        return 'Nota', match_nf.group(1)
    return '', ''

def extrair_fornecedor(texto):
    texto = texto.upper()
    match = re.search(r'FORNECEDOR[:\s\-]*([A-Z0-9 ]+)', texto)
    return match.group(1).strip() if match else texto.strip()

def conciliar_lancamentos(file):
    buffer = BytesIO(file.read())
    df = pd.read_excel(buffer, header=7)

    df['Débito'] = pd.to_numeric(df['Débito'], errors='coerce').fillna(0)
    df['Crédito'] = pd.to_numeric(df['Crédito'], errors='coerce').fillna(0)
    df['Histórico'] = df['Histórico'].astype(str)
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
    df['Valor'] = df['Débito'] + df['Crédito']
    df['Tipo'] = df['Crédito'].apply(lambda x: 'Pagamento' if x > 0 else 'Entrada')
    df['Fornecedor'] = df['Histórico'].apply(extrair_fornecedor)
    df[['RefTipo', 'RefNum']] = df['Histórico'].apply(lambda x: pd.Series(extrair_referencia(x)))

    notas = df[(df['Tipo'] == 'Entrada') & (df['Valor'] > 0) & df['Data'].notnull()]
    pagamentos = df[(df['Tipo'] == 'Pagamento') & (df['Valor'] > 0) & df['Data'].notnull()]

    relacionamentos = []
    for _, pag in pagamentos.iterrows():
        candidatos = notas[
            (abs(notas['Valor'] - pag['Valor']) <= 1) &
            (notas['Fornecedor'].str.lower().str.contains(pag['Fornecedor'].lower(), na=False))
        ].copy()

        if candidatos.empty:
            candidatos = notas[(abs(notas['Valor'] - pag['Valor']) <= 1)].copy()

        candidatos['DeltaData'] = abs((candidatos['Data'] - pag['Data']).dt.days)
        candidatos = candidatos.sort_values(by='DeltaData')

        if not candidatos.empty:
            nota = candidatos.iloc[0]
            diff = abs(pag['Valor'] - nota['Valor'])
            confiabilidade = 'Alta' if diff == 0 else 'Média'
            conciliado = 'Sim' if diff == 0 else 'Não'
            relacionamentos.append({
                'Valor Pago': round(pag['Valor'], 2),
                'Data Pagamento': pag['Data'].strftime('%d/%m/%Y'),
                'Histórico Pagamento': pag['Histórico'],
                'Valor NF': round(nota['Valor'], 2),
                'Data NF': nota['Data'].strftime('%d/%m/%Y'),
                'Histórico NF': nota['Histórico'],
                'Fornecedor': nota['Fornecedor'],
                'Diferença': round(diff, 2),
                'Confiabilidade': confiabilidade,
                'Conciliado': conciliado
            })

    return pd.DataFrame(relacionamentos)
