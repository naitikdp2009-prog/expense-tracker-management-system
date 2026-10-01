from services.analytics import get_dashboard_summary

def evaluate_purchase_decision(product_name, price, category_name, need_or_want, urgency):
    """
    Evaluates whether the user should BUY, WAIT, or AVOID a planned purchase.
    Uses realistic financial rule algorithms based on user budget, balance, need level, and urgency.
    """
    summary = get_dashboard_summary()
    
    current_balance = summary['current_balance']
    remaining_budget = summary['remaining_budget']
    monthly_budget = summary['monthly_budget']
    monthly_income = summary['monthly_income'] if summary['monthly_income'] > 0 else 25000.0

    price = float(price)
    need_or_want = need_or_want.lower()
    urgency = urgency.lower()

    # Calculate metrics
    pct_of_remaining_budget = (price / remaining_budget * 100) if remaining_budget > 0 else 100.0
    pct_of_monthly_budget = (price / monthly_budget * 100) if monthly_budget > 0 else 100.0
    est_remaining_after = max(0, remaining_budget - price)
    est_balance_after = current_balance - price

    # Recommendation Logic
    recommendation = "WAIT"
    reason = ""
    alternative_action = ""
    badge_color = "warning"

    if est_balance_after < 0:
        recommendation = "AVOID"
        badge_color = "danger"
        reason = f"Purchasing '{product_name}' for ₹{price:,.2f} exceeds your current total balance of ₹{current_balance:,.2f}. You would go into debt."
        alternative_action = "Save up for this product or find a cheaper alternative within your current balance."

    elif price > remaining_budget:
        if need_or_want == 'need' and urgency == 'high':
            recommendation = "BUY WITH CAUTION"
            badge_color = "warning"
            reason = f"This purchase exceeds your remaining monthly budget by ₹{(price - remaining_budget):,.2f}, but it is classified as a high-urgency Need."
            alternative_action = "Reallocate funds from another category (like Entertainment or Shopping) to cover this purchase."
        else:
            recommendation = "AVOID"
            badge_color = "danger"
            reason = f"This purchase exceeds your remaining monthly budget limit (₹{remaining_budget:,.2f})."
            alternative_action = "Postpone this purchase to next month when your monthly budget resets."

    elif pct_of_remaining_budget <= 25:
        recommendation = "BUY"
        badge_color = "success"
        reason = f"'{product_name}' takes only {round(pct_of_remaining_budget, 1)}% of your remaining budget. Your post-purchase budget remains comfortable at ₹{est_remaining_after:,.2f}."
        alternative_action = "Proceed with purchase! You still have plenty of safety margin in your budget."

    elif pct_of_remaining_budget <= 60:
        if need_or_want == 'need':
            recommendation = "BUY"
            badge_color = "success"
            reason = f"As an essential Need, this fits within your remaining budget, leaving ₹{est_remaining_after:,.2f} for the rest of the month."
            alternative_action = "Safe to buy, but monitor non-essential expenses for the remainder of the month."
        elif urgency == 'low':
            recommendation = "WAIT"
            badge_color = "warning"
            reason = f"This item is a low-urgency Want that will absorb {round(pct_of_remaining_budget, 1)}% of your remaining budget."
            alternative_action = "Wait 7 to 14 days. If you still want it after reflection, re-evaluate your remaining balance."
        else:
            recommendation = "BUY"
            badge_color = "info"
            reason = f"This purchase consumes {round(pct_of_remaining_budget, 1)}% of your remaining budget. You have sufficient headroom."
            alternative_action = "Proceed, but avoid additional major discretionary purchases this week."

    else: # > 60% of remaining budget
        if need_or_want == 'want':
            recommendation = "WAIT"
            badge_color = "warning"
            reason = f"This discretionary 'Want' takes {round(pct_of_remaining_budget, 1)}% of your remaining budget, leaving only ₹{est_remaining_after:,.2f} for unexpected expenses."
            alternative_action = "Wait until the start of next month or look for seasonal discounts."
        else:
            recommendation = "BUY WITH CAUTION"
            badge_color = "warning"
            reason = f"This essential purchase absorbs {round(pct_of_remaining_budget, 1)}% of your remaining budget."
            alternative_action = "Delay non-essential expenses for the rest of the month to maintain cash flow."

    return {
        'product_name': product_name,
        'price': price,
        'category_name': category_name,
        'need_or_want': need_or_want,
        'urgency': urgency,
        'recommendation': recommendation,
        'badge_color': badge_color,
        'reason': reason,
        'alternative_action': alternative_action,
        'budget_impact_pct': round(pct_of_remaining_budget, 1),
        'remaining_budget_before': remaining_budget,
        'remaining_budget_after': est_remaining_after,
        'current_balance': current_balance,
        'balance_after': est_balance_after
    }

def simulate_what_if(current_spending, purchase_amount, monthly_budget):
    """
    Computes What-If comparison before and after a proposed purchase.
    """
    current_spending = float(current_spending)
    purchase_amount = float(purchase_amount)
    monthly_budget = float(monthly_budget)

    new_spending = current_spending + purchase_amount
    current_remaining = max(0, monthly_budget - current_spending)
    new_remaining = max(0, monthly_budget - new_spending)

    current_usage_pct = (current_spending / monthly_budget * 100) if monthly_budget > 0 else 0
    new_usage_pct = (new_spending / monthly_budget * 100) if monthly_budget > 0 else 0

    savings_impact = purchase_amount
    is_over_budget = new_spending > monthly_budget

    return {
        'current': {
            'spending': current_spending,
            'remaining': current_remaining,
            'usage_pct': round(current_usage_pct, 1)
        },
        'after': {
            'spending': new_spending,
            'remaining': new_remaining,
            'usage_pct': round(new_usage_pct, 1)
        },
        'purchase_amount': purchase_amount,
        'savings_impact': savings_impact,
        'is_over_budget': is_over_budget,
        'over_budget_amount': max(0, new_spending - monthly_budget)
    }
