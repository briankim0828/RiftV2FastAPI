from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from secrets import token_hex
import uvicorn
import os

app = FastAPI(title="Upload and Stream Videos")

# Directory where uploaded videos will be stored
video_directory = "videos"
os.makedirs(video_directory, exist_ok=True)

app.mount("/videos", StaticFiles(directory=video_directory), name="videos")

@app.delete("/delete/{file_name}")
async def delete_file(file_name: str):
    file_path = os.path.join(video_directory, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"success": True, "message": "File deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="File not found")


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_ext = file.filename.split(".").pop()
    if file_ext not in ["mp4", "avi", "MOV"]:  # Add or remove file types as needed
        raise HTTPException(status_code=400, detail="Unsupported file type")

    file_name = token_hex(10)
    file_path = f"{video_directory}/{file_name}.{file_ext}"
    with open(file_path, 'wb') as f:
        content = await file.read()
        f.write(content)
    return {"success": True, "file_path": f"/videos/{file_name}.{file_ext}", "message": "File upload successful"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 

