import json


def read_json_object(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, {'body': '올바른 JSON을 보내 주세요.'}
    if not isinstance(data, dict):
        return None, {'body': '객체 형식의 데이터를 보내 주세요.'}

    return data, None
