import json

def handler(request):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': 'Bio Band API Working!',
            'status': 'success',
            'endpoints': {
                'GET /api/': 'API status',
                'POST /api/users': 'Create user',
                'GET /api/users': 'Get users'
            }
        })
    }