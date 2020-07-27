def init_variables():
    path_to_json = "../cs-train/"
    column_dict = {'country': 'country', 'customer_id': 'customer_id',
                       'day': 'day','invoice': 'invoice', 'month': 'month',
                       'total_price': 'price', 'StreamID': 'stream_id',
                        'TimesViewed': 'times_viewed'}
    inconsistent_col = ['TimesViewed', 'StreamID', 'total_price']
    keys = ['country', 'customer_id', 'day', 'invoice', 'month', 'price', 'stream_id', 'times_viewed', 'year']
    return path_to_json, column_dict, inconsistent_col, keys
