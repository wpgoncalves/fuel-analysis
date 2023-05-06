from datetime import datetime

import streamlit as st
from typing_extensions import Literal, TypeAlias

from fuel_data import FuelData
from settings import DATE_END, DATE_START, MAX_DATE, MIN_DATE
from tools import word_capitalize

OptValue: TypeAlias = Literal['Inicial', 'Final']


class FuelController():

    _state = st.session_state

    def __init__(self, fdt: FuelData) -> None:
        self._fdt = fdt

    def _update_state(self, key_field: str, key_last: str) -> None:
        if len(self._state[key_field]) < 1:
            self._state[key_field] = self._state[key_last]
        else:
            self._state[key_last] = self._state[key_field]

    def date_input_field(self, option: OptValue = 'Inicial') -> datetime:

        if option not in ['Inicial', 'Final']:
            raise ValueError(
                f"'{str(option)}' is not an accepted value. option only accepts: "  # noqa: E501
                "'Inicial' or 'Final'"
            )

        params = {
            'Inicial': [
                'Data Inicial',
                'inicial_date',
                'Selecione a data de início do intervalo de tempo'
            ],
            'Final': [
                'Data Final',
                'final_date',
                'Selecione a data final do intervalo de tempo'
            ]
        }

        value = st.date_input(
            f':calendar: {params[option][0]}',
            DATE_START if option == 'Inicial' else DATE_END,
            MIN_DATE,
            MAX_DATE,
            key=params[option][1],
            help=params[option][2]
        )

        return value  # type: ignore

    def multiselect_regions(self) -> list:
        regions_list = self._fdt.get_regions()
        amount_regions = len(regions_list)
        acronyms = {
            'CO': 'Centro-Oeste',
            'N': 'Norte',
            'NE': 'Nordeste',
            'S': 'Sul',
            'SE': 'Sudeste',
        }

        return st.multiselect(
            ':compass: Região(ões)',
            regions_list,
            format_func=lambda x: acronyms[x],
            max_selections=amount_regions-1,
            key='selected_regions',
            help='Selecione uma ou mais regiões do país.'
        )

    def multiselect_states(self, regions: list = []) -> list:
        states_list = self._fdt.get_states(regions)
        amount_states = len(states_list)
        acronyms = {
            'AC': 'Acre',
            'AL': 'Alagoas',
            'AP': 'Amapá',
            'AM': 'Amazonas',
            'BA': 'Bahia',
            'CE': 'Ceará',
            'DF': 'Distrito Federal',
            'ES': 'Espírito Santo',
            'GO': 'Goiás',
            'MA': 'Maranhão',
            'MT': 'Mato Grosso',
            'MS': 'Mato Grosso do Sul',
            'MG': 'Minas Gerais',
            'PA': 'Pará',
            'PB': 'Paraíba',
            'PR': 'Paraná',
            'PE': 'Pernambuco',
            'PI': 'Piauí',
            'RJ': 'Rio de Janeiro',
            'RN': 'Rio Grande do Norte',
            'RS': 'Rio Grande do Sul',
            'RO': 'Rondônia',
            'RR': 'Roraima',
            'SC': 'Santa Catarina',
            'SP': 'São Paulo',
            'SE': 'Sergipe',
            'TO': 'Tocantins'
        }

        return st.multiselect(
            ':city_sunrise: Estado(s)',
            states_list,
            format_func=lambda x: acronyms[x],
            max_selections=amount_states if regions != [] else amount_states-1,
            key='selected_states',
            help='Selecione um ou mais estados brasileiros'
        )

    def multiselect_cities(self, states: list = []) -> list:
        cities_list = self._fdt.get_cities(states)

        return st.multiselect(
            ':city_sunrise: Município(s)',
            cities_list,
            max_selections=4,
            format_func=lambda x: word_capitalize(x),
            key='selected_city',
            help='Selecione um ou mais municípios brasileiros'
        )

    def selectbox_city(self, states: list = []) -> str:
        cities_list = self._fdt.get_cities(states, True)

        return str(st.selectbox(
            ':city_sunrise: Município',
            cities_list,
            format_func=lambda x: word_capitalize(x),
            key='selected_city',
            help='Selecione um município brasileiro'
        ))

    def selectbox_resales(self, sets: dict = None) -> list:  # type: ignore
        resales_list = self._fdt.get_resales(sets)

        return [st.selectbox(
            ':shopping_trolley: Revenda',
            resales_list,
            format_func=lambda x: word_capitalize(x),
            key='selected_resale',
            help='Selecione um revendedor'
        )]

    def multiselect_fuels(self, sets: dict = None) -> list:  # type: ignore
        fuels_list = self._fdt.get_fuels(sets)

        return st.multiselect(
            ':fuelpump: Combustível',
            fuels_list,
            max_selections=len(fuels_list)-1,
            format_func=lambda x: word_capitalize(x),
            key='selected_fuels',
            help='Selecione um ou mais tipos de combustível'
        )

    def multiselect_flags(self, sets: dict = None) -> list:  # type: ignore
        flags_list = self._fdt.get_flags(sets)

        return st.multiselect(
            ':waving_white_flag: Bandeira',
            flags_list,
            max_selections=len(flags_list)-1,
            format_func=lambda x: word_capitalize(x),
            key='selected_flags',
            help='Selecione uma ou mais bandeiras'
        )
