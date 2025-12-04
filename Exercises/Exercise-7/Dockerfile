FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y default-jdk scala wget vim software-properties-common python3.9 python3-pip curl unzip libpq-dev build-essential libssl-dev libffi-dev python3-dev && \
    apt-get clean

RUN wget https://archive.apache.org/dist/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz && \
    tar xvf spark-3.5.0-bin-hadoop3.tgz && \
    mv spark-3.5.0-bin-hadoop3/ /usr/local/spark && \
    ln -s /usr/local/spark /usr/bin/spark && \
    wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar && \
    mv aws-java-sdk-bundle-1.12.262.jar /usr/local/spark/jars && \
    wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    mv hadoop-aws-3.3.4.jar /usr/local/spark/jars


WORKDIR /app
COPY . /app

RUN pip3 install --upgrade pip && \
    pip3 install markupsafe==2.0.1 cryptography==38.0.4 cython==0.29.32 numpy==1.21.6 && \
    pip3 install -r requirements.txt

ENV PYSPARK_PYTHON=python3
ENV PYSPARK_SUBMIT_ARGS='--packages io.delta:delta-core_2.12:2.4.0 pyspark-shell'
