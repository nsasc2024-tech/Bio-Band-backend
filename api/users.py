import json

# Simple in-memory storage (will reset on each function call)
users_storage = []

def handler(request):
    global users_storage
    
    method = getattr(request, 'method', 'GET')
    
    if method == 'GET':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'users': users_storage,
                'count': len(users_storage),
                'note': 'Data stored in memory (resets on deployment)'
            })
        }
    
    elif method == 'POST':
        try:
            # Parse request body
            body_str = getattr(request, 'body', '{}')
            if isinstance(body_str, bytes):
                body_str = body_str.decode('utf-8')
            body = json.loads(body_str) if body_str else {}
            
            # Create user
            user_id = len(users_storage) + 1
            new_user = {
                'id': user_id,
                'full_name': body.get('full_name', ''),
                'email': body.get('email', ''),
                'age': body.get('age'),
                'created_at': '2024-09-28T16:00:00Z'
            }
            
            users_storage.append(new_user)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': True,
                    'user': new_user,
                    'message': 'User created successfully (in memory)',
                    'note': 'To connect to Turso database, we need to resolve Vercel function issues'
                })
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': False,
                    'error': str(e)
                })
            }
    
    else:
        return {
            'statusCode': 405,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Method not allowed'})
        }