import sys
import os
import pandas as pd
import shutil


def get_df_iterator(q: str, chunksize=5000):
    prod = os.environ['ENVIRONMENT'].lower() == 'prod'
    connection_key = "POSTGRES_CONNECTION_PROD" if prod else "POSTGRES_CONNECTION_DEV"
    connection = os.environ[connection_key]
    return pd.read_sql(sql=q, con=connection, chunksize=chunksize)


def create_folder(folder: str):
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    os.mkdir(folder)


def cwd_abspath():
    return os.path.abspath(os.path.dirname(__file__))


def save_chunk(df, filepath):
    df.to_csv(filepath, index=False)


def main(folder):
    path = cwd_abspath()
    folder = os.path.join(path, folder)
    create_folder(folder)

    dfs = get_df_iterator(
        q="select thesis, subject from mathematician where thesis is not null and subject is not null;",
    )
    for i, df in enumerate(dfs):
        filepath = os.path.join(folder, f'chunk_{str(i).zfill(4)}.csv')
        save_chunk(df, filepath)


if __name__ == '__main__':
    try:
        folder = sys.argv[1]
    except IndexError as e:
        folder = "thesis_subjects"
    main(folder)
