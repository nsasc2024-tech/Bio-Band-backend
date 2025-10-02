import json
import requests

def handler(request):
    # Turso database connection
    turso_url = "https://bio-hand-praveen123.aws-ap-south-1.turso.io/v1/execute"
    turso_token = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicm8iLCJpYXQiOjE3NTkwODAyMTMsImlkIjoiNDcyMWI0MzItODgyYi00MTVkLWI3YzQtNWQyZjk5ZTFkODVlIiwicmlkIjoiYjM4YTdkNjctNzcwMi00OTIxLWIwOTEtZTI0ODI2MzIyNmJmIn0.i8h9_arPOgflWPMGsC5jwTOa97g3ICpr7Q1z5c-6TLCzXLU__j5UEgcSj5dc-vd_1fpv2I7Pxq4FnXDGCYSPDQ"
    
    headers = {
        "Authorization": f"Bearer {turso_token}",
        "Content-Type": "application/json"
    }
    
    if request.method == 'GET':
        # Get all devices
        try:
            data = {
                "statements": [{
                    "stmt": "SELECT d.*, u.full_name as user_name FROM devices d LEFT JOIN users u ON d.user_id = u.id ORDER BY d.registered_at DESC"
                }]
            }
            
            response = requests.post(turso_url, headers=headers, json=data)
            result = response.json()
            
            devices = []
            if 'results' in result and len(result['results']) > 0:
                rows = result['results'][0].get('rows', [])
                columns = result['results'][0].get('columns', [])
                
                for row in rows:
                    device = {}
                    for i, col in enumerate(columns):
                        device[col] = row[i] if i < len(row) else None
                    devices.append(device)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'devices': devices,
                    'count': len(devices)
                })
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'success': False, 'error': str(e)})
            }
    
    elif request.method == 'POST':
        # Register new device
        try:
            body = json.loads(request.body) if hasattr(request, 'body') and request.body else {}
            
            device_id = body.get('device_id', '')
            user_id = body.get('user_id')
            model = body.get('model', '')
            
            data = {
                "statements": [{
                    "stmt": "INSERT INTO devices (device_id, user_id, model) VALUES (?, ?, ?) RETURNING id, device_id, user_id, model, registered_at",
                    "args": [device_id, user_id, model]
                }]
            }
            
            response = requests.post(turso_url, headers=headers, json=data)
            result = response.json()
            
            if 'results' in result and len(result['results']) > 0:
                rows = result['results'][0].get('rows', [])
                if rows:
                    device_data = rows[0]
                    return {
                        'statusCode': 200,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({
                            'success': True,
                            'device': {
                                'id': device_data[0],
                                'device_id': device_data[1],
                                'user_id': device_data[2],
                                'model': device_data[3],
                                'registered_at': device_data[4]
                            },
                            'message': 'Device registered successfully'
                        })
                    }
            
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'success': False, 'error': 'Failed to register device'})
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'success': False, 'error': str(e)})
            }
    
    else:
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Method not allowed'})
        }