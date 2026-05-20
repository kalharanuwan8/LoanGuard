from fastapi import APIRouter, Depends
from backend.schemas import LoanApplicant, PredictionResult
from backend.database import predictions_col
from backend.routes.auth import get_current_user
from model.predict import predict_risk
from datetime import datetime

router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post("", response_model=PredictionResult)
async def predict(
    applicant: LoanApplicant,
    current_user: dict = Depends(get_current_user)   # requires login
):
    input_data = applicant.dict()
    result     = predict_risk(input_data)

    # Save to MongoDB audit log
    await predictions_col.insert_one({
        "officer_id":   str(current_user["_id"]),
        "officer_name": current_user["name"],
        "input":        input_data,
        "result":       result,
        "created_at":   datetime.utcnow()
    })

    return result