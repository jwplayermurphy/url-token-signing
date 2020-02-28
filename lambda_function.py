from jose import jwt
import math
import json
import time
import hashlib
from urllib import parse

def lambda_handler(event, context):
    
    video_key = event['queryStringParameters']['media_id']  # example video key
    playlist_key = event['queryStringParameters']['playlist_id']  # example video key
    player_key = event['queryStringParameters']['player_id']  # example player key
    secret = "mysecretstring"
    list_of_domains = ['http://anillosguillen.com', 'https://anillosguillen.com', 'http://localhost', 'https://se.jwplayer.com']
    
    def get_signed_player(video_key, player_key, secret):
        path = "libraries/{player_key}.js".format(
            player_key=player_key
        )
        expires = round((time.time() + 3600) / 300) * 300
        secret = secret
        hashedString = "{path}:{exp}:{secret}".format(path=path,exp=str(expires), secret=secret).encode('utf-8')
        signature = hashlib.md5(hashedString)
        url = "https://cdn.jwplayer.com/{path}?exp={exp}&sig={sig}".format(
            path=path, exp=str(expires), sig=signature.hexdigest()
        )
        return url
    
    def jwt_sign_url(media_key, host='http://cdn.jwplayer.com/v2/', route, secret):
        secret = secret
        exp = math.ceil((time.time() + 3600)/180) * 180 # Link is valid for 1hr but normalized to 3 minutes to promote better caching

        token_body = {
            "resource": "/v2/" + route + "/" + media_key,
            "exp": exp
        }
    
        url = host + media_key + '?sig={signature}'.format(host=host, signature=jwt.encode(token_body, secret, algorithm='HS256'))
        return url
    
    if 'origin' in event['headers'] and event['headers']['origin'] in list_of_domains :
        player_url = get_signed_player(video_key, player_key, secret)
        
        if playlist_key != "":
            signed_url = jwt_sign_url(playlist_key, "playlists", secret)
        else:
            signed_url = jwt_sign_url(video_key, "media", secret)
        
        return {
            "statusCode": 200,
            "body": signed_url + "," + player_url
        }
    else:
        return {
            "statusCode": 403,
            "body": "403 Forbidden: You Do Not Have Access to This Service"
        }