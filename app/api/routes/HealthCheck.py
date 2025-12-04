from fastapi import APIRouter
from fastapi.responses import JSONResponse

 
health_check_router = APIRouter(tags=["health_check"])

@health_check_router.get("/health")
def health_check():
    return JSONResponse({'message': "Service is up and running"}, status_code=200)

