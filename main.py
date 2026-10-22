from fastapi import FastAPI

app = FastAPI()

@app.get("/Welcome")
def Welcome():
    return {
        "Message" : "Hellooooooo"
    }