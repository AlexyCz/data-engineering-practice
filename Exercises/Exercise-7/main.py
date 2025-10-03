import os
from zipfile import ZipFile

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import pyspark.sql.types as T
from pyspark.sql.window import Window


def main():
    spark = SparkSession.builder.appName("Exercise7").enableHiveSupport().getOrCreate()
    # your code here
    spark.conf.set('spark.sql.execution.arrow.pyspark.enabled', 'true')
    
    cwd = os.getcwd()  # get current working directory path
    file_path = os.path.join(cwd, 'data/hard-drive-2022-01-01-failures.csv.zip')
    
    spark_df = None
    
    with ZipFile(file_path) as current_zip:
        with current_zip.open('hard-drive-2022-01-01-failures.csv') as failures_csv:
            spark_df = (
                spark
                .read
                .format('csv')
                .option('header', True)
                .schema(FILE_IMPORT_SCHEMA)
                .load(failures_csv)
                # .transform(lambda sdf: rename_columns(sdf, RENAME_MAP))
            )
    
    # TODO: return report.
    return spark_df


if __name__ == "__main__":
    main()
