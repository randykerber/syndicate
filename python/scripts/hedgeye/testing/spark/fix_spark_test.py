#!/usr/bin/env python3
"""Test Spark with ultra-minimal configuration"""

import os
import sys
import signal

# Set timeout handler
def timeout_handler(signum, frame):
    print("❌ Test timed out after 60 seconds")
    sys.exit(1)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(60)  # 60 second timeout

# Set Java 17 explicitly
os.environ['JAVA_HOME'] = '/usr/local/Cellar/openjdk@17/17.0.15/libexec/openjdk.jdk/Contents/Home'

# Ultra-minimal Spark configuration
os.environ['SPARK_LOCAL_IP'] = '127.0.0.1'
os.environ['PYSPARK_SUBMIT_ARGS'] = '--master local[1] --driver-memory 512m --conf spark.ui.enabled=false --conf spark.driver.host=127.0.0.1 pyspark-shell'

print(f"JAVA_HOME: {os.environ.get('JAVA_HOME')}")
print(f"Python: {sys.version}")

try:
    print("Step 1: Importing PySpark...")
    from pyspark.sql import SparkSession
    from pyspark import SparkConf
    print("✅ PySpark imports successful")
    
    print("Step 2: Creating SparkConf...")
    conf = SparkConf()
    conf.setAppName("ultra-minimal-test")
    conf.setMaster("local[1]")
    conf.set("spark.driver.host", "127.0.0.1")
    conf.set("spark.driver.bindAddress", "127.0.0.1")
    conf.set("spark.ui.enabled", "false")
    conf.set("spark.driver.memory", "512m")
    conf.set("spark.executor.memory", "512m")
    print("✅ SparkConf created")
    
    print("Step 3: Creating SparkSession (this is where it usually hangs)...")
    # Try with even more restrictive settings
    conf.set("spark.sql.warehouse.dir", "/tmp/spark-warehouse")
    conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    conf.set("spark.sql.adaptive.enabled", "false")
    conf.set("spark.sql.adaptive.coalescePartitions.enabled", "false")
    conf.set("spark.dynamicAllocation.enabled", "false")
    
    spark = SparkSession.builder.config(conf=conf).getOrCreate()
    
    print(f"🎉 SUCCESS! Spark version: {spark.version}")
    
    # Cancel the alarm since we succeeded
    signal.alarm(0)
    
    # Quick test
    print("Step 4: Running basic test...")
    data = [1, 2, 3]
    rdd = spark.sparkContext.parallelize(data)
    result = rdd.sum()
    print(f"✅ Test calculation: sum of {data} = {result}")
    
    spark.stop()
    print("✅ Spark stopped successfully")
    
except Exception as e:
    signal.alarm(0)  # Cancel alarm
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()