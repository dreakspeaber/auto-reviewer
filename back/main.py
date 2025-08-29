from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from reviewer import Reviewer

app = FastAPI(title="Auto Reviewer API", version="0.1.0")

# Add CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReviewRequest(BaseModel):
    content: str

class ReviewResponse(BaseModel):
    reviewed_content: str

@app.get("/")
async def root():
    return {"message": "Auto Reviewer API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/review", response_model=ReviewResponse)
async def review_content(request: ReviewRequest):
    """
    Mock endpoint that simulates content review.
    In a real implementation, this would use the GCP class to process the content.
    """
    try:
        content = request.content        
        reviewer = Reviewer()
        result = await reviewer.review(content)
        return ReviewResponse(
            reviewed_content=result.to_markdown())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing content: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
