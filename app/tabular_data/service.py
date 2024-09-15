from collections.abc import Hashable
from typing import Dict, List

import pandas as pd

from app.tabular_data.models import TabularDataFile, TabularDataFileHeader, TabularDataFileRow


class TabularDataService:

    def __init__(self, file):
        self.file = file

    def process_data(self) -> pd.DataFrame:
        """
        Process the tabular data
        """
        df = pd.read_csv(self.file)
        return df

    @staticmethod
    def get_headers(df: pd.DataFrame) -> List[str]:
        """
        Get the headers of the tabular data
        """
        return df.columns.tolist()

    @staticmethod
    def get_rows(df: pd.DataFrame) -> List[Dict[str, any]]:
        """
        Get the rows of the tabular data
        """
        return df.to_dict(orient="records")

    @staticmethod
    def df_from_rows_and_headers(rows: List[Dict[str, any]], headers: List[str]) -> pd.DataFrame:
        """
        Create a DataFrame from rows and headers
        """
        return pd.DataFrame(rows, columns=headers)

    @staticmethod
    def statistics_from_TabularDataFile(tabular_data_file: TabularDataFile) -> Dict[str, Dict]:
        """
        Get statistics from a TabularDataFile
        """
        tabular_data_file_headers = [header.header for header in tabular_data_file.headers]
        tabular_data_file_rows = [row.row_data for row in tabular_data_file.rows]
        df = TabularDataService.df_from_rows_and_headers(tabular_data_file_rows, tabular_data_file_headers)
        return TabularDataService.compute_statistics(df)

    @staticmethod
    def compute_statistics(df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Compute statistics for the tabular data
        """
        numeric_df = df.select_dtypes(include=["number"])

        # Compute statistics
        statistics = {
            "mean": numeric_df.mean().to_dict(),
            "median": numeric_df.median().to_dict(),
            "mode": numeric_df.mode().iloc[0].to_dict(),
            "quartiles": numeric_df.quantile([0.25, 0.5, 0.75]).to_dict(),
            "z_scores": TabularDataService.outliers_z_scores(numeric_df, numeric_df.columns.tolist()).to_dict(),
        }
        return statistics

    @staticmethod
    def outliers_z_scores(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Compute the Z-scores for the outliers
        """
        z_scores = {}
        for column in columns:
            z_scores[column] = TabularDataService.calculate_z_score(df, column)
        return pd.DataFrame(z_scores)

    @staticmethod
    def calculate_z_score(df: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        Calculate the Z-score for a column
        """
        mean = df[column].mean()
        std = df[column].std()
        z_scores = (df[column] - mean) / std
        return z_scores

    @staticmethod
    def detect_outliers(df: pd.DataFrame) -> Dict[Hashable, any]:
        """
        Detect outliers using the IQR method
        """

        """
        Detect outliers using the IQR method
        """
        outliers = {}
        Q1 = df.quantile(0.25)
        Q3 = df.quantile(0.75)
        IQR = Q3 - Q1

        for column in df.columns:
            if pd.api.types.is_numeric_dtype(df[column]):
                lower_bound = Q1[column] - 1.5 * IQR[column]
                upper_bound = Q3[column] + 1.5 * IQR[column]

                column_outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)][column].tolist()
                outliers[column] = column_outliers

        return outliers

    @staticmethod
    def create_tabular_data_file_headers(
        tabular_data_file: TabularDataFile, df: pd.DataFrame
    ) -> List[TabularDataFileHeader]:
        """
        Create tabular data file headers
        """
        tabular_data_file_headers = []
        for index, header in enumerate(TabularDataService.get_headers(df)):
            tabular_data_file_header = TabularDataFileHeader(
                tabular_data_file_id=tabular_data_file.id, header=header, index=index
            )
            tabular_data_file_headers.append(tabular_data_file_header)
        return tabular_data_file_headers

    @staticmethod
    def create_tabular_data_file(name: str, path: str, statistics: Dict[str, Dict]) -> TabularDataFile:
        """
        Create a new tabular data file
        """
        tabular_data_file = TabularDataFile(name=name, path=path, statistics=statistics)
        return tabular_data_file

    @staticmethod
    def create_tabular_data_file_rows(tabular_data_file: TabularDataFile, df: pd.DataFrame) -> List[TabularDataFileRow]:
        """
        Create tabular data file rows
        """
        tabular_data_file_rows = []
        for row_index, row in enumerate(TabularDataService.get_rows(df)):
            tabular_data_file_row = TabularDataFileRow(
                tabular_data_file_id=tabular_data_file.id, row_data=row, index=row_index
            )
            tabular_data_file_rows.append(tabular_data_file_row)
        return tabular_data_file_rows
