from django.http import Http404
from django.shortcuts import redirect, render

from account.decorators import django_login_required

from . import services as pf
from .forms import HoldingForm


@django_login_required
def portfolio_detail(request):
    uid = request.user.pk
    portfolio = pf.get_or_create_portfolio(uid)
    return render(
        request,
        "portfolio/detail.html",
        {"portfolio": portfolio, "holding_form": HoldingForm()},
    )


@django_login_required
def holding_add(request):
    uid = request.user.pk

    if request.method == "POST":
        form = HoldingForm(request.POST)
        if form.is_valid():
            pf.add_holding(uid, form.cleaned_data)
            portfolio = pf.get_or_create_portfolio(uid)
            if request.htmx:
                return render(
                    request,
                    "portfolio/_holdings_table.html",
                    {"portfolio": portfolio, "holding_form": HoldingForm()},
                )
            return redirect("portfolio:detail")

        if request.htmx:
            portfolio = pf.get_or_create_portfolio(uid)
            return render(
                request,
                "portfolio/_holdings_table.html",
                {"portfolio": portfolio, "holding_form": form},
                status=400,
            )
        return render(request, "portfolio/holding_form.html", {"form": form, "is_edit": False}, status=400)

    return render(request, "portfolio/holding_form.html", {"form": HoldingForm(), "is_edit": False})


@django_login_required
def holding_edit(request, holding_id):
    uid = request.user.pk
    holding = pf.get_holding(uid, holding_id)
    if holding is None:
        raise Http404

    if request.method == "POST":
        form = HoldingForm(request.POST)
        if form.is_valid():
            pf.update_holding(uid, holding_id, form.cleaned_data)
            portfolio = pf.get_or_create_portfolio(uid)
            if request.htmx:
                return render(
                    request,
                    "portfolio/_holdings_table.html",
                    {"portfolio": portfolio, "holding_form": HoldingForm()},
                )
            return redirect("portfolio:detail")

        if request.htmx:
            return render(
                request,
                "portfolio/_holding_edit_row.html",
                {"form": form, "holding": holding},
                status=400,
            )
        return render(request, "portfolio/holding_form.html", {"form": form, "is_edit": True}, status=400)

    initial = {
        "symbol": holding.symbol,
        "name": holding.name,
        "asset_type": holding.asset_type,
        "quantity": holding.quantity,
        "cost_basis_per_unit": holding.cost_basis_per_unit,
        "current_price": holding.current_price,
    }
    form = HoldingForm(initial=initial)
    if request.htmx:
        return render(request, "portfolio/_holding_edit_row.html", {"form": form, "holding": holding})
    return render(request, "portfolio/holding_form.html", {"form": form, "is_edit": True})


@django_login_required
def holding_delete(request, holding_id):
    uid = request.user.pk
    holding = pf.get_holding(uid, holding_id)
    if holding is None:
        raise Http404

    if request.method in ("POST", "DELETE"):
        pf.delete_holding(uid, holding_id)
        portfolio = pf.get_or_create_portfolio(uid)
        if request.htmx:
            return render(
                request,
                "portfolio/_holdings_table.html",
                {"portfolio": portfolio, "holding_form": HoldingForm()},
            )
        return redirect("portfolio:detail")

    return render(request, "portfolio/holding_confirm_delete.html", {"holding": holding})
