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
        # Get all health data
        try:
            data = {
                "statements": [{
                    "stmt": "SELECT hd.*, u.full_name as user_name FROM device_data hd LEFT JOIN users u ON hd.user_id = u.id ORDER BY hd.timestamp DESC LIMIT 100"
                }]
            }
            
            response = requests.post(turso_url, headers=headers, json=data)
            result = response.json()
            
            health_data = []
            if 'results' in result and len(result['results']) > 0:
                rows = result['results'][0].get('rows', [])
                columns = result['results'][0].get('columns', [])
                
                for row in rows:
                    data_item = {}
                    for i, col in enumerate(columns):
                        data_item[col] = row[i] if i < len(row) else None
                    health_data.append(data_item)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'health_data': health_data,
                    'count': len(health_data)
                })
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'success': False, 'error': str(e)})
            }
    
    elif request.method == 'POST':
        # Add new health data
        try:
            body = json.loads(request.body) if hasattr(request, 'body') and request.body else {}
            
            user_id = body.get('user_id')
            device_id = body.get('device_id', '')
            heart_rate = body.get('heart_rate')
            spo2 = body.get('spo2')
            temperature = body.get('temperature')
            steps = body.get('steps')
            calories = body.get('calories')
            activity = body.get('activity', '')
            
            data = {
                "statements": [{
                    "stmt": "INSERT INTO device_data (user_id, device_id, heart_rate, spo2, temperature, steps, calories, activity) VALUES (?, ?, ?, ?, ?, ?, ?, ?) RETURNING id, user_id, device_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp",
                    "args": [user_id, device_id, heart_rate, spo2, temperature, steps, calories, activity]
                }]
            }
            
            response = requests.post(turso_url, headers=headers, json=data)
            result = response.json()
            
            if 'results' in result and len(result['results']) > 0:
                rows = result['results'][0].get('rows', [])
                if rows:
                    health_data = rows[0]
                    return {
                        'statusCode': 200,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({
                            'success': True,
                            'health_data': {
                                'id': health_data[0],
                                'user_id': health_data[1],
                                'device_id': health_data[2],
                                'heart_rate': health_data[3],
                                'spo2': health_data[4],
                                'temperature': health_data[5],
                                'steps': health_data[6],
                                'calories': health_data[7],
                                'activity': health_data[8],
                                'timestamp': health_data[9]
                            },
                            'message': 'Health data added successfully'
                        })
                    }
            
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'success': False, 'error': 'Failed to add health data'})
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