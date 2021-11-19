import requests
from fastapi import FastAPI, Depends, HTTPException
from pymongo import MongoClient

from .schema import UserDetails
from .auth import AuthHandler
from .config import mongo_url

app = FastAPI()
client = MongoClient(mongo_url)
authHandler = AuthHandler()

users = []
db = client['fastapi-db']
user_collection = db['users']

@app.post('/sign-up')
def signup(userDetails: UserDetails):
    
    user = db.user_collection.find_one({ 'username': userDetails.username })
    if user is None:

        hashedPassword = authHandler.get_password_hash(userDetails.password)

        db.user_collection.insert_one({
            'username': userDetails.username,
            'password': hashedPassword
        })

        return {
            'success': True,
            'message': 'User created successfully!'
        }

    else:
        return {
            'success': False,
            'message': 'Username already exists!'
        }


@app.post('/sign-in')
def signin(userDetails: UserDetails):

    user = db.user_collection.find_one({ 'username': userDetails.username })
    if user is not None:
    
        if not authHandler.verify_password(userDetails.password, user['password']):
            raise HTTPException(status_code=401, detail='Invalid username and/or password')
            
        token = authHandler.encode_token(user['username'])
        return {
            'success': True,
            'message': 'User signed in successfully',
            'token': token
        }

    else:
        return {
            'success': False,
            'message': 'User not found!'
        }

@app.get("/")
def search(search: str, username=Depends(authHandler.auth_wrapper)):
    url = "https://imdb8.p.rapidapi.com/auto-complete"
    querystring = { "q": search }

    headers = {
        'x-rapidapi-host': "imdb8.p.rapidapi.com",
        'x-rapidapi-key': "58c8afa833mshcd673019e6cc4b7p1e8d3bjsn9cf0587dcbf2"
    }

    response = requests.request('GET', url, headers=headers, params=querystring)
    return { 'data': response.json() }
