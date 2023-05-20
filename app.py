from pathlib import Path

import streamlit as st
from streamlit.elements import utils

from custom_exceptions import ExcessValues
from fuel_controller import FuelController
from fuel_data import BASE_DIR, FuelData
from settings import ABOUT_MSG, DATE_END, DATE_START


def clear_selections() -> None:
    st.session_state.clear()
    st.session_state.update(
        [
            ('inicial_date', DATE_START),
            ('final_date', DATE_END),
            ('selected_regions', []),
            ('selected_states', []),
            ('selected_county', []),
            ('selected_resale', 'Todos'),
            ('selected_fuels', []),
            ('selected_flags', []),
        ]
    )


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
    fcl = FuelController(fdt)

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
                inicial_date = fcl.date_input_field('Inicial')

            with col2:
                final_date = fcl.date_input_field('Final')

        with st.expander(':dart: **Dados de Localidade**'):
            selected_regions = fcl.multiselect_regions()

            selected_states = fcl.multiselect_states(selected_regions)

            selected_cities = fcl.multiselect_cities(selected_states)

        with st.expander(':white_check_mark: **Outras Seleções**'):
            selected_resale = fcl.selectbox_resales(
                sets={
                    'cities': selected_cities,
                    'flags': None,
                    'fuels': None,
                    'period': (inicial_date, final_date),
                    'regions': selected_regions,
                    'resales': None,
                    'states': selected_states
                }
            )

            selected_fuels = fcl.multiselect_fuels(
                sets={
                    'cities': selected_cities,
                    'flags': None,
                    'fuels': None,
                    'period': (inicial_date, final_date),
                    'regions': selected_regions,
                    'resales': selected_resale,
                    'states': selected_states
                }
            )

            selected_flags = fcl.multiselect_flags(
                sets={
                    'cities': selected_cities,
                    'flags': None,
                    'fuels': selected_fuels,
                    'period': (inicial_date, final_date),
                    'regions': selected_regions,
                    'resales': selected_resale,
                    'states': selected_states
                }
            )

        st.button(':recycle: **Limpar Seleções**',
                  on_click=clear_selections,
                  use_container_width=True)

    fdt.set_fuel(
        sets={
            'period': (inicial_date, final_date),
            'regions': selected_regions,
            'states': selected_states,
            'cities': selected_cities,
            'resales': selected_resale,
            'fuels': selected_fuels,
            'flags': selected_flags
        },
        inplace=True
    )

    # Containers separated by tabs: charts and spreadsheet
    with st.container():
        tab1, tab2 = st.tabs([
            ':bar_chart: Gráficos',
            ':clipboard: Planilha'
        ])

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

            st.markdown('---')
            st.markdown('### Valores Médios de Venda dos Combustíves')

            with st.expander('**Comparativo por Região Brasileira**'):
                st.markdown(
                    '''
                    > *O presente relatório apresenta os valores médios dos
                    preços de venda dos combustíveis nas diferentes regiões
                    do país, com base nos dados fornecidos pela Agência
                    Nacional do Petróleo, Gás Natural e Biocombustíveis (ANP).
                    O objetivo é fornecer uma visão geral da evolução dos
                    preços dos principais tipos de combustíveis (gasolina,
                    gasolina aditivada e etanol) no período selecionado, bem
                    como comparar os valores médios entre as regiões
                    brasileiras.*
                    '''
                )
                fdt.get_chart_sales_value_by_region(st.pyplot)

            with st.expander('**Comparativo por Estado e Região Brasileira**'):
                st.markdown(
                    '''
                    > *Um dos fatores que influenciam o custo de vida dos
                    brasileiros é o preço dos combustíveis. Esse preço
                    varia de acordo com a região do país, a carga
                    tributária, a concorrência entre os postos e a demanda
                    dos consumidores. Neste contexto, vamos apresentar os
                    valores médios dos preços de venda dos combustíveis nos
                    diferentes estados, com base nos dados da Agência
                    Nacional do Petróleo, Gás Natural e Biocombustíveis
                    (ANP) referentes ao perído selecionado.*
                    '''
                )
                fdt.get_chart_sales_value_by_regions_and_states(st.pyplot)

            with st.expander('**Comparativo por Cidades Brasileiras**'):
                st.markdown(
                    '''
                    > *Os valores médios dos preços de venda dos combustíveis
                    nas diferentes cidades são calculados com base nas
                    informações fornecidas pelos postos de abastecimento. Esses
                    valores podem variar de acordo com a localização, a
                    concorrência, a oferta, a demanda, entre outros fatores.*
                    '''
                )

                try:
                    st.pyplot(fdt.get_chart_sales_value_by_cities())
                except ExcessValues as e:
                    st.warning(e, icon="⚠️")

            with st.expander('**Comparativo de valores por bandeira dos postos\
                             de combustível**'):
                st.markdown(
                    '''
                    > *Um comparativo de valores por bandeira dos postos de
                    combustível é uma forma de encontrar o melhor preço na hora
                    de abastecer o seu veículo. Os preços dos combustíveis
                    variam de acordo com a bandeira do posto, que representa a
                    distribuidora que fornece o produto. As bandeiras mais
                    conhecidas no Brasil são BR (Petrobras), Ipiranga, Shell e
                    Ale. Existem também os postos sem bandeira, também chamados
                    de bandeira branca que são aqueles que não respresentam uma
                    marca própria, sendo livre para negociar e comprar
                    combustíveis de diferentes distribuidoras.*
                    '''
                )

                try:
                    st.pyplot(fdt.get_chart_sales_value_by_flags())
                except ExcessValues as e:
                    st.warning(e, icon="⚠️")

            st.markdown('---')
            st.markdown(
                '### Evolução dos Valores Médios de Venda dos Combustíveis')

            with st.expander('**Ao longo do tempo**'):
                st.markdown(
                    '''
                    > *Os valores médios de venda dos combustíveis variam ao
                    longo do tempo e são monitorados pela Agência Nacional do
                    Petróleo, Gás Natural e Biocombustíveis (ANP). A ANP faz
                    pesquisas semanais e mensais de preços de diferentes tipos
                    de combustíveis e em várias localidades do país. Essas
                    pesquisas mostram as mudanças nos preços e nas margens de
                    comercialização dos combustíveis, e os efeitos das
                    políticas públicas e do mercado no setor. Os dados das
                    pesquisas podem ser acessados no site da ANP em formato
                    aberto.*
                    '''
                )
                st.pyplot(fdt.get_chart_evolution_of_sales_values_over_time())

        # with tab2:
        #     st.markdown('# Evolução dos Valores dos Combustíveis')
        #     st.markdown('* ## ao longo do tempo')

        with tab2:
            columns = ['Revenda', 'CNPJ da Revenda', 'Produto',
                       'Data da Coleta', 'Valor de Venda', 'Valor de Compra',
                       'Bandeira']

            st.dataframe(fdt.get_dataframe(columns, True, True),
                         use_container_width=True)

            st.write(
                f'Total de registros: {fdt.get_amount_records()}')
