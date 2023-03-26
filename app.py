from datetime import datetime
from pathlib import Path

import streamlit as st

from fuel_data import BASE_DIR, FuelData

# Constantes
DATE_START = datetime(2022, 7, 1)
DATE_END = datetime(2022, 7, 31)
MIN_DATE = datetime(2022, 7, 1)
MAX_DATE = datetime(2022, 12, 31)


def multiselect_regions(fdt: FuelData) -> list:
    value = st.multiselect(
        ':compass: Região',
        fdt.get_regions(),
        key='selected_regions',
        help='Selecione uma ou mais regiões do país'
    )

    if len(value) > 0:
        fdt.set_regions(value)

    return value


def selectbox_states(fdt: FuelData, regions: list) -> str:
    value = str(st.selectbox(
        ':city_sunrise: Estado',
        fdt.get_states(regions),
        disabled=len(regions) == 0,
        key='selected_state',
        help='Selecione um estado brasileiro'
    ))

    if value != 'Todos':
        fdt.set_state(value)

    return value


def selectbox_counties(fdt: FuelData, state: str) -> str:
    value = str(st.selectbox(
        ':city_sunrise: Município',
        fdt.get_counties(state),
        disabled=(state == 'Todos'),
        key='selected_county',
        help='Selecione um município brasileiro'
    ))

    if value != 'Todos':
        fdt.set_county(value)

    return value


def selectbox_resales(fdt: FuelData, state: str, county: str) -> str:
    value = str(st.selectbox(
        ':shopping_trolley: Revenda',
        fdt.get_resales(state, county),
        key='selected_resale',
        help='Selecione um revendedor'
    ))

    if value != 'Todos':
        fdt.set_resale(value)

    return value


def selectbox_fuels(fdt: FuelData) -> str:
    value = str(st.selectbox(
        ':fuelpump: Combustível',
        fdt.get_fuels(),
        key='selected_fuel',
        help='Selecione um tipo de combustível'
    ))

    if value != 'Todos':
        fdt.set_fuel(value)

    return value


def selectbox_flags(fdt: FuelData) -> str:
    value = str(st.selectbox(
        ':waving_white_flag: Bandeira',
        fdt.get_flags(),
        key='selected_flag',
        help='Selecione uma bandeira'
    ))

    if value != 'Todos':
        fdt.set_flag(value)

    return value


def clear_selections() -> None:
    st.session_state['inicial_date'] = DATE_START
    st.session_state['final_date'] = DATE_END
    st.session_state['selected_regions'] = []
    st.session_state['selected_state'] = 'Todos'
    st.session_state['selected_county'] = 'Todos'
    st.session_state['selected_resale'] = 'Todos'
    st.session_state['selected_fuel'] = 'Todos'
    st.session_state['selected_flag'] = 'Todos'


if __name__ == '__main__':

    fdt = FuelData()

    st.set_page_config(
        page_title='Projeto Integrador IV',
        page_icon=Path.joinpath(
            BASE_DIR, 'static/img/statistics.png').__str__(),
        layout='wide'
    )

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
                inicial_date = st.date_input(
                    ':calendar: Data Inicial',
                    DATE_START,
                    MIN_DATE,
                    MAX_DATE,
                    key='inicial_date',
                    help='Selecione a data de início do intervalo de tempo'
                )

            with col2:
                final_date = st.date_input(
                    ':calendar: Data Final',
                    DATE_END,
                    MIN_DATE,
                    MAX_DATE,
                    key='final_date',
                    help='Selecione a data final do intervalo de tempo'
                )

            fdt.set_period(inicial_date, final_date)  # type: ignore

        with st.expander(':dart: Dados de Localidade'):
            selected_regions = multiselect_regions(fdt)

            # Container for state and city select box
            with st.container():
                col1, col2 = st.columns([1, 2])

                with col1:
                    selected_state = selectbox_states(fdt, selected_regions)

                with col2:
                    selected_county = selectbox_counties(fdt, selected_state)

        with st.expander(':white_check_mark: Outras Seleções'):
            selected_resale = selectbox_resales(
                fdt, selected_state,
                selected_county
            )

            selected_fuel = selectbox_fuels(fdt)

            selected_flag = selectbox_flags(fdt)

        st.button(':recycle: **Limpar Seleções**',
                  on_click=clear_selections,
                  use_container_width=True)

    # Containers separated by tabs: charts and spreadsheet
    with st.container():
        tab1, tab2 = st.tabs(
            [':bar_chart: Gráficos', ':clipboard: Planilha'])
        with tab1:
            st.text('Área de conteúdo onde os gráficos relevantes para a análise serão exibidos')  # noqa: E501

        with tab2:
            # st.text('Content area where the table relevant to the analysis will be displayed')  # noqa: E501
            # col1, col2, col3 = st.columns(3, gap='large')
            # col1.metric('lower value', )
            # col2.metric('highest value')
            # col3.metric('Record Total')
            columns = ['Revenda', 'CNPJ da Revenda', 'Produto',
                       'Data da Coleta', 'Valor de Venda', 'Valor de Compra',
                       'Bandeira']

            st.dataframe(fdt.get_dataframe(columns),
                         use_container_width=True)

            st.write(
                f'Total de registros: {fdt.get_amount_records()}')
