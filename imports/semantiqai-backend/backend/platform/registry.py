MODULE_REGISTRY = [
    {"name": "cognitive_lab", "import_path": "backend.cognitive_lab.routes", "blueprint_name": "cognitive_lab", "group": "intelligence", "route": "/cognitive"},
    {"name": "ai_school", "import_path": "backend.ai_school.routes", "blueprint_name": "ai_school", "group": "learning", "route": "/learning"},
    {"name": "execution_engine", "import_path": "backend.execution_engine.routes", "blueprint_name": "execution_engine", "group": "action", "route": "/execution"},
    {"name": "simulation_engine", "import_path": "backend.simulation_engine.routes", "blueprint_name": "simulation_engine", "group": "strategy", "route": "/simulation"},
    {"name": "creation_engine", "import_path": "backend.creation_engine.routes", "blueprint_name": "creation_engine", "group": "creation", "route": "/creation"},
    {"name": "founder_video", "import_path": "backend.founder_video.routes", "blueprint_name": "founder_video", "group": "media", "route": "/founder"},
    {"name": "founder_distribution", "import_path": "backend.founder_distribution.routes", "blueprint_name": "founder_distribution", "group": "media", "route": "/founder"},
    {"name": "founder_panel", "import_path": "backend.founder_panel.routes", "blueprint_name": "founder_panel", "group": "control", "route": "/founder"},
    {"name": "auth_system", "import_path": "backend.auth_system.routes", "blueprint_name": "auth_system", "group": "security", "route": "/login"},
    {"name": "stabilization", "import_path": "backend.stabilization.routes", "blueprint_name": "stabilization", "group": "stability", "route": "/dashboard"},
    {"name": "integration", "import_path": "backend.integration.routes", "blueprint_name": "integration", "group": "core", "route": "/dashboard"},
    {"name": "finance", "import_path": "backend.finance_system.routes", "blueprint_name": "finance", "group": "user", "route": "/dashboard"},
    {"name": "health", "import_path": "backend.health_system.routes", "blueprint_name": "health", "group": "user", "route": "/dashboard"},
    {"name": "writing", "import_path": "backend.writing_studio.routes", "blueprint_name": "writing", "group": "user", "route": "/creation"},
    {"name": "research", "import_path": "backend.research_workspace.routes", "blueprint_name": "research", "group": "user", "route": "/dashboard"},
    {"name": "vault", "import_path": "backend.knowledge_vault.routes", "blueprint_name": "vault", "group": "user", "route": "/dashboard"},
    {"name": "analytics", "import_path": "backend.personal_analytics.routes", "blueprint_name": "analytics", "group": "user", "route": "/dashboard"},
    {"name": "life", "import_path": "backend.life_system.routes", "blueprint_name": "life", "group": "user", "route": "/dashboard"},
    {"name": "revenue", "import_path": "backend.revenue_engine.routes", "blueprint_name": "revenue", "group": "founder", "route": "/founder"},
    {"name": "campaign", "import_path": "backend.campaign_engine.routes", "blueprint_name": "campaign", "group": "founder", "route": "/founder"},
    {"name": "calendar", "import_path": "backend.content_calendar.routes", "blueprint_name": "calendar", "group": "founder", "route": "/founder"},
    {"name": "affiliate", "import_path": "backend.affiliate_system.routes", "blueprint_name": "affiliate", "group": "founder", "route": "/founder"},
    {"name": "growth", "import_path": "backend.growth_analytics.routes", "blueprint_name": "growth", "group": "founder", "route": "/founder"},
    {"name": "audience", "import_path": "backend.audience_engine.routes", "blueprint_name": "audience", "group": "founder", "route": "/founder"},
    {"name": "competitor", "import_path": "backend.competitor_engine.routes", "blueprint_name": "competitor", "group": "founder", "route": "/founder"}
]

MODULE_REGISTRY += [
    {"name": "cleanup", "import_path": "backend.cleanup.routes", "blueprint_name": "cleanup", "group": "core", "route": "/dashboard"}
]
