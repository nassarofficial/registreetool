# Multi Street View Annotation Tool
This is the official repo for Registree's Annotational Tool presented in "Simultaneous multi-view instance detection with learned geometric soft-constraints" accepted for ICCV 2019.
For the paper, and dataset check https://www.registree.ethz.ch/index.html. 

## Usage:
   1. Clone the repository 
   ```
   git clone https://github.com/nassarofficial/registreetool && cd registreetool
   ```
   2. Install pip packages or dependencies   
   ```
   virtualenv annottool
   source env/bin/activate
   pip install -r requirements.txt
   ```
   2. Download and upload/insert the mongodb dump file to any mongodb of your choosing:
   
### Adding a User:
#### Users:
To add a user to the tool, insert a document with the following json:
```
{
    "_id": {
        "$oid": "5aeaf393060a2f0f839aa62c"
    },
    "user": "admin",
    "pass": "admin"
}
 ```
