from typing import Annotated

from fastapi import Depends
from models import Session


def get_session():
    with Session() as session:
        yield session


SessionDependency = Annotated[Session, Depends(get_session)]
