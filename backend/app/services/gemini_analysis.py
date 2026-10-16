import base64, json, os, urllib.error, urllib.request
from pathlib import Path

MODEL=os.getenv('GEMINI_MODEL','gemini-2.5-flash')
ENDPOINT='https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'


def analyze_image(path: Path, mime_type: str, filename: str) -> dict:
    api_key=os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise RuntimeError('Gemini is not configured.')
    prompt=(
        'You are assisting a human reviewer of a GSCHPT vehicle record. '
        'Return only JSON suggestions from visible evidence in this image. '
        'Never invent, infer, or fill unseen plate numbers, chassis numbers, motor numbers, ownership, identity, violations, or incident facts. '
        'Use null when a value is not clearly visible. Do not associate this image with any vehicle. '
        f'Original filename: {filename}. Return fields: vehicle_type, make, model, color, plate_or_sticker, confidence, uncertain_fields, notes.'
    )
    body={
        'contents':[{'parts':[
            {'text':prompt},
            {'inline_data':{'mime_type':mime_type,'data':base64.b64encode(path.read_bytes()).decode('ascii')}}
        ]}],
        'generationConfig':{
            'responseMimeType':'application/json',
            'responseSchema':{
                'type':'OBJECT',
                'properties':{
                    'vehicle_type':{'type':'STRING','nullable':True},
                    'make':{'type':'STRING','nullable':True},
                    'model':{'type':'STRING','nullable':True},
                    'color':{'type':'STRING','nullable':True},
                    'plate_or_sticker':{'type':'STRING','nullable':True},
                    'confidence':{'type':'NUMBER'},
                    'uncertain_fields':{'type':'ARRAY','items':{'type':'STRING'}},
                    'notes':{'type':'STRING'}
                },
                'required':['confidence','uncertain_fields','notes']
            }
        }
    }
    request=urllib.request.Request(
        ENDPOINT.format(model=MODEL),
        data=json.dumps(body).encode('utf-8'),
        headers={'Content-Type':'application/json','x-goog-api-key':api_key},
        method='POST'
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            result=json.loads(response.read().decode('utf-8'))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError('Gemini analysis request failed.') from exc
    text=result.get('candidates',[{}])[0].get('content',{}).get('parts',[{}])[0].get('text','')
    if not text:
        raise RuntimeError('Gemini returned no analysis.')
    try:
        parsed=json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError('Gemini returned invalid structured analysis.') from exc
    parsed['source']='Gemini suggestion; human review required'
    return parsed
