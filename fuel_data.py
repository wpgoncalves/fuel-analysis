from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Union

import matplotlib.pyplot as plt
import pandas as pd
from numpy import arange, isnan
from typing_extensions import Literal, TypeAlias

from tools import word_capitalize

BASE_DIR = Path(__file__).resolve().parent

Value: TypeAlias = Union['pd.Series', float, None]
DataValue: TypeAlias = Union['pd.DataFrame', 'pd.Series']
StringValue: TypeAlias = Union[str, None]
Operation: TypeAlias = Literal['Mínimo', 'Máximo', 'Médio']
Fuel: TypeAlias = Literal['GASOLINA', 'GASOLINA ADITIVADA']


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

    def __plot_bar(self,
                   df: DataValue,
                   suptitle: StringValue = None,
                   display_bar_label: bool = False,
                   chart_break: bool = False) -> plt.Figure:

        if isinstance(df, pd.Series):
            df = pd.DataFrame(df)
        else:
            if not isinstance(df, pd.DataFrame):
                raise TypeError(
                    f"'{str(df)}' is of type {str(type(df))}, which is not an accepted type."  # noqa: E501
                    " value only accepts: pandas.DataFrame or pandas.Series"
                    " Please convert the value to an accepted type."
                )

        if not isinstance(display_bar_label, bool):
            raise TypeError(
                f"'{str(display_bar_label)}' is of type {str(type(display_bar_label))}, which is not an accepted type."  # noqa: E501
                " value only accepts: bool"
                " Please convert the value to an accepted type."
            )

        if not isinstance(chart_break, bool):
            raise TypeError(
                f"'{str(chart_break)}' is of type {str(type(chart_break))}, which is not an accepted type."  # noqa: E501
                " value only accepts: bool"
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

        if df.shape[0] > 4 and chart_break:
            fig, (ax, ax1) = plt.subplots(
                2,
                1,
                figsize=(11.3, 12),
                layout='tight',
                dpi=600
            )
        else:
            fig, ax = plt.subplots(
                1,
                1,
                figsize=(11.3, 6),
                layout='tight',
                dpi=600
            )

        x = [p - bar_width for p in arange(len(df.index))]

        for column in df.columns:
            h = df[column]
            x = [p + bar_width for p in x]

            if df.shape[0] > 4 and chart_break:
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

                if display_bar_label:
                    ax.bar_label(bar_container,
                                 fmt=self.__currency_format,
                                 padding=1,
                                 rotation=30,
                                 fontweight='light',
                                 fontsize=fs_bar_label)

                    ax1.bar_label(bar_container1,
                                  fmt=self.__currency_format,
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
                if display_bar_label:
                    ax.bar_label(bar_container,
                                 fmt=self.__currency_format,
                                 padding=1,
                                 rotation=30,
                                 fontweight='light',
                                 fontsize=fs_bar_label)

        ax.set_xlabel('Estado(s)', fontweight='book', fontsize=fs_label)

        if df.shape[0] > 4 and chart_break:
            ax1.set_xlabel('Estado(s)', fontweight='book', fontsize=fs_label)

        ax.set_ylabel('Valor Médio de Venda',
                      fontweight='book', fontsize=fs_label)

        if len(df.columns) > 2:
            x = [p - bar_width for p in x]
        elif len(df.columns) % 2 == 0:
            x = [p - (bar_width / 2) for p in x]

        if df.shape[0] > 4 and chart_break:
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

    def get_fuels(self, option_all: bool = True, to_list: bool = False) -> pd.Series | list:  # noqa: E501
        products = pd.Series(self.__df['Produto'].sort_values().unique())

        if not option_all:
            return products if not to_list else products.tolist()

        return self.__include_all_option(products) if not to_list else \
            self.__include_all_option(products).tolist()

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

    def get_chart_sales_value_by_region(self, pyplot_method: Callable) -> None:  # noqa: E501
        columns = ['Regiao - Sigla', 'Produto']
        average_regions = self.__df.groupby(by=columns).mean(
            numeric_only=True).round(3)
        average_regions.drop(['Valor de Compra'], axis=1, inplace=True)
        average_regions = average_regions.unstack(level=1)
        average_regions.columns.names = [None, None]
        average_regions.index.name = None
        average_regions.columns = average_regions.columns.droplevel()

        pyplot_method(self.__plot_bar(average_regions, display_bar_label=True))

    def get_chart_sales_value_by_regions_and_states(self, pyplot_method: Callable) -> None:  # noqa: E501
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

            pyplot_method(
                self.__plot_bar(
                    sheet,
                    f'Região: {regions_dict[region]}',
                    True,
                    True
                )
            )

    def get_ethanol_cost_benefit(self, other_fuel: Fuel = 'GASOLINA', operation: Operation = 'Médio') -> str:  # noqa: E501

        if other_fuel not in ['GASOLINA', 'GASOLINA ADITIVADA']:
            raise ValueError(
                f"'{str(other_fuel)}' is not an accepted value. option only accepts: "  # noqa: E501
                "'GASOLINA' or 'GASOLINA ADITIVADA'"
            )

        if operation not in ['Mínimo', 'Máximo', 'Médio']:
            raise ValueError(
                f"'{str(operation)}' is not an accepted value. option only accepts: "  # noqa: E501
                "'Mínimo', 'Máximo' or 'Médio'"
            )

        ethanol = self.__df.query('Produto == "ETANOL"')['Valor de Venda']
        other = self.__df.query('Produto == @other_fuel')['Valor de Venda']

        match operation:
            case 'Mínimo':
                ethanol = ethanol.min(numeric_only=True)
                other = other.min(numeric_only=True)
            case 'Máximo':
                ethanol = ethanol.max(numeric_only=True)
                other = other.max(numeric_only=True)
            case 'Médio':
                ethanol = ethanol.mean(numeric_only=True)
                other = other.mean(numeric_only=True)

        cost_benefit = round(ethanol / other * 100, 1)
        cost_benefit = cost_benefit if not isnan(cost_benefit) else 0

        return f'{cost_benefit:.1f} %'.replace('.', ',')

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

    def set_fuels(self, fuels: list) -> None:
        self.__df = self.__df[self.__df['Produto'].isin(fuels)]

    def set_flag(self, flag: str) -> None:
        self.__df.query('Bandeira == @flag', inplace=True)
