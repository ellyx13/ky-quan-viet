from fastapi import APIRouter
from modules.v1.health import routers as health_routers
from modules.v1.tasks import routers as tasks_routers
from modules.v1.games import routers as games_routers
from modules.v1.histories import routers as histories_routers
from users import routers as users_routers

api_routers = APIRouter()

# Healthy check
api_routers.include_router(health_routers.router)

# Users
api_routers.include_router(users_routers.router)

# Modules
api_routers.include_router(tasks_routers.router)

# Modules
api_routers.include_router(games_routers.router)

# Modules
api_routers.include_router(histories_routers.router)