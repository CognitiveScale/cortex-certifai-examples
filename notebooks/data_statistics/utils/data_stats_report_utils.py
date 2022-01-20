import collections
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from copy import deepcopy
import matplotlib.ticker as ticker
loc = ticker.MultipleLocator(base=1.0)

# CERTIFAI PACKAGES
from certifai.scanner.report_reader import ScanReportReader

def retrieve_metric(reader, reports_df, scan_dir, metric='feature_quality'):
    results_dict = {}

    for run_idx, indiviudal_report in enumerate(reports_df.values):
        data_stats_report_list = reports_df.iloc[run_idx]
        result = reader.load_scan(scan_dir, data_stats_report_list['scan id'])

        model_id = list(result['data_statistics'].keys())[0]
        results_dict[run_idx] = result['data_statistics'][model_id]['data_statistics'][metric]

    return results_dict


def flatten_dictionary(d, parent_key='', sep='_', categorical=False):
    items = []
    for elem in d:
        if categorical:
            new_key = parent_key + sep + str(elem['name']) if parent_key else elem['name']
            v = elem['value']
        else:
            new_key = parent_key + sep + elem if parent_key else elem
            v = d[elem]

        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep, categorical=categorical).items())
        else:
            items.append((new_key, v))

    return dict(items)


def generate_feature_quality_df(reports_df, aggregate_dict):
    aggregate_dict_copy = deepcopy(aggregate_dict)
    list_of_dicts_num, list_of_dicts_cat = [], []
    for dataset_id, result in aggregate_dict_copy.items():
        for feature_dict in result:
            feature_dict['scan_id'] = reports_df.iloc[dataset_id]['scan id']
            feature_dict['date'] = reports_df.iloc[dataset_id]['date']
            feature_dict['dataset_id'] = dataset_id
            if 'quartiles' in feature_dict:
                insert_dict = flatten_dictionary(feature_dict['quartiles'], parent_key='quartiles')
                feature_dict.pop('quartiles')
                list_of_dicts_num.append({**feature_dict, **insert_dict})

            else:
                if feature_dict['display_counts']:
                   label_key = 'counts' if feature_dict['feature'] in str(feature_dict['counts'][0]['name']) else 'counts_'+str(feature_dict['feature'])
                   insert_dict = flatten_dictionary(feature_dict['counts'], parent_key=label_key, categorical=True)
                   feature_dict.pop('counts')

                   list_of_dicts_cat.append({**feature_dict, **insert_dict})

    return pd.DataFrame(list_of_dicts_num), pd.DataFrame(list_of_dicts_cat)


def aggregate_quartile_features(feature_df):
    unique_features = feature_df['feature'].unique()

    result = {key : {} for key in unique_features}

    num_datasets = feature_df['dataset_id'].max()

    for feature in unique_features:
        idx = feature_df['feature'] == feature

        result[feature]['quartiles_min'] = feature_df.loc[idx, 'quartiles_min'].values
        result[feature]['quartiles_first'] = feature_df.loc[idx, 'quartiles_first'].values
        result[feature]['quartiles_second'] = feature_df.loc[idx, 'quartiles_second'].values
        result[feature]['quartiles_third'] = feature_df.loc[idx, 'quartiles_third'].values
        result[feature]['quartiles_max'] = feature_df.loc[idx, 'quartiles_max'].values

    return result


def collapse_dictionary_key(feature_dict, key):
    insert_dict = flatten_dictionary(feature_dict, parent_key=key)
    if key:
        feature_dict.pop(key)
    return {**feature_dict, **insert_dict}


def generate_data_quality_df(reports_df, aggregate_dict):
    aggregate_dict_copy = deepcopy(aggregate_dict)
    list_of_dicts = []

    for dataset_id, result in aggregate_dict_copy.items():
        result['scan_id'] = reports_df.iloc[dataset_id]['scan id']
        result['date'] = reports_df.iloc[dataset_id]['date']
        result['dataset_id'] = dataset_id
        list_of_dicts.append(collapse_dictionary_key(result, ''))

    return pd.DataFrame(list_of_dicts)


def aggregate_counts_features(feature_df, columns=[]):
    if 'feature' in feature_df:
        unique_features = feature_df['feature'].unique()
        result = {key : {} for key in unique_features}
    else:
        unique_features = columns
        result = {}

    num_datasets = feature_df['dataset_id'].max()
    data_id_list = feature_df['dataset_id']

    for feature in unique_features:
        sub_df = feature_df[[x for x in feature_df.columns if (feature in x) | (x == 'dataset_id')]]
        feature_list = sub_df.columns[sub_df.columns != 'dataset_id']

        for header in feature_list:
            feature_dict = sub_df.groupby(['dataset_id'])[header].agg(list).to_dict()
            count_array = [np.nan if np.isnan(value_array).all() else np.nanmax(value_array) for value_array in feature_dict.values()]

            if 'feature' in feature_df:
                result[feature][header] = count_array
            else:
                result[header] = count_array

    return result


def unravel_prediction_dict(input_dict):
    result_dict = list(input_dict.values())
    list_of_dicts = []
    for feature_dict in result_dict:
        if feature_dict['quartiles'] is not None:
            insert_dict = flatten_dictionary(feature_dict['quartiles'], parent_key='quartiles')
            feature_dict.pop('quartiles')
            list_of_dicts_num.append({**feature_dict, **insert_dict})

        else:
            insert_dict = flatten_dictionary(feature_dict['counts'], parent_key='', categorical=True)

            list_of_dicts.append(insert_dict)

    return pd.DataFrame(list_of_dicts)


def generate_data_drift_df(reports_df, aggregate_dict):
    aggregate_dict_copy = deepcopy(aggregate_dict)
    list_of_dicts = []

    def set_meta_data(data_id, input_dict):
        input_dict.pop('aux_stats')
        # remove aux stats for now
        input_dict['scan_id'] = reports_df.iloc[data_id]['scan id']
        input_dict['date'] = reports_df.iloc[data_id]['date']
        input_dict['dataset_id'] = data_id

        return input_dict


    for dataset_id, result in aggregate_dict_copy.items():
        if isinstance(result, dict):
            output = set_meta_data(dataset_id, result)
            list_of_dicts.append(output)
        else:
            for feature_dict in result:
                output = set_meta_data(dataset_id, feature_dict)
                list_of_dicts.append(output)

    return pd.DataFrame(list_of_dicts)


def aggregate_drift_features(feature_df):
    unique_features = feature_df['feature'].unique()

    result = {key : {} for key in unique_features}

    num_datasets = feature_df['dataset_id'].max()

    for feature in unique_features:
        idx = feature_df['feature'] == feature

        result[feature]['value'] = feature_df.loc[idx, 'value'].values
        result[feature]['threshold'] = feature_df.loc[idx, 'threshold'].values
        result[feature]['metric'] = feature_df.loc[idx, 'metric'].values

    return result


def plot_quartile_data(result_dict):
    for idx, (feature, data_row) in enumerate(result_dict.items()):
        N = len(data_row['quartiles_min'])
        cmap = get_cmap(N)

        fig, ax = plt.subplots(figsize=(20, 5))

        quartiles = ['max', 'third', 'second', 'first', 'min']
        label_dict = {'max':'Max', 'third':'75%', 'second':'50%', 'first':'25%', 'min':'Min'}
        width = [4, 2, 2, 2, 4]
        style = ['-', '--', '-', '--', '-']
        markers = ['', '', 'o', '', '']

        for entry_idx, entry in enumerate(quartiles):
            plt.plot(data_row['quartiles_' + entry], label=label_dict[entry], color=cmap(idx), linewidth=width[entry_idx], linestyle=style[entry_idx], marker=markers[entry_idx])

        t = np.arange(N)
        ax.fill_between(t, data_row['quartiles_min'],  data_row['quartiles_max'], facecolor='lightgray', alpha=0.1)

        plt.xlabel('Monitored Dataset #')
        ax.xaxis.set_major_locator(loc)
        plt.ylabel('Value')
        plt.title(f"Quartiles for Feature: {feature}")
        plt.legend()


def plot_count_data(counts_data):
    for feature, group in counts_data.items():
        fig, ax = plt.subplots(figsize=(20, 5))
        y = [data for data in group.values()]
        y_sum = np.nansum(y, axis=0)
        y_sum[y_sum == 0] = 1.0

        X = list(range(0, len(y[0])))

        labels = []
        for x in list(group.keys()):
            substring = x.replace('counts_', '')
            if "_" in substring:
                result = substring.replace(feature+'_', '')
            else:
                result = substring
            labels.append(result)

        plt.stackplot(X, 100*np.nan_to_num(y)/y_sum, labels=labels, alpha=0.3)

        plt.xlabel('Monitored Dataset #')
        ax.xaxis.set_major_locator(loc)
        plt.ylabel('Percent (%)')
        plt.title(f"Distribution: {feature.replace('counts_','')}")
        plt.legend(bbox_to_anchor = (1.05, 0.6))
        plt.show()


def get_top_N(data_dict, N=6):
    if len(data_dict) <= N:
        return data_dict
    else:
        max_per_group = [np.nanmax(data_array) for data_array in data_dict.values()]
        group_name = [key for key in data_dict.keys()]
        sorted_idx = np.argsort(max_per_group)[::-1]

        result = {}
        for idx in range(N-1):
            result[group_name[sorted_idx[idx]]] = data_dict[group_name[sorted_idx[idx]]]

        other_sum = np.zeros(len(data_dict[group_name[sorted_idx[idx]]]))

        for idx in range(N, len(sorted_idx)):
            other_sum = np.nansum([other_sum, data_dict[group_name[sorted_idx[idx]]]], axis=0)

        result['other'] = other_sum
        return result


def plot_stacked_count(counts_data):
    for feature, group in counts_data.items():
        aggregate_dict = get_top_N(group)
        plot_count_data({feature: aggregate_dict})


def plot_drift(drift_result):
    def plot_graph(idx, feature, data_row):
        N = len(data_row['value'])
        cmap = get_cmap(N)

        fig, ax = plt.subplots(figsize=(20, 5))
        plt.plot(data_row['value'], marker='o', label=feature, color=cmap(idx), linewidth=4)

        if data_row['metric'][0] == 'kolmogorov-smirnov' :
            plt.ylabel('KS Statistic')
        else:
            plt.ylabel(r"$\chi^{2}$ Statistic")

        plt.plot(data_row['threshold'], 'r--', linewidth=2)

        t = np.arange(N)
        ax.fill_between(t, data_row['threshold'],  np.ones(N)*np.max(np.array([data_row['value'], data_row['threshold']*1.05])), facecolor='red', alpha=0.1)
        plt.text(0, data_row['threshold'][0]*1.05, r"Data Drift Detected", fontsize=12, color='r')

        plt.xlabel('Monitored Dataset #')
        ax.xaxis.set_major_locator(loc)
        plt.legend()
        plt.show()

    if isinstance(drift_result, dict):
        for idx, (feature, data_row) in enumerate(drift_result.items()):
            plot_graph(idx, feature, data_row)
    else:
        plot_graph(0, 'prediction', drift_result)


def plot_prediction_distribution(prediction_df):
    result = {'Outcome' : {"counts_"+str(key): value.values for key, value in prediction_df.items()}}
    plot_count_data(result)


def get_cmap(n, name='tab20'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)
