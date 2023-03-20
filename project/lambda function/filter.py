import json

THRESHOLD = .93


def lambda_handler(event, context):

    # Grab the inferences from the event
    inferences = event["inferences"]  ## TODO: fill in

    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = (inferences>THRESHOLD) ## TODO: fill in

    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
