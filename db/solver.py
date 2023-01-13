from sqlmodel import select
from .settings import session
from db.models.solver import Solver

def set_points(user_id, points):
    solver = session.exec(select(Solver).where(Solver.user_id == id)).first()
    solver.points += points
    session.add(solver)
    session.commit()
    session.refresh(solver)
    return {"msg": "set"}
def close_game(user_id):
    session.delete(session.exec(select(Solver).where(Solver.user_id == id)).first())
    return {"msg": "deleted"}