import os

import duckdb
import boto3
os.environ['HOME'] = '/tmp'
con = duckdb.connect(database=':memory:', config={'memory_limit': '9GB','worker_threads': 5,'temp_directory':'/tmp/file/overmem'})
# 验证设置
con.execute("""
FORCE INSTALL aws;
FORCE INSTALL httpfs;
FORCE INSTALL iceberg;
CREATE SECRET (
    TYPE s3,
    PROVIDER credential_chain
);
""")
s3tables = boto3.client('s3tables')
table_buckets = s3tables.list_table_buckets(maxBuckets=1000)['tableBuckets']

def handler(event, context):
    for table_bucket in table_buckets:
        name = table_bucket['name']
        arn = table_bucket['arn']
        try:
            con.execute(f"DETACH {name};")
        except:
            pass
        con.execute(
            f"""
            ATTACH '{arn}' AS {name} (
            TYPE iceberg,
            ENDPOINT_TYPE s3_tables
        );
            """
        )
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
# event = {
#     "sql": "select * from testtable.namespace_example.test_table;"
# }
# print(handler(event, None))