FROM public.ecr.aws/lambda/python:3.12

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt
ARG DUCKDB_EXT_DIR="/tmp/.duckdb"
RUN mkdir -p ${DUCKDB_EXT_DIR} && \
    # Run python to install extensions, telling DuckDB to use the created directory
    python -c "\
import duckdb;\
import os;\
ext_dir = os.environ.get('DUCKDB_EXT_DIR');\
con = duckdb.connect(database=':memory:', read_only=False);\
# Set the home_directory AFTER connecting using the SET command.\
con.execute(f\"SET home_directory='{ext_dir}'\");\
con.execute('INSTALL aws FROM core_nightly;');\
con.execute('INSTALL httpfs FROM core_nightly;');\
con.execute('INSTALL iceberg FROM core_nightly;');\
print('Extensions installed during build.');\
con.close();\
"
# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.handler" ]