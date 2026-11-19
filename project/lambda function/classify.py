import json
import sagemaker
import base64
from sagemaker.serializers import IdentitySerializer
from sagemaker.predictor import Predictor

# Fill this in with the name of your deployed model
ENDPOINT = 'image-classification-2023-02-14-13-25-18-287'  ## TODO: fill in

def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(## TODO: fill in)

    # Instantiate a Predictor
    ## TODO: fill in
    predictor = Predictor('image-classification-2023-02-14-13-25-18-287')
    
    # For this model the IdentitySerializer needs to be "image/png"
    predictor.serializer = IdentitySerializer("image/png")

    # Make a prediction:
    inferences = predictor.predict(predictor.serializer)  ## TODO: fill in

    # We return the data back to the Step Function    
    event["inferences"] = inferences.decode('utf-8')
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }