# Voucher Selection API 

### The data pipeline

Please note, the data might have invalid values and unexpected issues. Ensure that data cleaning and preparation was done properly.
Requirements

The task is to provide the most used voucher value for different customer groups (segments). The segments should be calculated in the pipeline.
How to select a voucher?

On the request customer object will be provided:

    { 
    "customer_id": 123, 
	 "country_code": "Peru", 
	 "last_order_ts": "2018-05-03 00:00:00",  
	 “first_order_ts”: "2017-05-03 00:00:00", 
	 "total_orders": 15, 
	 "segment_name": "recency_segment" 
    }

Where segment_name - the name of the segment created in the pipeline.
Based on the segment_name a specific voucher should be provided.

You should implement the segments below:

frequent_segment -  number of orders for customer
Segments variants:

    "0-4" - customers which have done 0-4 orders 
    "5-13" - customers which have done 5-13 orders
    "14-37" - customers which have done 14-37 orders    
recency_segment -  days since last customer order by a customer
Segments variants:

    "30-60" - 30-60 days since the last order
    "61-90" - 61-90 days since the last order
    "91-120" - 91-120 days since the last order
    "121-180" - 121-180 days since the last order
    "180+" - more than 180 days since the last order

Requirements
0. The solution should be simple but reliable.
1. The solution should be integrated with REST API.

### Approach
We can divide this problem into two stages:
        1. Preprocessing of data
        2. API to read from processed data
### Solution With AWS:
Since we're getting the data in a compressed file format it would be better to store the file in AWS S3.
Whenever we upload a new file a AWS lambda will be triggered for the data processing and it will store the 
data as _'**pkl**'_ file based on country.
Now whenever we're going to call the voucher selection api we can just load the preprocessed 'pkl' file and return the required. 

### Local env solution:
I tried to mimic the same behaviour like AWS solution but instead ASW s3 
I'm storing all the raw and processed file in the resources folder(local storage). 
The structure looks like this : 
    
    --resources
        configurations
            __init__.py
            segment.json
        __init__.py
        data.parquet.gzip # raw compressed data
        peru_processed_data.pkl # pre-processed data country used as prefix
        
        
Instead of lambda I'm using one API to trigger the data pre-processing part.
The api is `http://127.0.0.1:5000/refresh`
we have to manually call this api if pre-processing is needed.
It's a POST api and expect the below req
        
        {
            "country_code": "Peru"
        }
The main motivation of passing the country_code is that we can compute for any country and use the
voucher selection api for all the other countries based on our requirements.

_If we have already computed the pkl file then there's no need to call this API. I have already created and uploaded the 
pkl file for the country Peru._

The other API[POST] is `http://127.0.0.1:5000/select-voucher` 
This API takes the below req
        
          { 
            "customer_id": 123, 
             "country_code": "Peru", 
             "last_order_ts": "2018-05-03 00:00:00",  
             "first_order_ts": "2017-05-03 00:00:00", 
             "total_orders": 15, 
             "segment_name": "recency_segment" 
            }
  and returns the voucher amount response:
         
         {
            "voucher_amount": 2640.0
         }
 

### How to run this app

Clone this repo, it might take some time(40-50secs) as I have uploaded both raw and processed data.
Once it's done go to the folder `voucher_selection` and run the command `docker-compose up`, once it's up and running
open postman or any api verification tool or curl or python app and call the API : Default port `5000` port and host `127.0.0.1`
     
    import requests
    url = 'http://127.0.0.1:5000/select-voucher'
    req = { 
            "customer_id": 123, 
             "country_code": "Peru", 
             "last_order_ts": "2018-05-03 00:00:00",  
             "first_order_ts": "2017-05-03 00:00:00", 
             "total_orders": 15, 
             "segment_name": "recency_segment" 
           }
    res= requests.post(url, json=req)
    print(res.text)


TO REFRESH DATA use the below

    import requests
    url = 'http://127.0.0.1:5000/refresh'
    req = {
            "country_code": "Peru"
          }
    res= requests.post(url, json=req)
    print(res.text)
    
CURL REQUESTS

    curl --location --request POST 'http://127.0.0.1:5000/select-voucher' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "customer_id": 123,
        "country_code": "Peru",
        "last_order_ts": "2018-05-03 00:00:00",
        "first_order_ts": "2018-03-04 00:00:00",
        "total_orders": 0,
        "segment_name": "recency_segment"
    }'
   
    curl --location --request POST 'http://127.0.0.1:5000/refresh' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "country_code": "Peru"
    }'
      
