# `def lambda_handler(event, context):`

- This is the entry point of your AWS Lambda function.
- AWS invoke this function when lambda is triggered.
- There are two parameters:
    1. event
    2. context
1. event:
    - Contains information about what triggered lambda.
    - For example, if S3 triggered your lambda then the information might contain:
        - Bucket name
        - object name
        - object key
        - event type
2. context:
    - It contains information about lambda execution environment
    - For example:
        - function name
        - memory limit
        - request ID
        - remaining execution time