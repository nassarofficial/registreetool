# RegisTree-Annotation-Tool
This is the official repo for Registree's Annotational Tool presented in "Name of Paper".
For the paper, and dataset check https://www.registree.ethz.ch/index.html. 

## Usage:
### MongoDB Structure:
#### Users:
To add a user to the tool, insert a document with the following json:
{
    "_id": {
        "$oid": "5aeaf393060a2f0f839aa62c"
    },
    "user": "admin",
    "pass": "admin"
}
