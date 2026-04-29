from app.database import Base, SessionLocal, engine
from app.models import Calculation


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_persist_calculation_row_and_query_back():
    db = SessionLocal()
    try:
        calc = Calculation.create("multiplication", [2, 3, 4])
        calc.result = calc.get_result()
        db.add(calc)
        db.commit()
        db.refresh(calc)

        row = db.query(Calculation).filter(Calculation.id == calc.id).first()

        assert row is not None
        assert row.a == 2
        assert row.b == 3
        assert row.type == "multiplication"
        assert row.inputs == [2, 3, 4]
        assert row.result == 24
    finally:
        db.close()
