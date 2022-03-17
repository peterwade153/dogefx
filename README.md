# dogefx
Forex exchange API

Built with Python 3.8, FastAPI. Requires Installation of Redis

Create An account with Openexchangerates to get an API KEY @ https://openexchangerates.org/ 


### Installation

1. Create and activate a virtual environment and Clone the project `https://github.com/peterwade153/dogefx.git`

2. Move into the project folder
   ```
    cd dogefx
   ```

3. Install dependencies 
   ```
    pip install -r requirements.txt
   ```

4. Create a `.env` file from the `.env.sample` file. 

5. Replace the variables in the sample file with the actual variables e.g. API KEY etc.

### Start Redis Server
```
redis-server
```

### Start Server
```
uvicorn main:app --reload
```

#### The API is the accessible at the URL below
```
http://localhost:8000/docs
```