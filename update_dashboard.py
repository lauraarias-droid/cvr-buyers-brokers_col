import requests
import re
import csv
import io

# ID del Google Sheet
SHEET_ID = '1mtnoNs_Hn1A0xbdsaFiBBN_ESXEoQT_9-mWPKmYAM6c'
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1'

# Leer datos del Sheet
response = requests.get(SHEET_URL)
response.encoding = 'utf-8'

reader = csv.DictReader(io.StringIO(response.text))
rows = list(reader)

print("Headers encontrados:", rows[0].keys() if rows else "Sin datos")
print("Primera fila:", rows[0] if rows else "Sin datos")

# Limpiar headers (quitar espacios y BOM)
clean_rows = []
for row in rows:
    clean_row = {k.strip().lstrip('\ufeff'): v.strip() for k, v in row.items()}
    clean_rows.append(clean_row)

rows = clean_rows
print("Headers limpios:", rows[0].keys() if rows else "Sin datos")

# Organizar datos por mes
data_by_mes = {}
for row in rows:
    mes_raw = row['mes'][:7]  # 2026-05
    mes_parts = mes_raw.split('-')
    meses = {'01':'ene','02':'feb','03':'mar','04':'abr','05':'may','06':'jun',
             '07':'jul','08':'ago','09':'sep','10':'oct','11':'nov','12':'dic'}
    mes = meses[mes_parts[1]] + '-' + mes_parts[0][2:]
    
    producto = row['producto'].strip()
    if mes not in data_by_mes:
        data_by_mes[mes] = {}
    data_by_mes[mes][producto] = row

# Ordenar meses cronológicamente
orden_meses = {'ene':1,'feb':2,'mar':3,'abr':4,'may':5,'jun':6,
               'jul':7,'ago':8,'sep':9,'oct':10,'nov':11,'dic':12}
meses_ordenados = sorted(data_by_mes.keys(),
    key=lambda x: (int('20'+x.split('-')[1]), orden_meses[x.split('-')[0]]))

# Construir array DATA
data_lines = []
for mes in meses_ordenados:
    d = data_by_mes[mes]
    ib = d.get('ibuyer', {})
    in_ = d.get('inmo', {})
    
    line = (f"  {{mes:'{mes}',"
            f"ib_vo:{ib.get('cvr_visita_oferta','0')},"
            f"ib_oc:{ib.get('cvr_oferta_cierre','0')},"
            f"ib_vc:{ib.get('cvr_visita_cierre','0')},"
            f"in_vo:{in_.get('cvr_visita_oferta','0')},"
            f"in_oc:{in_.get('cvr_oferta_cierre','0')},"
            f"in_vc:{in_.get('cvr_visita_cierre','0')},"
            f"ib_vis:{ib.get('visitas','0')},"
            f"ib_ofe:{ib.get('ofertas','0')},"
            f"ib_cie:{ib.get('cierres','0')},"
            f"in_vis:{in_.get('visitas','0')},"
            f"in_ofe:{in_.get('ofertas','0')},"
            f"in_cie:{in_.get('cierres','0')}}},")
    data_lines.append(line)

new_data = '\n'.join(data_lines)

# Leer cvrs.html
with open('cvrs.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar el array DATA
new_content = re.sub(
    r'const DATA = \[.*?\];',
    f'const DATA = [\n{new_data}\n];',
    content,
    flags=re.DOTALL
)

# Guardar
with open('cvrs.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Dashboard actualizado correctamente')
