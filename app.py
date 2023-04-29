from pathlib import Path

import streamlit as st
from streamlit.elements import utils

from fuel_controller import (DATE_END, DATE_START, date_input_field,
                             multiselect_fuels, multiselect_regions,
                             selectbox_counties, selectbox_flags,
                             selectbox_resales, selectbox_states)
from fuel_data import BASE_DIR, FuelData

# Constantes
ABOUT_MSG = '''
## Projeto Integrador em Computação IV

***Título:***
* *Análise comparativa da relação Custo x Benefício do Etanol nos postos de
combustíveis brasileiros.*

***Grupo:***
* *LORENA-PJI410-SALA-001GRUPO-001*

***Integrantes:***
* *Elcio Tsutomu Mashiba, RA 2001444;*
* *Leilane Dos Santos, RA 2001968;*
* *Lucas Carolino De Almeida, RA 2010447; e*
* *Talles Da Silva Carlos Fernandes, RA 2002465.*
---
Visite nossa página no [Github](https://github.com/wpgoncalves/fuel-analysis)
'''


def clear_selections() -> None:
    state = st.session_state

    state.last_selected_regions = state.regions_list
    state.last_selected_states = state.states_list
    state.last_selected_fuels = state.fuels_list
    state.last_selected_flags = state.flags_list

    state.inicial_date = DATE_START
    state.final_date = DATE_END
    state.selected_regions = state.last_selected_regions
    state.selected_states = state.last_selected_states
    state.selected_county = 'Todos'
    state.selected_resale = 'Todos'
    state.selected_fuels = state.last_selected_fuels
    state.selected_flags = state.last_selected_flags


@st.cache_data
def load_data() -> FuelData:
    return FuelData()


if __name__ == '__main__':

    utils._shown_default_value_warning = True

    st.set_page_config(
        page_title='Projeto Integrador IV',
        page_icon=Path.joinpath(
            BASE_DIR, 'static/img/statistics.png').__str__(),
        layout='wide',
        menu_items={
            'Get help': 'mailto:wpgoncalves1984@gmail.com',
            'Report a bug': 'https://github.com/wpgoncalves/fuel-analysis/issues',  # noqa: E501
            'About': ABOUT_MSG
        }
    )

    fdt = load_data()

    st.title(
        'Análise Comparativa da Relação Custo x Benefício do Etanol nos Postos Brasileiros.'  # noqa: E501
    )

    # Sidebar lateral contendo filtros
    with st.sidebar:
        st.title(':ballot_box_with_check: Dados de Seleção')

        st.markdown('Período Análisado: ***2º Semestre de 2022***')

        # Container for inicial date and final date widgets
        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                inicial_date = date_input_field('Inicial')

            with col2:
                final_date = date_input_field('Final')

            fdt.set_period(inicial_date, final_date)

        with st.expander(':dart: **Dados de Localidade**'):
            selected_regions = multiselect_regions(fdt)

            selected_state = selectbox_states(fdt, selected_regions)

            selected_county = selectbox_counties(fdt, selected_state)

        with st.expander(':white_check_mark: **Outras Seleções**'):
            selected_resale = selectbox_resales(
                fdt, selected_state,
                selected_county
            )

            selected_fuel = multiselect_fuels(fdt)

            selected_flag = selectbox_flags(fdt)

        st.button(':recycle: **Limpar Seleções**',
                  on_click=clear_selections,
                  use_container_width=True)

    # Containers separated by tabs: charts and spreadsheet
    with st.container():
        tab1, tab2 = st.tabs(
            [':bar_chart: Gráficos', ':clipboard: Planilha'])

        with tab1:
            st.markdown(
                '### Métricas: Valores mínimo, máximo e custo benefício')

            with st.container():
                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    msg_help = '''
                    Demonstração do valor mínimo e máximo do Etanol.
                    '''

                    st.metric('ETANOL',
                              fdt.get_min_sale_value_of_product('ETANOL'),
                              delta=fdt.get_max_sale_value_of_product(
                                  'ETANOL'),
                              delta_color="normal",
                              help=msg_help,
                              label_visibility="visible")
                with col2:
                    msg_help = '''
                    Demonstração do valor mínimo e máximo da Gasolina.
                    '''

                    st.metric('GASOLINA',
                              fdt.get_min_sale_value_of_product('GASOLINA'),
                              delta=fdt.get_max_sale_value_of_product(
                                  'GASOLINA'),
                              delta_color="normal",
                              help=msg_help,
                              label_visibility="visible")

                with col3:
                    msg_help = '''
                    Demonstração do valor mínimo e máximo da Gasolina
                    Aditivada.
                    '''

                    st.metric('GASOLINA ADITIVADA',
                              fdt.get_min_sale_value_of_product(
                                  'GASOLINA ADITIVADA'),
                              delta=fdt.get_max_sale_value_of_product(
                                  'GASOLINA ADITIVADA'),
                              delta_color="normal",
                              help=msg_help,
                              label_visibility="visible")

                with col4:
                    msg_help = '''
                    Demostração do custo benefício do Etanol em relação a
                    Gasolina.\n
                    Até 70% o Etanol se mostra mais vantasojo.
                    '''

                    st.metric(
                        'ETANOL x GASOLINA',
                        fdt.get_ethanol_cost_benefit(operation='Mínimo'),
                        delta=fdt.get_ethanol_cost_benefit(operation='Máximo'),
                        delta_color='normal',
                        help=msg_help,
                        label_visibility='visible'
                    )

                with col5:
                    msg_help = '''
                    Demostração do custo benefício do Etanol em relação a
                    Gasolina Aditivada.\n
                    Até 70% o Etanol se mostra mais vantasojo.
                    '''

                    st.metric(
                        'ETANOL x GAS. ADITIVADA',
                        fdt.get_ethanol_cost_benefit(
                            'GASOLINA ADITIVADA', 'Mínimo'),
                        delta=fdt.get_ethanol_cost_benefit(
                            'GASOLINA ADITIVADA', 'Máximo'),
                        delta_color='normal',
                        help=msg_help,
                        label_visibility='visible'

                    )

            st.markdown('# Valores Médios de Venda dos Combustíves')
            st.markdown('* ## por Região Brasileira')

            fdt.get_chart_sales_value_by_region(st.pyplot)

            st.markdown('* ## por Região e Estado Brasileiro')

            fdt.get_chart_sales_value_by_regions_and_states(st.pyplot)

        with tab2:
            columns = ['Revenda', 'CNPJ da Revenda', 'Produto',
                       'Data da Coleta', 'Valor de Venda', 'Valor de Compra',
                       'Bandeira']

            st.dataframe(fdt.get_dataframe(columns),
                         use_container_width=True)

            st.write(
                f'Total de registros: {fdt.get_amount_records()}')
