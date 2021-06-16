from datetime import datetime

import pandas as pd
import numpy as np

from service.constants import SRC_FILE_PATH, PKL_FILE_PATH, SEGMENT_CONFIG_PATH
from service.support import voucher_selection_helper, create_frequent_segment, create_recency_segment

_supported_segment = ['frequent_segment', 'recency_segment']


def refresh_data_service(req):
    try:
        country_code = req.get('country_code').lower()
        data = pd.read_parquet(SRC_FILE_PATH, engine='pyarrow') # read the raw file
        # display(data)
        # data.country_code.unique()
        # data.groupby("voucher_amount").agg({'voucher_amount': ['count']})

        filtered_df = data[data['country_code'].str.lower() == country_code] # filter the country
        # filtered_df.country_code.unique()
        filtered_df['total_orders'] = filtered_df['total_orders'].apply(pd.to_numeric, errors='coerce')
        filtered_df['total_orders'] = filtered_df['total_orders'].fillna(0.0).astype('int')
        filtered_df['voucher_amount'] = filtered_df['voucher_amount'].fillna(0.0)
        filtered_df['last_order_ts'] = filtered_df['last_order_ts'].astype('datetime64')
        filtered_df['last_order_ts'] = pd.to_datetime(filtered_df.last_order_ts).dt.tz_localize('UTC')
        filtered_df['timestamp'] = filtered_df['timestamp'].astype('datetime64')
        filtered_df['timestamp'] = pd.to_datetime(filtered_df.timestamp).dt.tz_localize('UTC')
        # display(filtered_df)

        # PROCESSING
        processed_df = filtered_df
        processed_df['order_period'] = (processed_df.last_order_ts - processed_df.first_order_ts) / np.timedelta64(1,
                                                                                                                   'D')
        # min(processed_df['order_period'])

        # prepare recency_segment
        processed_df['recency_segment'] = np.where(
            processed_df['order_period'].between(30, 60, inclusive=False), '30-60',
            np.where(
                processed_df['order_period'].between(61, 90, inclusive=False), '61-90',
                np.where(
                    processed_df['order_period'].between(91, 120, inclusive=False), '91-120',
                    np.where(
                        processed_df['order_period'].between(121, 180, inclusive=False), '121-180',
                        np.where(
                            processed_df['order_period'] > 180, '180+',
                            '0-30'
                        )
                    )
                )
            )
        )

        # prepare frequent_segment
        processed_df['frequent_segment'] = np.where(
            processed_df['total_orders'].between(0, 4, inclusive=False), '0-4',
            np.where(
                processed_df['total_orders'].between(5, 13, inclusive=False),
                '5-13',
                np.where(
                    processed_df['total_orders'].between(14, 37, inclusive=False),
                    '14-37', '37+'
                )
            )
        )

        # create frequent_segment
        frequent_most_used_vouchers = create_frequent_segment(processed_df)
        recency_most_used_vouchers = create_recency_segment(processed_df)
        most_used_voucher_df = pd.concat([recency_most_used_vouchers, frequent_most_used_vouchers])
        # display(merge_df)

        segment_config_df = pd.read_json(SEGMENT_CONFIG_PATH, dtype='unicode')
        # print(segment_config_df)
        final_df = pd.merge(most_used_voucher_df, segment_config_df, on='segment_type', how='inner')
        # print(final_df)
        final_df['lower_bound'] = final_df['lower_bound'].astype('float')
        final_df['upper_bound'] = final_df['upper_bound'].astype('float')

        final_df.to_pickle(PKL_FILE_PATH.replace('{COUNTRY}', country_code))
        return {"msg": f"data has been refreshed for {country_code}"}
    except Exception as ex:
        return {"msg": ex}


def voucher_selection_service(request):
    segment_name = request.get('segment_name')
    country_code = request.get('country_code').lower()

    if segment_name == 'frequent_segment':
        total_orders = int(request.get('total_orders', 0))
        return voucher_selection_helper(country_code, segment_name, total_orders, total_orders)

    elif segment_name == 'recency_segment':
        last_order_ts = request.get('last_order_ts')
        first_order_ts = request.get('first_order_ts')
        date_diff = (datetime.strptime(last_order_ts, '%Y-%m-%d %H:%M:%S')
                     - datetime.strptime(first_order_ts, '%Y-%m-%d %H:%M:%S')).days
        if date_diff < 0:
            return {"msg": "Invalid date selection criteria"}
        return voucher_selection_helper(country_code, segment_name, date_diff, date_diff)
    else:
        return {"msg": "Unsupported segment requested"}
