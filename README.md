# RegisTree Annotation Tool (ICCV 2019)
This is the official repo for Registree's Annotational Tool presented in "Name of Paper".
For the paper, and dataset check https://www.registree.ethz.ch/index.html. 

## Usage:
   1. Clone the repository 
   ```
   git clone https://github.com/nassarofficial/RegisTree-Annotation-Tool && cd polyrnn
   ```
   2. Install pip packages or dependencies   
   ```
   virtualenv annottool
   source env/bin/activate
   pip install -r requirements.txt
   ```
### MongoDB Structure:
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
