#!/usr/bin/env python3
"""Simple PySpark test script"""

import os
import sys
from pyspark.sql import SparkSession
from pyspark import SparkConf

def test_spark():
    """Test basic Spark functionality"""
    
    # Set minimal configuration for testing
    conf = SparkConf()
    conf.setAppName("HedgeyeKB-Test")
    conf.setMaster("local[1]")  # Single-threaded local mode
    conf.set("spark.sql.adaptive.enabled", "false")  # Disable adaptive query execution
    conf.set("spark.sql.adaptive.coalescePartitions.enabled", "false")
    conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    
    print("Creating SparkSession...")
    try:
        spark = SparkSession.builder.config(conf=conf).getOrCreate()
        print(f"✓ Spark version: {spark.version}")
        print(f"✓ Spark UI available at: {spark.sparkContext.uiWebUrl}")
        
        # Test basic DataFrame operations
        print("\nTesting basic DataFrame operations...")
        data = [("Alice", 25), ("Bob", 30), ("Charlie", 35)]
        columns = ["name", "age"]
        df = spark.createDataFrame(data, columns)
        
        print("✓ DataFrame created successfully")
        print(f"✓ Row count: {df.count()}")
        
        # Show data
        print("\nData preview:")
        df.show()
        
        # Test basic SQL
        df.createOrReplaceTempView("people")
        result = spark.sql("SELECT name, age FROM people WHERE age > 25")
        print("\nSQL query result:")
        result.show()
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        if 'spark' in locals():
            spark.stop()
            print("✓ SparkSession stopped")
    
    return True

if __name__ == "__main__":
    success = test_spark()
    sys.exit(0 if success else 1)