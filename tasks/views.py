import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .scoring import score_tasks, detect_cycles

@csrf_exempt
def analyze_tasks(request):
    if request.method != 'POST':
        return HttpResponseBadRequest(json.dumps({"error": "POST only"}), content_type="application/json")
    try:
        payload = json.loads(request.body.decode('utf-8'))
        tasks = payload.get('tasks') if isinstance(payload, dict) else payload
        weights = payload.get('weights') if isinstance(payload, dict) else None
        if tasks is None:
            return HttpResponseBadRequest(json.dumps({"error": "tasks key missing or body must be a list"}), content_type="application/json")
    except Exception as e:
        return HttpResponseBadRequest(json.dumps({"error": "invalid json", "detail": str(e)}), content_type="application/json")

    cycles = detect_cycles(tasks)
    if cycles:
        return JsonResponse({"error": "circular_dependencies", "cycles": cycles}, status=400)

    scored = score_tasks(tasks, weights=weights)
    return JsonResponse({"tasks": scored})

@csrf_exempt
def suggest_tasks(request):
    if request.method != 'POST':
        return HttpResponseBadRequest(json.dumps({"error": "POST only"}), content_type="application/json")
    try:
        payload = json.loads(request.body.decode('utf-8'))
        tasks = payload.get('tasks') if isinstance(payload, dict) else payload
        weights = payload.get('weights') if isinstance(payload, dict) else None
        if tasks is None:
            return HttpResponseBadRequest(json.dumps({"error": "tasks key missing or body must be a list"}), content_type="application/json")
    except Exception as e:
        return HttpResponseBadRequest(json.dumps({"error": "invalid json", "detail": str(e)}), content_type="application/json")

    cycles = detect_cycles(tasks)
    if cycles:
        return JsonResponse({"error": "circular_dependencies", "cycles": cycles}, status=400)

    scored = score_tasks(tasks, weights=weights)
    top3 = scored[:3]
    suggestions = []
    for t in top3:
        reasons = []
        if "past due" in t.get('_explanation', '').lower():
            reasons.append("Overdue")
        if t.get('importance', 0) >= 8:
            reasons.append("High importance")
        if float(t.get('estimated_hours', 1.0)) <= 2:
            reasons.append("Quick win")
        suggestions.append({"task": t, "reason_summary": ", ".join(reasons) or "Balanced priority"})
    return JsonResponse({"suggestions": suggestions})

