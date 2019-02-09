__**Written in python3.7**__

__Resolving script:__
ns.py - performs NS queries on input domains and outputs a CSV file with the following format:
domain_name,name_servers_count,glue_records_count,out_of_bailiwick_glue_records  
domain1.com,1,1,1  
domain2.com,1,1,1  
domain3.com,1,1,1  
...  

dependencies: dnspython  
usage: ns.py [-h] [-domains_file_path DOMAINS_FILE_PATH]  
             [-domains DOMAINS [DOMAINS ...]] -output_path OUTPUT_PATH

**note: the script should be ran on the resolver as it is configured to perform queries on 127.0.0.1**


__Plots script:__
create_statistics.py - reads output of ns.py and generates several plots:
* Nameservers histogram
* Nameservers CDF
* Glue records CDF
* Out-of-bailiwick Glue records CDF

dependencies: matplotlib, numpy  
usage: create_statistics.py [-h] -counters_file COUNTERS_FILE  
                            [-output_path OUTPUT_PATH]