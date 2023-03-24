from datetime import datetime

import streamlit as st

from fuel_data import FuelData

# Constantes
DATE_START = datetime(2022, 7, 1)
DATE_END = datetime(2022, 12, 31)
MIN_DATE = datetime(2022, 7, 1)
MAX_DATE = datetime(2022, 12, 31)


def update_filters():
    fuel_data.set_state(st.session_state.selected_state)
    st.info(f'Filtro aplicado! Estado: {st.session_state.selected_state}')

    # Continuar a partir daqui tentando realizar a filtragem através do
    # on_change.


if __name__ == '__main__':

    fuel_data = FuelData()

    st.set_page_config(
        page_title=' IV Integrator Project', layout='wide')

    st.title('Comparative Analysis of Fuel Prices in Brazil')

    # Sidebar lateral contendo filtros
    with st.sidebar:
        st.title(':ballot_box_with_check: Filters')

        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                inicial_date = st.date_input(':calendar: Initial date',
                                             DATE_START,
                                             MIN_DATE,
                                             MAX_DATE,
                                             help='Select the start date of the time range')  # noqa: E501

            with col2:
                final_date = st.date_input(':calendar: Final date',
                                           DATE_END,
                                           MIN_DATE,
                                           MAX_DATE,
                                           help='Select the end date of the time range')  # noqa: E501

        fuel_data.set_period(inicial_date, final_date)  # type: ignore

        selected_regions = st.multiselect(':compass: Region',
                                          fuel_data.get_regions(),
                                          help='Select one or more country regions')  # noqa: E501

        if len(selected_regions) > 0:
            fuel_data.set_regions(selected_regions)

        col1, col2 = st.columns([1, 2])

        with col1:
            opt_states = fuel_data.get_states(selected_regions)
            selected_state = st.selectbox(':city_sunrise: State',
                                          opt_states,
                                          key='selected_state',
                                          on_change=update_filters,
                                          help='Select a Brazilian state')

            # fuel_data.set_state(selected_state)  # type: ignore

        with col2:
            opt_counties = fuel_data.get_counties(
                selected_state)  # type: ignore
            selected_county = st.selectbox(':city_sunrise: County',
                                           opt_counties,
                                           help='Select a Brazilian municipality')  # noqa: E501

            # fuel_data.set_county(selected_county)  # type: ignore

        opt_resales = fuel_data.get_resales(
            selected_state, selected_county)  # type: ignore
        selected_resale = st.selectbox(':shopping_trolley: Resale',
                                       opt_resales,
                                       help='Select a reseller')

        opt_fuels = fuel_data.get_fuels()
        selected_fuel = st.selectbox(':fuelpump: Fuel',
                                     opt_fuels,
                                     help='Select a fuel type')

        selected_flag = st.selectbox(':waving_white_flag: Flag',
                                     [],
                                     help='Select a flag')

    # Conteiners separados por abas: Gráficos e Tabelas
    with st.container():
        tab1, tab2 = st.tabs([':bar_chart: Graphics', ':clipboard: Tables'])
        with tab1:
            st.text('Content area where the graphs relevant to the analysis will be displayed')  # noqa: E501

        with tab2:
            # st.text('Content area where the table relevant to the analysis will be displayed')  # noqa: E501
            # col1, col2, col3 = st.columns(3, gap='large')
            # col1.metric('lower value', )
            # col2.metric('highest value')
            # col3.metric('Record Total')
            columns = ['Revenda', 'CNPJ da Revenda', 'Produto',
                       'Data da Coleta', 'Valor de Venda', 'Valor de Compra',
                       'Bandeira']

            st.dataframe(fuel_data.get_dataframe(columns),
                         use_container_width=True)

            st.write(
                f'Total de registros: {fuel_data.get_dataframe().shape[0]}')

# Reiniciar incluindo um item em branco nos gets para não haver a filtragem
# automática (todos)
