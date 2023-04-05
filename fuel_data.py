from datetime import datetime
from pathlib import Path
from typing import Any, Union

import pandas as pd
from numpy import isnan
from typing_extensions import TypeAlias

BASE_DIR = Path(__file__).resolve().parent

Value: TypeAlias = Union['pd.Series', float, None]


class FuelData():

    __df = pd.DataFrame

    def __init__(self) -> None:
        df = pd.read_csv(Path.joinpath(
            BASE_DIR, 'base/ca-2022-02.csv'), sep=';')

        df['Data da Coleta'] = pd.to_datetime(
            df['Data da Coleta'], exact=True, dayfirst=True,
            infer_datetime_format=True, format='%d/%m/%Y', errors='coerce')

        df['Valor de Venda'] = df['Valor de Venda'].str.replace(',', '.')

        df['Valor de Venda'] = pd.to_numeric(
            df['Valor de Venda'], errors='coerce', downcast='float')

        df['Valor de Compra'] = pd.to_numeric(
            df['Valor de Compra'], errors='coerce', downcast='float')

        df.fillna(value={'Valor de Compra': 0}, inplace=True)

        df.drop(['Nome da Rua', 'Numero Rua', 'Complemento', 'Bairro', 'Cep',
                 'Unidade de Medida'], axis=1, inplace=True)

        self.__df = df[df['Produto'].isin([
            'GASOLINA',
            'GASOLINA ADITIVADA',
            'ETANOL'
        ])]

    def __extract_ordened_values_not_duplicates(self, IndexLabel: str, df: pd.DataFrame = None) -> pd.Series:  # noqa: E501
        df_base = df if df is not None else self.__df.copy()
        var = df_base[IndexLabel].drop_duplicates()
        var.sort_values(inplace=True, ignore_index=True)
        return var

    def __include_all_option(self, serie: pd.Series) -> pd.Series:
        empty = pd.Series(['Todos'], dtype='object')
        return pd.concat([empty, serie], ignore_index=True)

    def __currency_format(self, value: Value) -> Any:
        if value is None:
            value = "—"
        elif isinstance(value, pd.Series):
            value = value.map('R$ {:,.2f}'.format)
            value = pd.Series(value, dtype='string').str.replace('.', ',')
        elif isinstance(value, float):
            value = f'R$ {value:,.2f}'.replace('.', ',')
        else:
            raise TypeError(
                f"'{str(value)}' is of type {str(type(value))}, which is not an accepted type."  # noqa: E501
                " value only accepts: pandas.Series, float or None"
                " Please convert the value to an accepted type."
            )

        return value

    def __br_date_format(self, column: pd.Series) -> pd.Series:
        return column.dt.strftime('%d/%m/%Y')

    # Getters
    def get_dataframe(self, columns: list = []) -> pd.DataFrame:
        new_df = self.__df[columns].copy() if len(
            columns) > 0 else self.__df.copy()

        if 'Data da Coleta' in columns:
            new_df['Data da Coleta'] = self.__br_date_format(
                new_df['Data da Coleta'])

        if 'Valor de Venda' in columns:
            new_df['Valor de Venda'] = self.__currency_format(
                new_df['Valor de Venda'])

        if 'Valor de Compra' in columns:
            new_df['Valor de Compra'] = self.__currency_format(
                new_df['Valor de Compra'])

        return new_df

    def get_regions(self) -> pd.Series:
        return self.__extract_ordened_values_not_duplicates('Regiao - Sigla')

    def get_states(self, regions: list) -> pd.Series:
        base = self.__df[self.__df['Regiao - Sigla']
                         .isin(regions)] if len(regions) > 0 else None
        return self.__include_all_option(
            self.__extract_ordened_values_not_duplicates('Estado - Sigla',
                                                         base))

    def get_counties(self, state: str) -> pd.Series:
        base = self.__df.query('`Estado - Sigla` == @state')
        return self.__include_all_option(
            self.__extract_ordened_values_not_duplicates('Municipio',
                                                         base))

    def get_resales(self, state: str = 'Todos', county: str = 'Todos') -> pd.Series:  # noqa: E501
        columns = ['Revenda', 'CNPJ da Revenda']

        if state != 'Todos' and county != 'Todos':
            expr = '`Estado - Sigla` == @state and Municipio == @county'
            base = self.__df.query(expr=expr)[columns]
        elif state != 'Todos' and county == 'Todos':
            expr = '`Estado - Sigla` == @state'
            base = self.__df.query(expr=expr)[columns]
        elif state == 'Todos' and county != 'Todos':
            expr = 'Municipio == @county'
            base = self.__df.query(expr=expr)[columns]
        else:
            base = self.__df.copy()

        base.drop_duplicates(subset=columns[0], inplace=True)
        base.sort_values(by=columns, ignore_index=True, inplace=True)
        return self.__include_all_option(base[columns[0]])

    def get_fuels(self, option_all: bool = True):
        if not option_all:
            return self.__extract_ordened_values_not_duplicates('Produto')

        return self.__include_all_option(
            self.__extract_ordened_values_not_duplicates('Produto'))

    def get_flags(self) -> pd.Series:
        return self.__include_all_option(
            self.__extract_ordened_values_not_duplicates('Bandeira'))

    def get_amount_records(self) -> int:
        return self.__df.shape[0]

    def get_max_sale_value_of_product(self, produto: str) -> str:
        result = self.__df.query('Produto == @produto')['Valor de Venda'].max()
        result = float(result) if not isnan(result) else float(0)
        return self.__currency_format(result)

    def get_min_sale_value_of_product(self, produto: str) -> str:
        result = self.__df.query('Produto == @produto')['Valor de Venda'].min()
        result = float(result) if not isnan(result) else float(0)
        return self.__currency_format(result)

    # Setters
    def set_period(self, inicial_date: datetime, final_date: datetime) -> None:
        self.__df.query('`Data da Coleta` >= @inicial_date and `Data da Coleta` <= @final_date', inplace=True)  # noqa: E501

    def set_regions(self, regions: list) -> None:
        self.__df = self.__df[self.__df['Regiao - Sigla'].isin(regions)]

    def set_state(self, state: str) -> None:
        self.__df.query('`Estado - Sigla` == @state', inplace=True)

    def set_county(self, county: str) -> None:
        self.__df.query('Municipio == @county', inplace=True)

    def set_resale(self, resale: str) -> None:
        self.__df.query('Revenda == @resale', inplace=True)

    def set_fuel(self, fuel: str) -> None:
        self.__df.query('Produto == @fuel', inplace=True)

    def set_flag(self, flag: str) -> None:
        self.__df.query('Bandeira == @flag', inplace=True)
