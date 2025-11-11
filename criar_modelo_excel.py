"""
Script para criar arquivo Excel modelo para upload no sistema
"""

import pandas as pd
import os

def criar_modelo_excel():
    """
    Cria um arquivo Excel modelo com a estrutura necessária para o sistema
    """
    
    # Criar arquivo Excel com múltiplas abas
    output_file = "MODELO_TABELA_FRETE.xlsx"
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        
        # ==================== ABA DE ZONAS ====================
        # Aba: zones priority (exemplo)
        df_zonas_priority = pd.DataFrame({
            'Country/Territory': ['Portugal', 'Spain', 'France', 'Germany', 'United States', 'Brazil', 'China', 'Australia'],
            'ISO2': ['PT', 'ES', 'FR', 'DE', 'US', 'BR', 'CN', 'AU'],
            'Zona_Letra': ['A', 'A', 'B', 'B', 'C', 'D', 'E', 'F']
        })
        df_zonas_priority.to_excel(writer, sheet_name='zones priority ', index=False, startrow=1)
        
        # Aba: zones economy (exemplo)
        df_zonas_economy = pd.DataFrame({
            'Country/Territory': ['Portugal', 'Spain', 'France', 'Germany', 'United States', 'Brazil', 'China', 'Australia'],
            'ISO2': ['PT', 'ES', 'FR', 'DE', 'US', 'BR', 'CN', 'AU'],
            'Zona_Letra': ['A', 'A', 'B', 'B', 'C', 'D', 'E', 'F']
        })
        df_zonas_economy.to_excel(writer, sheet_name='zones economy', index=False, startrow=1)
        
        # Aba: zones cp (exemplo)
        df_zonas_cp = pd.DataFrame({
            'Country/Territory': ['Portugal', 'Spain', 'France', 'Germany', 'United States', 'Brazil', 'China', 'Australia'],
            'ISO2': ['PT', 'ES', 'FR', 'DE', 'US', 'BR', 'CN', 'AU'],
            'Zona_Letra': ['A', 'A', 'B', 'B', 'C', 'D', 'E', 'F']
        })
        df_zonas_cp.to_excel(writer, sheet_name='zones cp', index=False, startrow=1)
        
        # ==================== ABAS DE PREÇOS ====================
        # Criar estrutura de preços para Priority (exemplo)
        # Linha 1: vazio
        # Linha 2: Weight | Zone(s) | vazio | A | B | C | D | E | F
        # Linha 3: Envelope (peso fixo)
        # Linha 4+: Pak e Package com pesos
        
        # Criando dados de exemplo para a aba Priority
        dados_priority = {
            'Col_A': ['', 'Weight', 'Envelope', 'Pak'] + list(range(1, 21)),
            'Col_B': ['', 'Zone(s)', '', ''] + [''] * 20,
            'Col_C': ['', '', '', ''] + [''] * 20,
            'A': ['', 'Kgs', 10.50, 15.00] + [20 + i*2 for i in range(20)],
            'B': ['', '', 12.00, 17.00] + [22 + i*2.2 for i in range(20)],
            'C': ['', '', 14.00, 19.00] + [25 + i*2.5 for i in range(20)],
            'D': ['', '', 16.00, 21.00] + [28 + i*2.8 for i in range(20)],
            'E': ['', '', 18.00, 23.00] + [32 + i*3.2 for i in range(20)],
            'F': ['', '', 20.00, 25.00] + [35 + i*3.5 for i in range(20)]
        }
        
        # Adicionar tipo Package após Pak
        dados_priority['Col_A'][3] = 'Package'
        dados_priority['Col_A'][4] = 0.5
        
        df_priority = pd.DataFrame(dados_priority)
        df_priority.to_excel(writer, sheet_name='Priority', index=False, header=False)
        
        # Criar aba Economy (similar)
        df_economy = pd.DataFrame(dados_priority)
        df_economy.to_excel(writer, sheet_name='Economy', index=False, header=False)
        
        # Criar aba CP (similar)
        df_cp = pd.DataFrame(dados_priority)
        df_cp.to_excel(writer, sheet_name='CP', index=False, header=False)
        
        # ==================== INSTRUÇÕES ====================
        # Criar aba com instruções
        instrucoes = pd.DataFrame({
            'INSTRUÇÕES PARA USO DO MODELO': [
                '',
                '1. ABAS DE ZONAS:',
                '   - Devem conter: Country/Territory, ISO2, Zona_Letra',
                '   - Nomes das abas: "zones priority ", "zones economy", "zones cp"',
                '   - Para DHL: "zonas dhl"',
                '   - Para UPS: "zones express", "zones standard"',
                '',
                '2. ABAS DE PREÇOS:',
                '   - Linha 1: Vazia ou título',
                '   - Linha 2: Weight | Zone(s) | vazio | A | B | C | D | E | F...',
                '   - Linha 3: Envelope com preços por zona',
                '   - Linha 4: Pak com preços por zona',
                '   - Linha 5+: Package com peso (0.5, 1, 2, 3...) e preços',
                '',
                '3. REGRAS INCREMENTAIS (OPCIONAL):',
                '   - Após a tabela principal, adicionar nova seção "Weight"',
                '   - Formato: peso_inicial - peso_final | valores por zona',
                '   - Exemplo: 21 - 44 | 2.50 | 3.00 | 3.50',
                '',
                '4. NOMENCLATURA DAS ABAS:',
                '   - FedEx: Priority, Economy, CP',
                '   - UPS: Express, Standard',
                '   - DHL: dhl',
                '   - Outras: Configure conforme necessário',
                '',
                '5. IMPORTANTE:',
                '   - Os preços devem estar em formato numérico',
                '   - Use vírgula ou ponto para decimais',
                '   - As zonas (A, B, C...) devem corresponder às zonas nas abas de zonas',
                '   - Certifique-se de que não há linhas vazias entre os dados',
                '',
                'Para mais informações, consulte o arquivo INSTRUCOES.md'
            ]
        })
        instrucoes.to_excel(writer, sheet_name='INSTRUÇÕES', index=False)
    
    print(f"[OK] Arquivo modelo criado: {output_file}")
    return output_file

if __name__ == "__main__":
    criar_modelo_excel()

