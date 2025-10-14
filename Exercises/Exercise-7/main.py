import os
from zipfile import ZipFile

from pyspark.sql import SparkSession, DataFrame
import pyspark.sql.functions as F
import pyspark.sql.types as T
from pyspark.sql.window import Window


def main():
    spark = SparkSession.builder.appName("Exercise7").enableHiveSupport().getOrCreate()
    # your code here
    spark.conf.set('spark.sql.execution.arrow.pyspark.enabled', 'true')
    
    cwd = os.getcwd()  # get current working directory path
    file_path = os.path.join(cwd, 'data/hard-drive-2022-01-01-failures.csv.zip')
    
    s_df = None
    
    s_df = extract_csv(s_df, file_path, spark)
    
    s_df = extract_date_from_file(s_df)
    
    s_df = extract_brand_from_model(s_df)

    return s_df


def extract_csv(s_df: DataFrame, file_path: str, spark: SparkSession) -> DataFrame:
    '''
    Extracts the compressed CSV file in memory;
    During load, file name is extracted to 'source_file' column;
    '''

    with ZipFile(file_path) as current_zip:
        with current_zip.open('hard-drive-2022-01-01-failures.csv') as failures_csv:
            s_df = (
                spark
                .read
                .format('csv')
                .option('header', True)
                .load(failures_csv)
                .withColumn('source_file', F.input_file_name())
            )
    
    return s_df


def extract_date_from_file(s_df: DataFrame) -> DataFrame:
    '''
    Pulls date in date data-type from file name in column 'source_file'
    '''

    s_df = s_df.withColumn('file_date', F.to_date(
        F.regexp_extract('source_file', F.regexp_extract(r'\d{4}-\d{2}=\d{2}', 1)), 'yyyy-MM--dd'))
    
    return s_df


def extract_brand_from_model(s_df: DataFrame) -> DataFrame:
    '''
    Brand is based off hardrive model value provided;
    Space delimited, where first string value is brand, else unknown;
    
    have:
        ltrim(col)
        Trim the spaces from left end for the specified string value.
        
        regexp_extract(str, pattern, idx)
        Extract a specific group matched by a Java regex, from the specified string column.
        
        split(str, pattern[, limit])
        Splits str around matches of the given pattern.
        split("text", "\\s+")  # Split on one or more whitespace characters
    '''
    
    s_df = (s_df.withColumn('model_name_split', F.split(F.ltrim(F.col('model')), ' '))
                .withColumn('brand',
                    F.when(F.size('model_name_split') > 1, F.col('model_name_split')[0])
                    .otherwise(T.lit('unknown'))
                )
                .drop('model_name_split')
            )

    return s_df


def calculating_storage_ranking(s_df: DataFrame) -> DataFrame:
    '''
    We have column `capacity_bytes` and column `model`. The aim is to get storage capacity rankings
    for present models in the data based off the capacity provided.
    '''
    pass


if __name__ == "__main__":
    main()
