from datetime import datetime, date

def parse_date(d):
    if not d:
        return None
    if isinstance(d, (date, datetime)):
        return d if isinstance(d, date) else d.date()
    try:
        return datetime.fromisoformat(d).date()
    except:
        # fallback: try common format
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(d, fmt).date()
            except:
                continue
    return None

def detect_cycles(tasks):
    id_map = {t.get("id", i): t for i, t in enumerate(tasks)}
    graph = {tid: [dep for dep in (id_map.get(tid, {}).get('dependencies') or [])] for tid in id_map}
    # Better build adjacency: node -> its dependencies
    graph = {}
    for i, t in enumerate(tasks):
        tid = t.get("id", i)
        deps = t.get("dependencies", []) or []
        graph[tid] = deps

    visited = set()
    stack = set()
    cycles = []

    def dfs(node, path):
        if node in stack:
            # cycle slice
            if node in path:
                cycles.append(path[path.index(node):] + [node])
            else:
                cycles.append(path + [node])
            return
        if node in visited:
            return
        visited.add(node)
        stack.add(node)
        path.append(node)
        for nb in graph.get(node, []):
            if nb in graph:
                dfs(nb, path)
        path.pop()
        stack.remove(node)

    for n in list(graph.keys()):
        if n not in visited:
            dfs(n, [])

    return cycles

def score_tasks(tasks, weights=None, today=None, max_days=30):
    if weights is None:
        weights = {"urgency": 0.35, "importance": 0.30, "effort": 0.15, "dependencies": 0.20}
    if today is None:
        today = date.today()

    # normalize and map ids
    id_map = {}
    for idx, t in enumerate(tasks):
        t.setdefault('id', t.get('id', idx))
        t.setdefault('title', t.get('title', f"Task {idx}"))
        t.setdefault('estimated_hours', float(t.get('estimated_hours', 1.0) or 1.0))
        t.setdefault('importance', int(t.get('importance', 5) or 5))
        deps = t.get('dependencies', []) or []
        t['dependencies'] = deps
        id_map[t['id']] = t

    # dep count (how many tasks depend on this task)
    dep_count = {}
    for t in tasks:
        for d in t.get('dependencies', []):
            dep_count[d] = dep_count.get(d, 0) + 1
    max_dep_count = max(dep_count.values()) if dep_count else 1

    scored = []
    for t in tasks:
        expl = []
        due = parse_date(t.get('due_date'))
        if due is None:
            urgency_score = 0.0
            expl.append("no due date (low urgency)")
        else:
            days_left = (due - today).days
            if days_left < 0:
                urgency_score = 1.0
                expl.append(f"past due by {-days_left} day(s)")
            else:
                urgency_score = max(0.0, min(1.0, (max_days - days_left)/max_days))
                expl.append(f"due in {days_left} day(s)")
        importance_score = max(0.0, min(1.0, t.get('importance', 5) / 10.0))
        expl.append(f"importance {t.get('importance')}")
        est = float(t.get('estimated_hours', 1.0) or 1.0)
        effort_score = 1.0 / (1.0 + est)
        expl.append(f"estimated_hours {est}")
        dcount = dep_count.get(t['id'], 0)
        deps_score = (dcount / max_dep_count) if max_dep_count > 0 else 0.0
        expl.append(f"blocks {dcount} task(s)")
        final_score = (weights['urgency'] * urgency_score +
                       weights['importance'] * importance_score +
                       weights['effort'] * effort_score +
                       weights['dependencies'] * deps_score)
        t_copy = t.copy()
        t_copy['_score'] = round(final_score, 4)
        t_copy['_explanation'] = "; ".join(expl)
        scored.append(t_copy)

    # tie-breakers included in sort key
    scored.sort(key=lambda x: (-x['_score'], -x.get('importance', 0), x.get('estimated_hours', float('inf'))))
    return scored
