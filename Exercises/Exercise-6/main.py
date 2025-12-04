import os
from zipfile import ZipFile

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions as F
from pyspark.sql.types as T
from pyspark.sql.window import Window

REPORTS = {
    1: "daily_trip_dur.csv",
    2: "daily_num_trips.csv",
    3: "monthly_top_stations.csv",
    4: "two_week_top_three_stations.csv",
    5: "gender_trip_length.csv",
    6: "top_ten_ages_long_short_trips.csv"
}


def top_ten_ages(sdf):
    # generate report 6
    # ? top 10 ages: longest trips, shortest trips
    # sort by trip duration, desc.
    # take top 10, and final 10
    # get ages column
    # merge into one df, sorted on trip duration, desc
    # or or
    # we can group by age, avg agg respectively on their trip durations, and take top + bottom 10 of ages when sorted desc on avg trip duration.
    #
    valid_sdf = sdf.filter(sdf.birthyear.isNotNull())
    ages_sdf = sdf.withColumn('age', F.floor(F.months_between(F.current_date() - F.col('birthyear')) / 12).cast(T.IntegerType()))
    ages_sdf = ages_sdf.groupBy('age').agg(F.avg(ages_sdf.trip_duration).alias('age_avg_trip_duration'))

    top_ten_sdf = ages_sdf.orderBy(F.col('age_avg_trip_duration').desc()).limit(10)
    bottom_ten_sdf = ages_sdf.orderBy(F.col('age_avg_trip_duration').asc()).limit(10)
    top_bottom_ten_sdf = bottom_ten_sdf.union(top_ten_sdf)  # output csv...


def avg_trip_by_gender(sdf):
    # generate report 5
    # do males or females take longer trips...
    # drop any NA gender valued rows
    # group by male and agg avg their trip duration and alias new col
    # group by female and agg avg their trip duration and alias new col
    # rank the counts and output

    valid_sdf = sdf.filter(sdf.gender.isNotNull())
    gender_avg_trip_sdf = valid_sdf.groupBy('gender').agg(F.avg(valid_sdf.trip_duration).alias('gender_avg_trip_duration'))  # output csv...


def top_three_daily_stations(sdf):
    # generate report 4
    #
    # find final timestamp and backtrack two weeks. use methodology of above, but limit 3 instead and group by day.
    sorted_sdf = sdf.sort(F.col('start_time').desc())
    sorted_sdf = sorted_sdf.withColumn('last_day', F.lit(sorted_sdf.first()['start_time']))
    last_2w_sdf = sorted_sdf.filter(F.datediff(sorted_sdf.last_day - sorted_sdf.start_time) < 15)

    last_2w_sdf = last_2w_sdf.withColumn('start_date', F.to_date(last_2w_sdf.start_time))
    last_2w_sdf = last_2w_sdf.groupBy('start_date', 'start_station_id').agg(F.count().alias('day_visit_count'))
    window = Window.partitionBy('start_date').orderBy(F.col('day_visit_count').desc())

    top_three_daily_station_sdf = last_2w_sdf.withColumn('rank', F.dense_rank().over(window)).filter(F.col('rank') < 4).drop('rank')  # output csv

    # sdf = sdf.na.fill('0', subset=['tripduration'])  # fill in empty durations
    # sdf = sdf.na.drop('all', subset=['end_time'])  # drop any missing timestamps; needed for aggregation
    #


def top_station_monthly(sdf):
    # generate report 3
    # make a month-year column to aggregate for popular station
    # use windows to go with dense_rank()
    month_station_sdf = sdf.withColumn('start_month_date', F.to_date(sdf.start_time, 'MM/yyyy'))
    # popularStartStation_sdf = sdf.groupBy('start_month_date', 'start_station_name').agg(F.count().alias('station_count')).sort(F.col('station_count').desc()).limit(1).select('month_date', 'start_station_name')
    station_count_sdf = month_station_sdf.groupBy('start_month_date', 'start_station_id').agg(F.count().alias('month_visit_count'))
    window = Window.partitionBy('start_month_date').orderBy(F.col('month_visit_count').desc())  # could add additional arg describing to order by alphabet to have a definite first.

    top_station_monthly_sdf = station_count_sdf.withColumn('rank', F.dense_rank().over(window)).filter(F.col('rank') == 1).drop('rank')  # output csv...

def trip_count_per_day(sdf):
    # generate report 2
    countTripsByDay_sdf = sdf.groupBy('end_date').withColumn('trip_count', F.count('trip_id')).select(F.col('end_date'), F.col('trip_count'))  # output csv...


def avg_trip_per_day(sdf):
    # generate report 1
    # what is the avg trip duration per day?
    # find all null tripduration values, and attempt to calulcate. then join that df to complete df on trip_id
    emptyTripDur_sdf = sdf.filter(sdf.tripduration.isNull())
    # cast as a `double` to increase precision past integer values.
    calculatedTripDur_sdf = emptyTripDur_sdf.withColumn('tripduration',
                                       F.col('end_time').cast(T.DoubleType()) - F.col('start_time').cast(T.DoubleType()))
    # join the dataframes on trip id
    sdf = sdf.join(calculatedTripDur_sdf, on = (sdf.trip_id) == calculatedTripDur_sdf.trip_id, how = 'outer')
    # make a date column
    sdf = sdf.withColumn('end_date', F.col('end_time').cast(T.DateType()))

    avgTripDurationDay_sdf = (sdf.groupBy('end_date').agg(F.avg(sdf.tripduration).alias('trip_duration')).select(F.col('end_date'), F.col('trip_duration')))  # output csv...

    avgTripDurationDay_sdf.coalesce(1).write.mode('overwrite').option('header', 'true').csv('/reports/report_1')
    
    return


def main():
    spark = SparkSession.builder.appName("Exercise6").enableHiveSupport().getOrCreate()

    spark.conf.set('spark.sql.execution.arrow.pyspark.enabled', 'true')

    cwd = os.getcwd()
    path_0, path_1 = os.path.join(cwd, 'Divvy_Trips_2019_Q4.zip'), os.path.join(cwd, 'Divvy_Trips_2020_Q1.zip')

    sdf_0, sdf_1 = None, None

    FILE_IMPORT_SCHEMA = T.StructType([
        T.StructField('ride_id', T.StringType(), True),
        T.StructField('trip_id', T.StringType(), True),
        T.StructField('rideable_type', T.StringType(), True),
        T.StructField('started_at', T.TimestampType(), True),
        T.StructField('start_time', T.TimestampType(), True),
        T.StructField('ended_at', T.TimestampType(), True),
        T.StructField('end_time', T.TimestampType(), True),
        T.StructField('start_station_name', T.StringType(), True),
        T.StructField('from_station_name', T.StringType(), True),
        T.StructField('start_station_id', T.StringType(), True),
        T.StructField('from_station_id', T.StringType(), True),
        T.StructField('end_station_name', T.StringType(), True),
        T.StructField('to_station_name', T.StringType(), True),
        T.StructField('end_station_id', T.StringType(), True),
        T.StructField('to_station_id', T.StringType(), True),
        T.StructField('start_lat', T.FloatType(), True),
        T.StructField('start_lng', T.FloatType(), True),
        T.StructField('end_lat', T.FloatType(), True),
        T.StructField('end_lng', T.FloatType(), True),
        T.StructField('member_casual', T.StringType(), True),
        T.StructField('bikeid', T.StringType(), True),
        T.StructField('tripduration', T.FloatType(), True),
        T.StructField('usertype', T.StringType(), True),
        T.StructField('gender', T.StringType(), True),
        T.StructField('birthyear', T.DateType(), True),

    ])

    RENAME_MAP = {
        'ride_id': 'trip_id',
        'started_at': 'start_time',
        'ended_at': 'end_time',
        'from_station_name': 'start_station_name',
        'from_station_id': 'start_station_id',
        'to_station_name': 'end_station_name',
        'to_station_id': 'end_station_id'
    }

    # helper for renaming columns for a seamless join
    def rename_columns(df, renameMap):
        for name, rename in renameMap.items():
            df = df.withColumnRenamed(name, rename)
        return df


    # unzip
    with ZipFile(path_0) as czip:
        with czip.open('Divvy_Trips_2019_Q4.csv') as csv_0:
            sdf_0 = (
                spark
                .read
                .format('csv')
                .option('header', True)
                .schema(FILE_IMPORT_SCHEMA)
                .load(csv_0)
                .transform(lambda sdf: rename_columns(sdf, RENAME_MAP))
            )

    with ZipFile(path_1) as czip:
        with czip.open('Divvy_Trips_2020_Q1.csv') as csv_1:
            sdf_1 = (
                spark
                .read
                .format('csv')
                .option('header', True)
                .schema(FILE_IMPORT_SCHEMA)
                .load(csv_1)
                .transform(lambda sdf: rename_columns(sdf, RENAME_MAP))
            )

    sdf = sdf_0.join(sdf_1, how='outer')

    avg_trip_per_day(sdf)

    trip_count_per_day(sdf)

    top_station_monthly(sdf)

    top_three_daily_stations(sdf)

    avg_trip_by_gender(sdf)

    top_ten_ages(sdf)
    
    return


if __name__ == "__main__":
    main()
