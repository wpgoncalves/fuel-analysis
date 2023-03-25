from datetime import datetime

import streamlit as st

from fuel_data import FuelData

# Constantes
DATE_START = datetime(2022, 7, 1)
DATE_END = datetime(2022, 7, 31)
MIN_DATE = datetime(2022, 7, 1)
MAX_DATE = datetime(2022, 12, 31)


if __name__ == '__main__':

    fdt = FuelData()

    st.set_page_config(
        page_title=' IV Integrator Project', layout='wide')

    st.title(
        'Comparative analysis of the cost-benefit ratio of ethanol at Brazilian gas stations.')  # noqa: E501

    # Sidebar lateral contendo filtros
    with st.sidebar:
        st.title(':ballot_box_with_check: Selection data')

        st.markdown(':clipboard: Period analyzed: ***2nd half of 2022.***')

        # Container for inicial date and final date widgets
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

            fdt.set_period(inicial_date, final_date)  # type: ignore

        with st.expander(':round_pushpin: Localization'):
            selected_regions = st.multiselect(':compass: Region',
                                              fdt.get_regions(),
                                              help='Select one or more country regions')  # noqa: E501

            if len(selected_regions) > 0:
                fdt.set_regions(selected_regions)

            # Container for state and city select box
            with st.container():
                col1, col2 = st.columns([1, 2])

                with col1:
                    opt_states = fdt.get_states(selected_regions)

                    selected_state = st.selectbox(':city_sunrise: State',
                                                  opt_states,
                                                  disabled=len(selected_regions) == 0,  # noqa: E501
                                                  help='Select a Brazilian state')  # noqa: E501

                    if selected_state != 'All':
                        fdt.set_state(selected_state)  # type: ignore

                with col2:
                    opt_counties = fdt.get_counties(
                        selected_state)  # type: ignore

                    selected_county = st.selectbox(':city_sunrise: City',
                                                   opt_counties,
                                                   disabled=selected_state == 'All',  # noqa: E501
                                                   help='Select a Brazilian municipality')  # noqa: E501

                    if selected_county != 'All':
                        fdt.set_county(selected_county)  # type: ignore

        opt_resales = fdt.get_resales(
            selected_state, selected_county)  # type: ignore

        selected_resale = st.selectbox(':shopping_trolley: Resale',
                                       opt_resales,
                                       help='Select a reseller')
        if selected_resale != 'All':
            fdt.set_resale(selected_resale)  # type: ignore

        opt_fuels = fdt.get_fuels()

        selected_fuel = st.selectbox(':fuelpump: Fuel',
                                     opt_fuels,
                                     help='Select a fuel type')

        if selected_fuel != 'All':
            fdt.set_fuel(selected_fuel)  # type: ignore

        opt_flags = fdt.get_flags()

        selected_flag = st.selectbox(':waving_white_flag: Flag',
                                     opt_flags,
                                     help='Select a flag')

        if selected_flag != 'All':
            fdt.set_flag(selected_flag)  # type: ignore

    # Conteiners separados por abas: Gráficos e Tabelas
    with st.container():
        tab1, tab2 = st.tabs(
            [':bar_chart: Graphics', ':clipboard: Spreadsheet'])
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

            st.dataframe(fdt.get_dataframe(columns),
                         use_container_width=True)

            st.write(
                f'Total de registros: {fdt.get_amount_records()}')
