import os

import duckdb
import boto3

con = duckdb.connect(database=':memory:', config={'memory_limit': '9GB','worker_threads': 5,'temp_directory':'/tmp'})
ext_dir = os.environ.get('DUCKDB_EXT_DIR');
print(con.execute(f"SET home_directory='{ext_dir}'").fetchall())
# 验证设置
result = con.execute("SELECT current_setting('home_directory')").fetchone()[0]
print(f"Home directory: {result}")
con.execute("""
CREATE SECRET (
    TYPE s3,
    PROVIDER credential_chain
);
""")
s3tables = boto3.client('s3tables')
table_buckets = s3tables.list_table_buckets(maxBuckets=1000)['tableBuckets']
for table_bucket in table_buckets:
    name = table_bucket['name']
    arn = table_bucket['arn']
    con.execute(
        f"""
        ATTACH '{arn}' AS {name} (
        TYPE iceberg,
        ENDPOINT_TYPE s3_tables
    );
        """
    )
def handler(event, context):
    sql = event.get("sql")
    try:
        result = con.execute(sql).fetchall()
        return {
            "statusCode": 200,
            "result": result
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "error": str(e)
        }
