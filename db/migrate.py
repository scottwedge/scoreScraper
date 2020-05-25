import os
from sqlalchemy import create_engine
import nba

USER = os.environ["dbName"]
PASSWORD = os.environ["dbPass"]

if __name__ == "__main__":
    engine = create_engine(
        f"postgresql://{USER}:{PASSWORD}@localhost:5432/nba_stats", echo=True
    )
    nba.Base.metadata.create_all(engine)
