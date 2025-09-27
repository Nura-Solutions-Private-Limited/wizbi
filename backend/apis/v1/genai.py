import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apis.v1.login import get_current_user_from_token
from db.models.models import User
from db.session import get_db
from db.views.genai import GenAi
from schemas.genai import (
    ConnectionQuestion,
    Conversation,
    FactQuestion,
    FactResponse,
    FollowUpQuestion,
    GenDashQuery,
    OtherQuestion,
    OtherResponse,
    QueryConversation,
    QueryConversationResponse,
)

router = APIRouter()

logger = structlog.getLogger(__name__)


@router.post("/factquestion", response_model=FactResponse)
def get_fact_question(factQuestion: FactQuestion,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user_from_token)):
    '''
    Get 25 questions based on fact table for a pipeline
    '''
    genAi = GenAi(db=db)
    return genAi.fact_questions(pipeline_id=factQuestion.pipeline_id)


@router.post("/connection/question")
def get_connection_question(connectionQuestion: ConnectionQuestion,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user_from_token)):
    '''
    Get answer of follow up question
    '''
    genAi = GenAi(db=db)
    return genAi.connection_question(connectionQuestion=connectionQuestion)


@router.post("/followup-question")
def get_followup_question(followUpQuestion: FollowUpQuestion,
                          db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user_from_token)):
    '''
    Get answer of follow up question
    '''
    genAi = GenAi(db=db)
    return genAi.fact_follow_up_question(followUpQuestion=followUpQuestion)


@router.post("/otherquestion", response_model=OtherResponse)
def get_other_answer(otherQuestion: OtherQuestion,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user_from_token)):
    '''
    Get response for random question from user
    '''
    genAi = GenAi(db=db)
    return genAi.other_questions(question=otherQuestion.question)


@router.post("/gen-dashboard", response_model=OtherResponse)
def gen_dashboard_by_pipeline(
    # pipeline_id: str = Query( None, description="Pipeline ID" ),
    genDashQuery: GenDashQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    '''
    Use the given Data Warehouse pipeline to ask
    chatGPT to create SQL queries.
    Returns the AI response to the frontend.
    '''
    genAi = GenAi(db=db)
    return genAi.gen_dashboard(
        pipeline_id=genDashQuery.pipeline_id,
        prompt=genDashQuery.prompt
    )


@router.post("/conversation")
def create_conversation(
    conversation: Conversation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    '''
    Create a new conversation with the GenAI model.
    '''
    genAi = GenAi(db=db)
    return genAi.create_conversation(conversation=conversation, user_id=current_user.id)


@router.post("/coversation/query", response_model=QueryConversationResponse)
def ask_question(
    conversation: QueryConversation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    '''
    Ask a question to the GenAI model.
    '''
    genAi = GenAi(db=db)
    return genAi.ask_question(conversation=conversation, user_id=current_user.id)


@router.get("/conversations")
def get_conversation_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    '''
    Get the user's conversation history.
    '''
    genAi = GenAi(db=db)
    return genAi.get_conversation_history(user_id=current_user.id)


@router.get("/conversations/{id}")
def get_conversation_history_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    '''
    Get the conversation history by conversation ID.
    '''
    genAi = GenAi(db=db)
    return genAi.get_conversation_history_by_id(
        user_id=current_user.id, conversation_id=id
    )
