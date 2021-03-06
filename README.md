# Approach
We can divide this problem into two stages:
        1. Preprocessing of data
        2. API to read from processed data
### Solution With AWS:
Since we're getting the data in a compressed file format it would be better to store the file in AWS S3.
Whenever we upload a new file a AWS lambda will be triggered for the data processing and it will store the 
data as _'**pkl**'_ file based on country.
Now whenever we're going to call the voucher selection api we can just load the preprocessed 'pkl' file and return the response. 

### Local env solution:
I tried to mimic the same behaviour like AWS solution but instead ASW s3 I'm storing all the raw and processed file in the resources folder(local storage). 
The structure looks like this : 
    
    --resources
        configurations
            __init__.py
            segment.json # segment configuration 
        __init__.py
        data.parquet.gzip # raw compressed data
        peru_processed_data.pkl # pre-processed data country used as prefix
        
       
Instead of lambda I'm using one API to trigger the data pre-processing part. The api is `http://127.0.0.1:5000/refresh` we have to manually call this api if pre-processing is needed.
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
 
### Segment Configuration 

        {
        "lower_bound": 5,
        "upper_bound": 13,
        "segment_type": "5-13"
        }
In segment configuration one can define the segments conf. We can add any new configuration here based on the requirement like to support 37+ orders we can just a new config and build the image.
        
        {
        "lower_bound": 38,
        "upper_bound": null,
        "segment_type": "37+"
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
      
IF WE WANT TO RUN FOR OTHER COUNTRY WE JUST HAVE TO CHANGE REQ LIKE FOR Australia REQ : 

    curl --location --request POST 'http://127.0.0.1:5000/select-voucher' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "customer_id": 123,
        "country_code": "Australia",
        "last_order_ts": "2018-05-03 00:00:00",
        "first_order_ts": "2018-03-04 00:00:00",
        "total_orders": 0,
        "segment_name": "recency_segment"
    }'
   
    curl --location --request POST 'http://127.0.0.1:5000/refresh' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "country_code": "Australia"
    }'
