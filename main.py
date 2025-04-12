import uvicorn

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, workers=2, log_level="debug")
    # ssl_keyfile="ssl/key.pem",
    # reload=True,
    # ssl_certfile="ssl/cert.pem")