import os
import json
import shutil
import requests
import distutils
import argparse
import numpy as np
from tqdm import tqdm

TORONTO_OPEN_DATA_URL = 'https://ckan0.cf.opendata.inter.prod-toronto.ca'

def download_file(
    url: str, 
    path: str, 
    filename: str
):
    '''
    Downloads and stores the specified file locally.

    Args:
        url: web file url 
        path: local path
        filename: file name to use

    Raises:
        Exception if the download was unsuccessful
    '''
    response = requests.get(url)

    if response.status_code == 200:
        with open(f'{path}/{filename}', 'wb') as f:
            f.write(response.content)
    else:
        raise Exception(f"Failed to download file. Status code: {response.status_code}")


def scrap_toronto_open_data(  
    data_path: str,  
    start_idx: int=0
):
    '''
    Retrieves the list of all datasets available on Toronto Open Data portal (https://open.toronto.ca/catalogue/)
    and downloads ones which are available in CSV format and are non-retired.

    Args:
        data_path: path to store the data
        start_idx: dataset index to start from
    '''

    datasets_url = TORONTO_OPEN_DATA_URL + '/api/3/action/package_list'
    datasets = requests.get(datasets_url).json()['result']

    os.makedirs(f'{data_path}/excerpts', exist_ok=True)

    for dataset_id in tqdm(datasets[start_idx:]):
        dataset_key = dataset_id.replace(' ', '_').replace('-', '_')

        dataset_url = TORONTO_OPEN_DATA_URL + '/api/3/action/package_show'
        params = {"id": dataset_id}

        dataset_package = requests.get(dataset_url, params=params).json()['result']

        if (
            distutils.util.strtobool(dataset_package.get('is_retired', 'false')) or
            'CSV' not in dataset_package['formats']
        ):
            continue

        resources_path = f'{data_path}/datasets/{dataset_key}/resources'
        if os.path.exists(resources_path):
            continue
        os.makedirs(resources_path)

        resources = list(filter(lambda res: res['format'] == 'CSV', dataset_package['resources']))

        # Exclude duplicate tables with geo coordinates in different format
        resources = [res for res in resources if ' - 2945' not in res['name'] and ' - 2952' not in res['name']]
        
        # Exclude duplicate tables with missing extension
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

                download_file(
                    resource['url'],
                    resources_path,
                    resource_name,
                )
            except:
                n_failures += 1
                print(f'Failed to download {resource["name"]}.csv in {dataset_id}')

        if n_failures == len(resources) or len(resources)==0:
            shutil.rmtree(f'{data_path}/datasets/{dataset_key}')
            continue

        with open(f'{data_path}/datasets/{dataset_key}/description.json', 'w') as f:
            json.dump(dataset_package, f)

        with open(f'{data_path}/excerpts/{dataset_key}.txt', 'w') as f:
            f.writelines(dataset_package['notes'])


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, default='./data')
    parser.add_argument('--start_idx', type=int, default=0)
    args = parser.parse_args()

    scrap_toronto_open_data(args.data_path, args.start_idx)

