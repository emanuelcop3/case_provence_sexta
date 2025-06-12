from flask import Flask, render_template, request, jsonify
from lxml import etree
from datetime import datetime
import pandas as pd
import json
from typing import List, Dict, Any

app = Flask(__name__)

def parse_anbima_xml(xml_content: str) -> Dict[str, Any]:
    try:
        # Parse XML
        root = etree.fromstring(xml_content)
        
        # Extract header information
        header = root.find('.//header')
        fund_info = {
            'codigo': header.find('codigo').text,
            'nome': header.find('nome').text,
            'data': header.find('dtposicao').text,
            'pl': float(header.find('patliq').text),
            'valorativos': float(header.find('valorativos').text),
            'valorreceber': float(header.find('valorreceber').text),
            'valorpagar': float(header.find('valorpagar').text)
        }
        
        # Extract positions
        positions = []
        
        # Process public bonds (títulos públicos)
        for titulo in root.findall('.//titpublico'):
            pos = {
                'tipo': 'Renda Fixa',
                'subtipo': titulo.find('cusip').text,
                'isin': titulo.find('isin').text,
                'quantidade': float(titulo.find('qtdisponivel').text),
                'valor_unitario': float(titulo.find('puposicao').text),
                'valor_total': float(titulo.find('valorfindisp').text),
                'data_vencimento': titulo.find('dtvencimento').text
            }
            positions.append(pos)
        
        # Process fund shares (cotas)
        for cota in root.findall('.//cotas'):
            pos = {
                'tipo': 'Fundo',
                'subtipo': 'Fundo de Investimento',
                'isin': cota.find('isin').text,
                'quantidade': float(cota.find('qtdisponivel').text),
                'valor_unitario': float(cota.find('puposicao').text),
                'valor_total': float(cota.find('qtdisponivel').text) * float(cota.find('puposicao').text),
                'data_vencimento': None
            }
            positions.append(pos)
        
        # Process provisions
        provisions = []
        for prov in root.findall('.//provisao'):
            prov_data = {
                'codigo': prov.find('codprov').text,
                'tipo': 'Crédito' if prov.find('credeb').text == 'C' else 'Débito',
                'data': prov.find('dt').text,
                'valor': float(prov.find('valor').text)
            }
            provisions.append(prov_data)
        
        # Calculate totals
        total_provisions = sum(p['valor'] for p in provisions if p['tipo'] == 'Crédito') - \
                         sum(p['valor'] for p in provisions if p['tipo'] == 'Débito')
        
        total_assets = sum(p['valor_total'] for p in positions)
        pl_difference = abs((total_assets + total_provisions) - fund_info['pl'])
        
        # Calculate position percentages
        for pos in positions:
            pos['percentual'] = (pos['valor_total'] / total_assets) * 100
        
        # Group by type
        type_summary = []
        type_totals = {}
        for pos in positions:
            tipo = pos['tipo']
            if tipo not in type_totals:
                type_totals[tipo] = 0
            type_totals[tipo] += pos['valor_total']
        
        for tipo, total in type_totals.items():
            type_summary.append({
                'tipo': tipo,
                'percentual': (total / total_assets) * 100
            })
        
        # Validate data
        validations = validate_data(fund_info, positions, provisions, total_assets, total_provisions)
        
        return {
            'fund': {
                'codigo': fund_info['codigo'],
                'nome': fund_info['nome'],
                'data': fund_info['data'],
                'pl': fund_info['pl']
            },
            'validations': validations,
            'typeSummary': type_summary,
            'positions': positions,
            'provisions': provisions,
            'total_provisions': total_provisions,
            'total_assets': total_assets,
            'pl_difference': pl_difference
        }
    except Exception as e:
        raise Exception(f"Erro ao processar XML: {str(e)}")

def validate_data(fund_info: Dict[str, Any], positions: List[Dict[str, Any]], 
                 provisions: List[Dict[str, Any]], total_assets: float, 
                 total_provisions: float) -> List[Dict[str, Any]]:
    validations = []
    
    # Validate dates
    try:
        datetime.strptime(fund_info['data'], '%Y%m%d')
    except:
        validations.append({
            'status': 'error',
            'message': 'Data de posição inválida',
            'details': f"Data informada: {fund_info['data']}"
        })
    
    # Validate PL difference
    pl_difference = abs((total_assets + total_provisions) - fund_info['pl'])
    if pl_difference > 0.01:
        validations.append({
            'status': 'error',
            'message': 'Diferença entre valor total das posições + provisões e PL',
            'details': f"Diferença: R$ {pl_difference:.2f}"
        })
    elif pl_difference > 0.001:
        validations.append({
            'status': 'warning',
            'message': 'Pequena diferença entre valor total das posições + provisões e PL',
            'details': f"Diferença: R$ {pl_difference:.2f}"
        })
    
    # Validate percentages sum to 100%
    total_percentage = sum(p['percentual'] for p in positions)
    if abs(total_percentage - 100) > 0.01:
        validations.append({
            'status': 'error',
            'message': 'Percentuais não somam 100%',
            'details': f"Total: {total_percentage:.2f}%"
        })
    
    # Validate missing dates
    missing_dates = [p for p in positions if p.get('data_vencimento') is None]
    if missing_dates:
        validations.append({
            'status': 'warning',
            'message': 'Posições com data de vencimento ausente',
            'details': f"Total de posições: {len(missing_dates)}"
        })
    
    # If no validations failed, add success message
    if not any(v['status'] == 'error' for v in validations):
        validations.append({
            'status': 'success',
            'message': 'Validação bem-sucedida',
            'details': 'Todos os dados foram validados com sucesso'
        })
    
    return validations

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if not file.filename.endswith('.xml'):
        return jsonify({'error': 'Arquivo deve ser XML'}), 400
    
    try:
        xml_content = file.read().decode('utf-8')
        result = parse_anbima_xml(xml_content)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True) 