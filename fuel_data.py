from datetime import datetime
from pathlib import Path
from typing import Any, Union

import matplotlib.pyplot as plt
import pandas as pd
from numpy import arange, isnan
from typing_extensions import TypeAlias

from tools import word_capitalize

BASE_DIR = Path(__file__).resolve().parent

Value: TypeAlias = Union['pd.Series', float, None]
DataValue: TypeAlias = Union['pd.DataFrame', 'pd.Series']
StringValue: TypeAlias = Union[str, None]


class FuelData():

    __df = pd.DataFrame

    # Constructor
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

    # private methods
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

    def __plot_bar(self, df: DataValue, suptitle: StringValue = None) -> plt.Figure:  # noqa: E501

        if isinstance(df, pd.Series):
            df = pd.DataFrame(df)
        else:
            if not isinstance(df, pd.DataFrame):
                raise TypeError(
                    f"'{str(df)}' is of type {str(type(df))}, which is not an accepted type."  # noqa: E501
                    " value only accepts: pandas.DataFrame or pandas.Series"
                    " Please convert the value to an accepted type."
                )

        if not isinstance(suptitle, str) and suptitle is not None:
            raise TypeError(
                f"'{str(suptitle)}' is of type {str(type(suptitle))}, which is not an accepted type."  # noqa: E501
                " value only accepts: str or None"
                " Please convert the value to an accepted type."
            )

        plt.style.use('Solarize_Light2')

        bar_width = 0.25
        fs_bar_label = 9
        fs_legend = 10
        fs_label = 10
        fs_ticks = 10

        bar_colors = {
            'ETANOL': 'green',
            'GASOLINA': 'orange',
            'GASOLINA ADITIVADA': 'tomato',
        }

        if df.shape[0] > 4:
            fig, (ax, ax1) = plt.subplots(
                2, 1, figsize=(11.3, 12), layout='tight', dpi=300)
        else:
            fig, ax = plt.subplots(1, 1, figsize=(
                11.3, 6), layout='tight', dpi=300)

        x = [p - bar_width for p in arange(len(df.index))]

        for column in df.columns:
            h = df[column]
            x = [p + bar_width for p in x]

            if df.shape[0] > 4:
                bar_container = ax.bar(x[:4],
                                       h[:4],
                                       color=bar_colors[column],
                                       width=bar_width,
                                       edgecolor='white',
                                       linewidth=0.8,
                                       label=word_capitalize(column))

                bar_container1 = ax1.bar(x[4:],
                                         h[4:],
                                         color=bar_colors[column],
                                         width=bar_width,
                                         edgecolor='white',
                                         linewidth=0.8,
                                         label=word_capitalize(column))

                ax.bar_label(bar_container,
                             fmt=lambda x: f'R$ {x:,.2f}'.replace('.', ','),
                             padding=1,
                             rotation=30,
                             fontweight='light',
                             fontsize=fs_bar_label)

                ax1.bar_label(bar_container1,
                              fmt=lambda x: f'R$ {x:,.2f}'.replace('.', ','),
                              padding=1,
                              rotation=30,
                              fontweight='light',
                              fontsize=fs_bar_label)
            else:
                bar_container = ax.bar(x,
                                       h,
                                       color=bar_colors[column],
                                       width=bar_width,
                                       edgecolor='white',
                                       linewidth=0.8,
                                       label=word_capitalize(column))

                ax.bar_label(bar_container,
                             fmt=lambda x: f'R$ {x:,.2f}'.replace('.', ','),
                             padding=1,
                             rotation=30,
                             fontweight='light',
                             fontsize=fs_bar_label)

        ax.set_xlabel('Estado(s)', fontweight='book', fontsize=fs_label)

        if df.shape[0] > 4:
            ax1.set_xlabel('Estado(s)', fontweight='book', fontsize=fs_label)

        ax.set_ylabel('Valor Médio de Venda',
                      fontweight='book', fontsize=fs_label)

        if len(df.columns) > 2:
            x = [p - bar_width for p in x]
        elif len(df.columns) % 2 == 0:
            x = [p - (bar_width / 2) for p in x]

        if df.shape[0] > 4:
            ax.set_xticks(x[:4],
                          df.index[:4],
                          fontsize=fs_ticks,
                          fontweight='regular')

            ax1.set_xticks(x[4:],
                           df.index[4:],
                           fontsize=fs_ticks,
                           fontweight='regular')

            ax.set_yticks([v for v in arange(0, 8, 0.5)],
                          [str(v) for v in arange(0, 8, 0.5)],
                          fontsize=fs_ticks,
                          fontweight='regular')

            ax1.set_yticks([v for v in arange(0, 8, 0.5)],
                           [str(v) for v in arange(0, 8, 0.5)],
                           fontsize=fs_ticks,
                           fontweight='regular')
        else:
            ax.set_xticks(x,
                          df.index,
                          fontsize=fs_ticks,
                          fontweight='regular')

            ax.set_yticks([v for v in arange(0, 8, 0.5)],
                          [str(v) for v in arange(0, 8, 0.5)],
                          fontsize=fs_ticks,
                          fontweight='regular')

        if suptitle is not None:
            fig.suptitle(suptitle)

        handles, labels = ax.get_legend_handles_labels()
        fig.legend(handles=handles, labels=labels, fontsize=fs_legend)

        return fig

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

    def get_chart_sales_value_by_region(self) -> plt.Figure:
        regions = self.get_regions()
        columns = ['Regiao - Sigla', 'Produto']
        average_regions = self.__df.groupby(by=columns).mean(numeric_only=True)
        average_regions.drop(['Valor de Compra'], axis=1, inplace=True)
        average_regions = average_regions.unstack(level=0)
        average_regions.columns.names = [None, None]
        average_regions.index.name = None
        average_regions.columns = average_regions.columns.droplevel()

        plt.style.use('Solarize_Light2')

        barWidth = 0.3
        fs_bar_label = 10
        fs_label = 12
        fs_ticks = 10
        x_eth = None
        x_gas = None
        x_addgas = None
        fig, ax = plt.subplots(figsize=(11.3, 6), layout='tight', dpi=300)

        if 'ETANOL' in average_regions.index:
            h_eth = average_regions.loc['ETANOL'].tolist()
            x_eth = arange(len(h_eth))
            x = x_eth

            bar_container_eth = ax.bar(x_eth,
                                       h_eth,
                                       color='green',
                                       width=barWidth,
                                       edgecolor='white',
                                       linewidth=0.8,
                                       label='Etanol')

            ax.bar_label(bar_container_eth,
                         fmt=lambda x: f'R$ {x:,.2f}'.replace('.', ','),
                         fontweight='light',
                         fontsize=fs_bar_label)

        if 'GASOLINA' in average_regions.index:
            h_gas = average_regions.loc['GASOLINA'].tolist()

            if x_eth is not None:
                x_gas = [x + barWidth for x in x_eth]
            elif x_eth is None:
                x_gas = arange(len(h_gas))  # type: ignore
                x = x_gas  # type: ignore

            bar_container_gas = ax.bar(x_gas,
                                       h_gas,
                                       color='orange',
                                       width=barWidth,
                                       edgecolor='white',
                                       linewidth=0.8,
                                       label='Gasolina')

            ax.bar_label(bar_container_gas,
                         fmt=lambda x: f'R$ {x:,.2f}'.replace('.', ','),
                         fontweight='light',
                         fontsize=fs_bar_label)

        if 'GASOLINA ADITIVADA' in average_regions.index:
            h_addgas = average_regions.loc['GASOLINA ADITIVADA'].tolist()

            if x_gas is not None:
                x_addgas = [x + barWidth for x in x_gas]
            elif x_gas is None:
                if x_eth is not None:
                    x_addgas = [x + barWidth for x in x_eth]
                else:
                    x_addgas = arange(len(h_addgas))  # type: ignore
                    x = x_addgas  # type: ignore

            bar_container_added_gas = ax.bar(x_addgas,
                                             h_addgas,
                                             color='tomato',
                                             width=barWidth,
                                             edgecolor='white',
                                             linewidth=0.8,
                                             label='Gasolina Aditivada')

            ax.bar_label(bar_container_added_gas,
                         fmt=lambda x: f'R$ {x:,.2f}'.replace('.', ','),
                         fontweight='light',
                         fontsize=fs_bar_label)

        ax.set_xlabel('Região(ões)', fontweight='book', fontsize=fs_label)

        ax.set_ylabel('Valor Médio de Venda',
                      fontweight='book', fontsize=fs_label)

        if average_regions.shape[0] > 1:
            ax.set_xticks([r + barWidth for r in range(len(x))],
                          regions, fontsize=fs_ticks, fontweight='regular')
        else:
            ax.set_xticks([r for r in range(len(x))],
                          regions, fontsize=fs_ticks, fontweight='regular')

        ax.set_yticks([v for v in arange(0, 8, 0.5)],
                      [str(v) for v in arange(0, 8, 0.5)],
                      fontsize=fs_ticks, fontweight='regular')

        fig.legend()

        return fig

    def get_chart_sales_value_by_regions_and_states(self, pyplot_method):
        columns = ['Regiao - Sigla', 'Estado - Sigla', 'Produto']
        average_states = self.__df.groupby(by=columns).mean(
            numeric_only=True).round(3)
        average_states.drop(['Valor de Compra'], axis=1, inplace=True)
        average_states = average_states.unstack(level=2)
        regions = average_states.index.get_level_values(level=0).unique()

        for region in regions:
            sheet = average_states.loc[region]
            sheet.columns = sheet.columns.droplevel(level=0)
            sheet.columns.name = None
            sheet.index.name = None

            regions_dict = {
                'CO': 'Centro-Oeste',
                'N': 'Norte',
                'NE': 'Nordeste',
                'S': 'Sul',
                'SE': 'Sudeste'
            }

            pyplot_method(self.__plot_bar(
                sheet, f'Região: {regions_dict[region]}'))

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
