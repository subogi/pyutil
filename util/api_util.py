from dict_util import MyDict
import json


def ApiErrorResponse(code,errorstring):
    return {
                "headers": {
                    "Access-Control-Allow-Headers" : "Content-Type",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
                },
                "statusCode": code,
                "body": json.dumps({"statusCode": code,"data": errorstring})
            }

def ApiSuccessResponse(data):
    return {
                "headers": {
                    "Access-Control-Allow-Headers" : "Content-Type",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
                },
                "statusCode": 200,
                "body": data.WriteJsonString()
            }
