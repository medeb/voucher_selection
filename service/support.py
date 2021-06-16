import json

import pandas as pd

from service.constants import PKL_FILE_PATH


def create_frequent_segment(processed_df):
    frequent_segment_cols = ['timestamp', 'country_code', 'last_order_ts', 'first_order_ts', 'total_orders',
                             'voucher_amount', 'frequent_segment']
    frequent_segment_df = pd.DataFrame(processed_df, columns=frequent_segment_cols)
    # frequent_segment_df.shape
    frequent_segment_df = frequent_segment_df[frequent_segment_df.total_orders > 0]
    frequent_segment_df = frequent_segment_df[frequent_segment_df.voucher_amount > 0]
    # frequent_segment_df.shape

    grouped_segment_df = frequent_segment_df.groupby(['frequent_segment', 'voucher_amount']).agg(
        freq=('frequent_segment', 'count'))
    grouped_segment_df['segment_name'] = 'frequent_segment'
    grouped_segment_df['row_num'] = grouped_segment_df.sort_values(['freq'], ascending=[False]).groupby(
        ['frequent_segment']).cumcount() + 1

    most_used_freq_vouchers = grouped_segment_df[grouped_segment_df['row_num'] == 1]
    most_used_freq_vouchers.reset_index(inplace=True)
    most_used_freq_vouchers.rename({'frequent_segment': 'segment_type'}, axis='columns', inplace=True)

    return most_used_freq_vouchers


def create_recency_segment(processed_df):
    recency_segment_cols = ['timestamp', 'country_code', 'last_order_ts', 'first_order_ts', 'total_orders',
                            'voucher_amount', 'recency_segment']

    recency_segment_df = pd.DataFrame(processed_df, columns=recency_segment_cols)
    # frequent_segment_df.shape
    recency_segment_df = recency_segment_df[recency_segment_df.voucher_amount > 0]
    # display(recency_segment_df)

    grouped_segment_df = recency_segment_df.groupby(['recency_segment', 'voucher_amount']).agg(
        freq=('recency_segment', 'count'))
    grouped_segment_df['segment_name'] = 'recency_segment'
    grouped_segment_df['row_num'] = grouped_segment_df.sort_values(['freq'], ascending=[False]).groupby(
        ['recency_segment']).cumcount() + 1

    most_used_rec_vouchers = grouped_segment_df[grouped_segment_df['row_num'] == 1]
    most_used_rec_vouchers.reset_index(inplace=True)
    most_used_rec_vouchers.rename({'recency_segment': 'segment_type'}, axis='columns', inplace=True)

    return most_used_rec_vouchers


def voucher_selection_helper(country_code, segment_name, lower_bound, upper_bound):
    try:
        df = pd.read_pickle(PKL_FILE_PATH.replace('{COUNTRY}', country_code))
        cols = ['voucher_amount']
        result_set = df.loc[(df['segment_name'] == segment_name) & (df['lower_bound'] <= lower_bound) & (
                (df['upper_bound'] >= upper_bound) | (df['upper_bound'].isnull())), cols]

        result_set_to_json = {}
        if result_set.empty:
            result_set_to_json['msg'] = 'Out of bound, try adding configuration for 37+ orders in segment json'
        else:
            result_set_to_json = json.loads(result_set.to_json(orient='records', lines=True))
        return result_set_to_json

    except Exception as ex:
        return {
            "msg": f"Error occurred for {country_code}, please check if we have done pre processing for this country "
                   f"or not "
        }
