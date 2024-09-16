from fastapi import FastAPI


app = FastAPI()


@app.get("/conf/")
async def home():
   return {"data": "Data will be available soon"}
