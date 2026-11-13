from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import current_user
from ..models import AuditLog, Ticket, User
from ..schemas import TicketAssignIn, TicketIn, TicketOut

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

@router.get("", response_model=list[TicketOut])
def list_tickets(user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = select(Ticket).order_by(Ticket.created_at.desc())
    if user.role != "admin":
        query = query.where(Ticket.assigned_to == user.id)
    return list(db.scalars(query))

@router.post("", response_model=TicketOut, status_code=201)
def create_ticket(data: TicketIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    ticket = Ticket(**data.model_dump(), created_by=user.id)
    db.add(ticket)
    db.flush()
    db.add(AuditLog(actor_id=user.id, action="ticket_created", entity_type="ticket", entity_id=ticket.id))
    db.commit()
    db.refresh(ticket)
    return ticket

@router.post("/{ticket_id}/assign", response_model=TicketOut)
def assign_ticket(ticket_id: int, data: TicketAssignIn, admin: User = Depends(current_user),
                  db: Session = Depends(get_db)):
    if admin.role != "admin":
        raise HTTPException(status_code=403, detail="Только для администратора")
    ticket = db.get(Ticket, ticket_id)
    worker = db.get(User, data.assigned_to)
    if ticket is None or worker is None or worker.role != "staff" or worker.status != "active":
        raise HTTPException(status_code=404, detail="Заявка или активный исполнитель не найден")
    ticket.assigned_to = worker.id
    db.add(AuditLog(actor_id=admin.id, action="ticket_assigned", entity_type="ticket", entity_id=ticket.id))
    db.commit()
    db.refresh(ticket)
    return ticket
