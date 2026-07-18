"""
Support ticket endpoints. A ticket is just an escalation record tied to
the logged-in user - creating one gives back a unique ticket_id the user
can track later via GET /tickets.
"""
from typing import List
from fastapi import APIRouter, Depends
from models.schemas import TicketCreateRequest, Ticket
from database import mongo
from api.auth_routes import get_current_user

router = APIRouter(tags=["tickets"])


@router.post("/tickets", response_model=Ticket)
def raise_ticket(req: TicketCreateRequest, user_email: str = Depends(get_current_user)):
    ticket = mongo.create_ticket(
        user_email=user_email,
        subject=req.subject,
        description=req.description,
        session_id=req.session_id,
    )
    return Ticket(**ticket)


@router.get("/tickets", response_model=List[Ticket])
def get_my_tickets(user_email: str = Depends(get_current_user)):
    tickets = mongo.list_tickets_for_user(user_email)
    return [Ticket(**t) for t in tickets]
