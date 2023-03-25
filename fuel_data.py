from datetime import datetime
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent


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

        self.__df = df

    def __extract_ordened_values_not_duplicates(self, IndexLabel: str, df: pd.DataFrame = None) -> pd.Series:  # noqa: E501
        df_base = df if df is not None else self.__df
        var = df_base[IndexLabel].drop_duplicates()
        var.sort_values(inplace=True, ignore_index=True)
        return var

    def __include_empty(self, serie: pd.Series) -> pd.Series:
        empty = pd.Series(['All'], dtype='object')
        return pd.concat([empty, serie], ignore_index=True)

    # Getters
    def get_dataframe(self, columns: list = []) -> pd.DataFrame:
        return self.__df[columns] if len(columns) > 0 else self.__df

    def get_regions(self) -> pd.Series:
        return self.__extract_ordened_values_not_duplicates('Regiao - Sigla')

    def get_states(self, regions: list) -> pd.Series:
        base = self.__df[self.__df['Regiao - Sigla']
                         .isin(regions)] if len(regions) > 0 else None
        return self.__include_empty(
            self.__extract_ordened_values_not_duplicates('Estado - Sigla',
                                                         base)
        )

    def get_counties(self, state: str) -> pd.Series:
        base = self.__df.query('`Estado - Sigla` == @state')
        return self.__include_empty(
            self.__extract_ordened_values_not_duplicates('Municipio',
                                                         base)
        )

    def get_resales(self, state: str = 'All', county: str = 'All') -> pd.Series:  # noqa: E501
        columns = ['Revenda', 'CNPJ da Revenda']

        if state == 'All' and county == 'All':
            base = self.__df
        else:
            expr = '`Estado - Sigla` == @state and Municipio == @county'
            base = self.__df.query(expr=expr)[columns]

        # base = self.__df.query(expr=expr)[columns]
        base.drop_duplicates(subset=columns[1], inplace=True)
        base.sort_values(by=columns, ignore_index=True, inplace=True)
        return self.__include_empty(base[columns[0]])

    def get_fuels(self):
        return self.__extract_ordened_values_not_duplicates('Produto')

    def get_flags(self) -> pd.Series:
        return self.__extract_ordened_values_not_duplicates('Bandeira')

    def get_amount_records(self) -> int:
        return self.__df.shape[0]

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
