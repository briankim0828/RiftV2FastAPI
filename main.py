from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from secrets import token_hex
import uvicorn
import os

app = FastAPI(title="Upload and Stream Videos")

# Directory where uploaded videos will be stored
video_directory = "videos"
os.makedirs(video_directory, exist_ok=True)

app.mount("/videos", StaticFiles(directory=video_directory), name="videos")

@app.get("/list-videos")
async def list_videos():
    files = []
    for filename in os.listdir(video_directory):
        file_path = os.path.join(video_directory, filename)
        if os.path.isfile(file_path):
            files.append({
                "name": filename,
                "url": f"/videos/{filename}",
                "size": os.path.getsize(file_path),
                "last_modified": os.path.getmtime(file_path)
            })
    return files

@app.get("/stream/{file_name}", response_class=FileResponse)
async def stream_video(file_name: str):
    file_path = os.path.join(video_directory, file_name)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(path=file_path, media_type='video/mp4', filename=file_name)
    else:
        raise HTTPException(status_code=404, detail="File not found")

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
    # if file_ext not in ["mp4", "avi", "mov"]:  # Add or remove file types as needed
    #     raise HTTPException(status_code=400, detail="Unsupported file type")

    file_name = token_hex(10) + "." + file_ext
    file_path = os.path.join(video_directory, file_name)
    with open(file_path, 'wb') as f:
        content = await file.read()
        f.write(content)
    return {"success": True, "file_path": f"/videos/{file_name}", "message": "File upload successful"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000, reload=True)
