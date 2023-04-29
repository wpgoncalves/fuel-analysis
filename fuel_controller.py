from datetime import datetime

import streamlit as st
from typing_extensions import Literal, TypeAlias

from fuel_data import FuelData

OptValue: TypeAlias = Literal['Inicial', 'Final']

# Constantes
DATE_START = datetime(2022, 7, 1)
DATE_END = datetime(2022, 7, 31)
MIN_DATE = datetime(2022, 7, 1)
MAX_DATE = datetime(2022, 12, 31)


def date_input_field(option: OptValue = 'Inicial') -> datetime:

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


def multiselect_regions(fdt: FuelData) -> list:

    state = st.session_state

    if 'regions_list'not in state:
        state.regions_list = fdt.get_regions().tolist()

    if 'last_selected_regions' not in state:
        state.last_selected_regions = state.regions_list

    def _update_state():
        if len(state.selected_regions) < 1:
            state.selected_regions = state.last_selected_regions
        else:
            state.last_selected_regions = state.selected_regions

    value = st.multiselect(
        ':compass: Região',
        fdt.get_regions(),
        default=state.regions_list,
        on_change=_update_state,
        max_selections=5,
        key='selected_regions',
        help='Selecione uma ou mais regiões do país'
    )

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


def multiselect_fuels(fdt: FuelData) -> list:

    state = st.session_state

    if "fuels_list" not in state:
        state.fuels_list = fdt.get_fuels(False, True)

    if "last_selected_fuels" not in state:
        state.last_selected_fuels = state.fuels_list

    def _update_state():
        if len(state.selected_fuel) < 1:
            state.selected_fuels = state.last_selected_fuels
        else:
            state.last_selected_fuels = state.selected_fuels

    value = st.multiselect(
        ':fuelpump: Combustível',
        fdt.get_fuels(False),
        default=state.fuels_list,
        on_change=_update_state,
        max_selections=3,
        key='selected_fuel',
        help='Selecione um ou mais tipos de combustível'
    )

    fdt.set_fuels(value)

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
