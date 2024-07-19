import os
import json
import shutil
import codecs
import requests
import distutils
import numpy as np
import pandas as pd
from tqdm import tqdm

DATA_PATH = './data'
TORONTO_OPEN_DATA_URL = 'https://ckan0.cf.opendata.inter.prod-toronto.ca'


def download_file(url, path, filename):
    response = requests.get(url)

    if response.status_code == 200:
        with open(f'{path}/{filename}', 'wb') as f:
            f.write(response.content)
    else:
        raise Exception(f"Failed to download file. Status code: {response.status_code}")


def scrap_toronto_open_data(start_idx=None):

    datasets_url = TORONTO_OPEN_DATA_URL + '/api/3/action/package_list'
    datasets = requests.get(datasets_url).json()['result']

    os.makedirs(f'{DATA_PATH}/excerpts', exist_ok=True)

    for dataset_id in tqdm(datasets if start_idx is None else datasets[start_idx:]):
        dataset_key = dataset_id.replace(' ', '_').replace('-', '_')

        dataset_url = TORONTO_OPEN_DATA_URL + '/api/3/action/package_show'
        params = {"id": dataset_id}

        dataset_package = requests.get(dataset_url, params=params).json()['result']

        if (
            distutils.util.strtobool(dataset_package.get('is_retired', 'false')) or
            'CSV' not in dataset_package['formats']
        ):
            continue

        resources_path = f'{DATA_PATH}/datasets/{dataset_key}/resources'
        if os.path.exists(resources_path):
            continue
        os.makedirs(resources_path)

        resources = list(filter(lambda res: res['format'] == 'CSV', dataset_package['resources']))
        resources = [res for res in resources if ' - 2945' not in res['name'] and ' - 2952' not in res['name']]

        names_stripped = [(res['name'][:-4] if res['name'].endswith('.csv') else res['name']) for res in resources]
        _, unique_indices = np.unique(names_stripped, return_index=True)
        resources = list(np.array(resources)[unique_indices])

        n_failures = 0
        for resource in resources:
            try:

                resource_name = resource['name']
                resource_name = resource_name.replace(' ', '_').replace('-', '_')
                if not resource_name.endswith('.csv'):
                    resource_name = resource['name'] + '.csv'
                if ' - 4326' in resource_name:
                    resource_name.replace(' - 4326', '')

                download_file(
                    resource['url'],
                    resources_path,
                    resource_name,
                )
            except:
                n_failures += 1
                print(f'Failed to download {resource["name"]}.csv in {dataset_id}')

            try:
                preprocess(
                    f'{resources_path}/{resource_name}',
                )
            except:
                n_failures += 1
                print(f'Failed to preprocess {resource["name"]}.csv in {dataset_id}')

        if n_failures == len(resources) or len(resources)==0:
            shutil.rmtree(f'{DATA_PATH}/datasets/{dataset_key}')
            continue

        with open(f'{DATA_PATH}/datasets/{dataset_key}/description.json', 'w') as f:
            json.dump(dataset_package, f)

        with open(f'{DATA_PATH}/excerpts/{dataset_key}.txt', 'w') as f:
            f.writelines(dataset_package['notes'])



def preprocess(resource_path):
    df = pd.read_csv(resource_path, dtype='unicode')

    if 'geometry' in df.columns:
        df = df.drop('geometry', axis=1)

    df.to_csv(resource_path)



scrap_toronto_open_data()

