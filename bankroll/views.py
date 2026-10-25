from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SessionForm
from .models import Session

def add_session(request):
    form = SessionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("bankroll:dashboard")
    return render(request, "bankroll/session_form.html", {"form": form, "is_edit": False})


def modify_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    form = SessionForm(request.POST or None, instance=session)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("bankroll:dashboard")
    return render(request, "bankroll/session_form.html", {"form": form, "is_edit": True, "session": session})

def dashboard(request):
    sessions = Session.objects.order_by("-session_start")
    totals = sessions.aggregate(total_buyin=Sum("buyin"), total_buyout=Sum("buyout"))
    total_buyin = totals["total_buyin"] or 0
    total_buyout = totals["total_buyout"] or 0

    context = {
        "sessions": sessions,
        "total_sessions": sessions.count(),
        "total_buyin": total_buyin,
        "total_buyout": total_buyout,
        "net_profit": total_buyout - total_buyin,
        "winning_sessions": sum(session.profit > 0 for session in sessions),
    }
    return render(request, "bankroll/dashboard.html", context)