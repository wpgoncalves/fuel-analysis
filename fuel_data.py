from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from numpy import arange, isnan
from typing_extensions import Literal, TypeAlias

from custom_exceptions import ExcessValues
from settings import DATE_END, DATE_START
from tools import word_capitalize

BASE_DIR = Path(__file__).resolve().parent

Value: TypeAlias = Union['pd.Series', float, None]
DataValue: TypeAlias = Union['pd.DataFrame', 'pd.Series']
ArrayType: TypeAlias = Union[pd.Series, np.ndarray]
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
            df['Data da Coleta'],
            exact=True,
            dayfirst=True,
            infer_datetime_format=True,
            format='%d/%m/%Y',
            errors='coerce'
        )

        df['Valor de Venda'] = df['Valor de Venda'].str.replace(
            ',',
            '.',
            regex=False
        )

        df['Valor de Venda'] = pd.to_numeric(
            df['Valor de Venda'],
            errors='coerce',
            downcast='float'
        )

        df['Valor de Compra'] = pd.to_numeric(
            df['Valor de Compra'],
            errors='coerce',
            downcast='float'
        )

        df.fillna(value={'Valor de Compra': 0}, inplace=True)

        df.drop(
            [
                'Nome da Rua',
                'Numero Rua',
                'Complemento',
                'Bairro',
                'Cep',
                'Unidade de Medida'
            ],
            axis=1,
            inplace=True
        )

        self.__df = df[df['Produto'].isin(
            ['GASOLINA', 'GASOLINA ADITIVADA', 'ETANOL']
        )]

    # private methods
    def __include_all_option(self, array: ArrayType) -> ArrayType:

        if isinstance(array, pd.Series):
            empty = pd.Series(['Todos'], dtype='object')
            return pd.concat([empty, array], ignore_index=True)
        elif isinstance(array, np.ndarray):
            empty = np.array(['Todos'], dtype=object)
            return np.concatenate([empty, array])
        else:
            raise TypeError(
                f"'{str(array)}' is of type {str(type(array))}, which is not an accepted type."  # noqa: E501
                " value only accepts: pandas.Series and numpy.ndarray"
                " Please convert the value to an accepted type."
            )

    def __currency_format(self, value: Value) -> Any:
        if value is None:
            value = "—"
        elif isinstance(value, pd.Series):
            value = value.map('R$ {:,.2f}'.format)
            value = pd.Series(value, dtype='string')
            value = value.str.replace('.', ',', regex=False)
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
    def get_dataframe(self,
                      columns: list = [],
                      capitalize: bool = False,
                      format: bool = False
                      ) -> pd.DataFrame:

        columns_raw = self.__df.columns.tolist()

        if len(columns) > 0:
            for column in columns:
                if column not in columns_raw:
                    raise ValueError(
                        f"'{str(column)}' is not an accepted value. Option only accepts: "  # noqa: E501
                        "'Regiao - Sigla', 'Estado - Sigla', 'Municipio', 'Revenda', "  # noqa: E501
                        "'CNPJ da Revenda', 'Produto', 'Data da Coleta', 'Valor de Venda', "  # noqa: E501
                        "'Valor de Compra' or 'Bandeira'"
                    )

        if len(columns) == 0:
            columns = columns_raw

        new_df = self.__df[columns].copy()

        if capitalize:
            if 'Municipio' in columns:
                new_df['Municipio'] = new_df['Municipio'].map(word_capitalize)

            if 'Revenda' in columns:
                new_df['Revenda'] = new_df['Revenda'].map(word_capitalize)

            if 'Produto' in columns:
                new_df['Produto'] = new_df['Produto'].map(word_capitalize)

            if 'Bandeira' in columns:
                new_df['Bandeira'] = new_df['Bandeira'].map(word_capitalize)

        if format:
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

    def get_regions(self) -> np.ndarray:
        base = self.__df['Regiao - Sigla'].unique()
        return np.sort(base)

    def get_states(self, regions: list = []) -> np.ndarray:
        base = self.__df.copy()

        if regions != []:
            base.query('`Regiao - Sigla` == @regions', inplace=True)

        return np.sort(base['Estado - Sigla'].unique())

    def get_cities(self, states: list = [], option_all: bool = False) -> np.ndarray:  # noqa: E501
        base = self.__df.copy()

        if states != []:
            base.query('`Estado - Sigla` == @states', inplace=True)

        base = np.sort(base['Municipio'].unique())

        return base if not option_all else self.__include_all_option(base)

    def get_resales(self, sets: dict = None, option_all: bool = True) -> np.ndarray:  # type: ignore # noqa: E501
        df = self.set_fuel(sets)
        subset = df['CNPJ da Revenda'].isin(df['CNPJ da Revenda'].unique())  # type: ignore # noqa: E501
        resales = df[subset][['Revenda', 'CNPJ da Revenda']]  # type: ignore # noqa: E501
        resales = np.sort(resales['Revenda'].unique())
        return self.__include_all_option(resales) if option_all else resales

    def get_fuels(self, sets: dict = None) -> np.ndarray:  # type: ignore
        return np.sort(self.set_fuel(sets)['Produto'].unique())  # type: ignore

    def get_flags(self, sets: dict = None) -> np.ndarray:  # type: ignore
        return np.sort(self.set_fuel(sets)['Bandeira'].unique())  # type: ignore # noqa: E501

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

    def get_chart_sales_value_by_cities(self) -> plt.Figure:
        columns = ['Municipio', 'Produto', 'Valor de Venda']
        data = self.get_dataframe(columns, True)
        number_cities = data['Municipio'].unique().shape[0]

        if number_cities > 4:
            raise ExcessValues(
                f'This search generated many results, about {number_cities}'
                ' cities were selected, so it is not possible to display the'
                ' information clearly. A maximum of 4 cities must be selected'
                ' for information to be displayed.'
            )

        fs_bar_label = 9
        fs_legend = 10
        fs_label = 10
        fs_ticks = 10

        sns.set_theme(
            context='notebook',
            style='darkgrid',
            palette='pastel'
        )

        fuel_colors = {
            'Etanol': 'green',
            'Gasolina': 'orange',
            'Gasolina Aditivada': 'tomato',
        }

        order_fuels = ['Etanol', 'Gasolina', 'Gasolina Aditivada']

        fig, ax = plt.subplots(
            figsize=(11.3, 6),
            dpi=600
        )

        ax.set_yticks(
            [v for v in arange(0, 6, 0.5)],
            [f'R$ {v:.2f}'.replace('.', ',') for v in arange(0, 6, 0.5)],
            fontsize=fs_ticks,
            fontweight='regular'
        )

        sns.barplot(
            data=data,
            x='Municipio',
            y='Valor de Venda',
            hue='Produto',
            hue_order=order_fuels,
            errorbar=None,
            palette=fuel_colors,
            ax=ax
        )

        plt.xticks(
            rotation=15,
            ha='center',
            fontsize=fs_ticks
        )

        plt.xlabel(
            'Município(s)',
            fontsize=fs_label,
            fontweight='book'
        )

        plt.ylabel(
            'Valores de Venda',
            fontsize=fs_label,
            fontweight='book'
        )

        plt.legend(
            shadow=True,
            fontsize=fs_legend,
            bbox_to_anchor=(1, 1, 0, 0.2)
        )

        for bars in ax.containers:
            ax.bar_label(
                bars,
                fmt=self.__currency_format,
                padding=1,
                rotation=0,
                fontweight='light',
                fontsize=fs_bar_label
            )

        plt.tight_layout()

        return fig

    def get_chart_sales_value_by_flags(self) -> plt.figure:
        columns = ['Bandeira', 'Produto', 'Valor de Venda']
        data = self.get_dataframe(columns, True)
        number_flags = data['Bandeira'].unique().shape[0]

        if number_flags > 5:
            raise ExcessValues(
                f'This search generated many results, about {number_flags}'
                ' flags were selected, so it is not possible to display the'
                ' information clearly. A maximum of 5 flags must be selected'
                ' for information to be displayed.'
            )

        fs_bar_label = 9
        fs_legend = 10
        fs_label = 10
        fs_ticks = 10

        sns.set_theme(
            context='notebook',
            style='darkgrid',
            palette='pastel'
        )

        fig, ax = plt.subplots(
            figsize=(11.3, 6),
            dpi=600
        )

        ax.set_yticks(
            [v for v in arange(0, 6, 0.5)],
            [f'R$ {v:.2f}'.replace('.', ',') for v in arange(0, 6, 0.5)],
            fontsize=fs_ticks,
            fontweight='regular'
        )

        sns.barplot(
            x='Bandeira',
            y='Valor de Venda',
            data=data,
            hue='Produto',
            estimator='mean',
            errorbar=None,
            palette=['green', 'orange', 'tomato'],
            ax=ax
        )

        plt.xticks(
            rotation=15,
            ha='center',
            fontsize=fs_ticks
        )

        plt.xlabel(
            'Bandeira(s)',
            fontsize=fs_label,
            fontweight='book'
        )

        plt.ylabel(
            'Valores de Venda',
            fontsize=fs_label,
            fontweight='book'
        )

        plt.legend(
            shadow=True,
            fontsize=fs_legend,
            bbox_to_anchor=(1, 1, 0, 0.2)
        )

        for bars in ax.containers:
            ax.bar_label(
                bars,
                fmt=self.__currency_format,
                padding=1,
                rotation=0,
                fontweight='light',
                fontsize=fs_bar_label
            )

        plt.tight_layout()

        return fig

    def get_chart_evolution_of_sales_values_over_time(self):
        columns = ['Produto', 'Data da Coleta', 'Valor de Venda']

        data = self.__df[columns].copy()
        data['Produto'] = data['Produto'].map(word_capitalize)

        months = {
            1: 'Janeiro',
            2: 'Fevereiro',
            3: 'Março',
            4: 'Abril',
            5: 'Maio',
            6: 'Junho',
            7: 'Julho',
            8: 'Agosto',
            9: 'Setembro',
            10: 'Outubro',
            11: 'Novembro',
            12: 'Dezembro'
        }

        if 'Mes' in data.columns:
            data.drop(columns=['Mes'], axis=1, inplace=True)

        dates = pd.DatetimeIndex(data['Data da Coleta'])
        data['Mes'] = dates.month.map(months)

        inicial_date = data['Data da Coleta'].min()
        final_date = data['Data da Coleta'].max()
        delta = final_date - inicial_date

        x = 'Mes' if delta.days > 45 else 'Data da Coleta'

        sns.set_theme(
            context='notebook',
            style='darkgrid',
            palette='pastel'
        )

        fuel_colors = {
            'Etanol': 'green',
            'Gasolina': 'orange',
            'Gasolina Aditivada': 'tomato',
        }

        order_fuels = ['Etanol', 'Gasolina', 'Gasolina Aditivada']

        chart = sns.relplot(
            x=x,
            y='Valor de Venda',
            data=data,
            col_order=order_fuels,
            style='Produto',
            hue='Produto',
            estimator='mean',
            palette=fuel_colors,
            kind='line',
            markers=True,
            dashes=False,
            legend=True,
            height=6,
            aspect=1.55,
            errorbar=None
        )

        chart.set_xticklabels(rotation=15, ha='center')

        chart.tight_layout(w_pad=0)

        return chart.fig

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
        self.__df.query('`Regiao - Sigla` == @regions', inplace=True)

    def set_state(self, state: str) -> None:
        self.__df.query('`Estado - Sigla` == @state', inplace=True)

    def set_county(self, county: str) -> None:
        self.__df.query('Municipio == @county', inplace=True)

    def set_resale(self, resale: str) -> None:
        self.__df.query('Revenda == @resale', inplace=True)

    def set_fuels(self, fuels: list) -> None:
        self.__df.query('Produto == @fuels', inplace=True)

    def set_flags(self, flags: list) -> None:
        self.__df.query('Bandeira == @flags', inplace=True)

    def set_fuel(self, sets: dict = None, inplace: bool = False) -> pd.DataFrame | None:  # type: ignore # noqa: E501

        _default = {
            'cities': None,
            'flags': None,
            'fuels': None,
            'period': (DATE_START, DATE_END),
            'regions': None,
            'resales': None,
            'states': None
        }

        _filters = {
            'cities': "Municipio == @sets.get('cities')",
            'flags': "Bandeira == @sets.get('flags')",
            'fuels': "Produto == @sets.get('fuels')",
            'period': "`Data da Coleta` >= @sets.get('period')[0] & `Data da Coleta` <= @sets.get('period')[1]",  # noqa: E501
            'regions': "`Regiao - Sigla` == @sets.get('regions')",
            'resales': "Revenda == @sets.get('resales')",
            'states': "`Estado - Sigla` == @sets.get('states')"
        }

        if sets is None:
            sets = _default

        if isinstance(sets, dict):
            keys_sets = list(sets.keys())
            keys_sets.sort()

            keys_default = list(_default.keys())
            keys_default.sort()

            if keys_sets != keys_default:
                raise ValueError(
                    "All keys must be declared."
                    " The dictionary must contain all of the following keys: 'period', 'regions', 'states', 'cities', 'resales', 'fuels', 'flags'."  # noqa: E501
                    " Even if you don't need to use a certain key, you must declare it with a value of type None."  # noqa: E501
                )
        else:
            raise TypeError(
                f"'{str(sets)}' is of type '{str(type(sets))}', which is not an accepted type."  # noqa: E501
                " value only accepts: dict only"
                " Please convert the value to an accepted type."
            )

        if sets.get('cities') == ['Todos'] or sets.get('cities') == []:
            sets.update({'cities': None})

        if sets.get('flags') == ['Todos'] or sets.get('flags') == []:
            sets.update({'flags': None})

        if sets.get('fuels') == ['Todos'] or sets.get('fuels') == []:
            sets.update({'fuels': None})

        if sets.get('period') is None or sets.get('period') == ():
            sets.update({'period': (DATE_START, DATE_END)})

        if sets.get('regions') == ['Todos'] or sets.get('regions') == []:
            sets.update({'regions': None})

        if sets.get('resales') == ['Todos'] or sets.get('resales') == []:
            sets.update({'resales': None})

        if sets.get('states') == ['Todos'] or sets.get('states') == []:
            sets.update({'states': None})

        keys = list(sets.keys())
        keys.sort()
        expr = ''

        for key in keys:
            if sets.get(key) is not None:
                expr += _filters.get(key) if expr == '' else f' & {_filters.get(key)}'  # type: ignore # noqa: E501

        _df = self.__df.query(expr=expr, inplace=inplace)

        return None if inplace else _df
