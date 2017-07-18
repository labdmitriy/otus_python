#!/usr/bin/env python2

from pandas import Series, DataFrame
import pandas as pd
import numpy as np

import gzip
import fnmatch
import os
import re
from datetime import datetime
from collections import defaultdict
from string import Template
from shutil import copyfile
from itertools import ifilter
from bisect import insort



config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def gen_open(file_name):
    if file_name.endswith(".gz"):
        f = gzip.open(file_name)
    else:
        f = open(file_name)
    
    for line in f:
        yield line


def gen_find(filepat, top):
    for path, dirlist, filelist in os.walk(top):
        for name in fnmatch.filter(filelist, filepat):
            yield os.path.join(path, name)       


def field_map(dict_seq, name, func):
    for d in dict_seq:
        d[name] = func(d[name])
        yield d


def select_columns(dict_seq, columns_list):
    for d in dict_seq:
        new_dict = {column: d[column] for column in columns_list}
        yield new_dict


def get_url(request):
    r = re.compile('\S+ (\S+) \S+')
    
    if r.match(request):
        return request.split()[1]


def main():
    log_files = gen_find('*', config['LOG_DIR'])
    
    r = re.compile(r'\D*(\d+)\D*')
    groups = (r.match(file_name) for file_name in log_files)
    file_dates = (g.groups()[0] for g in groups if g)
    max_date_str = max(file_dates)
    
    log_file_name = gen_find('*{}*'.format(max_date_str), config['LOG_DIR']).next()
    
    max_date_str = datetime.strptime(max_date_str, '%Y%m%d').strftime('%Y.%m.%d')
    
    report_file_name = gen_find('*{}*'.format(max_date_str), config['REPORT_DIR'])
    
    if list(report_file_name):
        print('file is already processed')
        return
    
    log_lines = gen_open(log_file_name)
    
    log_pats = r'(\S+) (\S+)  (\S+) \[(.*?)\] "(.*?)" (\S+) (\S+) "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)" (\S+)'
    log_pat = re.compile(log_pats)
    
    groups  = (log_pat.match(line) for line in log_lines)
    tuples  = (g.groups() for g in groups if g)
    
    col_names   = ('remote_addr', 'remote_user', 'http_x_real_ip', 'time_local', 'request',
                  'status', 'body_bytes_sent', 'http_referer', 'http_user_agent',
                   'http_x_forwarded_for','http_X_REQUEST_ID', 'http_X_RB_USER', 'request_time')
    
    log = (dict(zip(col_names,t)) for t in tuples)
    log = field_map(log, 'request_time', float)
    log = field_map(log, 'request', lambda x: get_url(x))
    log = select_columns(log, ['request', 'request_time'])
    
    
    counter = defaultdict(int)
    timer = defaultdict(float)
    max_value = defaultdict(float)
    median = defaultdict(float)
    
    for log_line in log:
        request = log_line['request']
        request_time = log_line['request_time']
        
        counter[request] += 1
        timer[request] += request_time
        
        if max_value[request] < request_time:
            max_value[request] = request_time
        
        if request not in median:
            median[request] = []
        insort(median[request], request_time)
    
    all_time = sum({request_time for request_time in timer.itervalues()})
    all_count = sum({count for count in counter.itervalues()})

    timer = [(key, timer[key]) 
             for key in sorted(timer, key = timer.get, reverse=True)][:REPORT_SIZE]
    timer = dict(timer)
    print(timer)
    
    
    
    
#    counter_series = Series(counter)
#    timer_series = Series(timer)
#    max_value_series = Series(max_value)
#    
#    stats_df = pd.concat([timer_series, counter_series, max_value_series],
#                         axis = 1, ignore_index = True).reset_index()
#    stats_df.columns = ['url', 'time_sum', 'count', 'time_max']
#    stats_df.sort_values('time_sum', axis = 0, ascending = False, inplace = True)
#    
#    all_time = stats_df['time_sum'].sum()
#    all_count = stats_df['count'].sum()
#    
#    stats_df['time_sum'] = np.round(stats_df['time_sum'], 3)
#    stats_df['count_perc'] = np.round((stats_df['count'] / all_count) * 100, 3)
#    stats_df['time_avg'] = np.round(stats_df['time_sum'] / stats_df['count'], 3)
#    stats_df['time_perc'] = np.round((stats_df['time_sum'] / all_time) * 100, 3)
#    
#    stats_df = stats_df.head(100)
#    
#    report_json = stats_df.to_json(orient = 'records')
#    report_template_path = os.path.join(os.curdir, 'template/report.html')
#    report_file_path = os.path.join(config['REPORT_DIR'], 'report-{}.html'.format(max_date_str))
#    report_template_path, report_file_path
#    
#    if not os.path.isdir(config['REPORT_DIR']):
#        os.makedirs(config['REPORT_DIR'])
#    
#    copyfile(report_template_path, report_file_path)
#    
#    with open(report_template_path, 'r') as f:
#        report_template = ''.join(f.readlines())
#    
#    
#    report = Template(report_template).safe_substitute({'table_json': report_json})
#    
#    with open(report_file_path, 'w') as f:
#        f.write(report)


if __name__ == '__main__':
    main()



