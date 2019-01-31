# RegisTree-Annotation-Tool
This is the official repo for Registree's Annotational Tool presented in "Name of Paper".
For the paper, and dataset check https://www.registree.ethz.ch/index.html. 

## Usage:
   1. Clone the repository 
   ```
   git clone https://github.com/davidjesusacu/polyrnn && cd polyrnn
   ```
   2. Install dependencies   
   (Note: Using a GPU (and tensorflow-gpu) is recommended. The model will run on a CPU, albeit slowly.)
   ```
   virtualenv env
   source env/bin/activate
   pip install -r requirements.txt
   ```
   3. Download the pre-trained models and graphs (448 MB)  
   (These models were trained on the Cityscapes Dataset)
   ``` 
   ./models/download_and_unpack.sh 
   ```
   4. Run demo\_inference.sh
   ```
   ./src/demo_inference.sh 
   ```
   This should produce results in the output/ folder that look like
   ![ex2](readme/frankfurt_000000_000294_42.png)
   ![ex1](readme/medical_00_5_20.png) 

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
