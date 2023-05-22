# Import all the models, so that Base has them before being
# imported by Alembic

from .database import Base
from src.auth.models import User
from src.fault.models import Image, Fault
from src.project.models import Project

