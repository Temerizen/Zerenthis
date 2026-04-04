def has_permission(role, required):
    hierarchy = ["user", "admin", "founder"]
    return hierarchy.index(role) >= hierarchy.index(required)
