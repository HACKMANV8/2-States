"""
Sample file demonstrating MCDC (Modified Condition/Decision Coverage) analysis.

This file contains various boolean conditions that require MCDC testing.
Use with: python coverage/cli.py analyze-mcdc examples/sample_mcdc.py
"""


def check_user_access(user, resource):
    """
    Check if user has access to resource.

    MCDC Condition: is_authenticated AND (is_admin OR is_public)
    Required Tests: 6

    Test Cases for MCDC:
    1. T | T | T → True  (all true)
    2. T | T | F → True  (admin access)
    3. T | F | T → True  (public access)
    4. T | F | F → False (no access)
    5. F | T | T → False (not authenticated)
    6. F | F | T → False (not authenticated)
    """
    if user.is_authenticated and (user.is_admin or resource.is_public):
        return True
    return False


def validate_payment(payment, user):
    """
    Validate payment can be processed.

    MCDC Condition: has_funds AND (is_verified OR is_trusted_merchant)
    """
    if payment.has_funds and (user.is_verified or user.is_trusted_merchant):
        return True
    return False


def should_send_notification(user, notification):
    """
    Determine if notification should be sent.

    MCDC Condition: is_enabled AND NOT is_quiet_hours AND (is_urgent OR is_important)
    """
    if user.notifications_enabled and not notification.is_quiet_hours and (notification.is_urgent or notification.is_important):
        return True
    return False


def complex_authorization(user, action, resource):
    """
    Complex authorization logic with multiple conditions.

    MCDC Condition:
    (is_owner OR is_admin) AND
    (has_permission OR resource_public) AND
    NOT is_suspended
    """
    if (user.is_owner or user.is_admin) and (user.has_permission or resource.is_public) and not user.is_suspended:
        return True
    return False


def simple_condition(value):
    """
    Simple condition (not MCDC - only one condition).
    """
    if value > 0:
        return True
    return False


def while_loop_condition(items):
    """
    While loop with complex condition.
    """
    index = 0
    result = []

    while index < len(items) and items[index].is_valid:
        result.append(items[index])
        index += 1

    return result


# Expected MCDC Analysis Output:
# ================================
#
# Decision 1: check_user_access
#   Conditions: 3 (is_authenticated, is_admin, is_public)
#   Required Tests: 6
#   Truth Table Rows: 8
#   Minimum Test Set: T1, T2, T3, T4, T5, T6
#
# Decision 2: validate_payment
#   Conditions: 3 (has_funds, is_verified, is_trusted_merchant)
#   Required Tests: 6
#
# Decision 3: should_send_notification
#   Conditions: 4 (is_enabled, NOT is_quiet_hours, is_urgent, is_important)
#   Required Tests: 8
#
# Decision 4: complex_authorization
#   Conditions: 5 (is_owner, is_admin, has_permission, is_public, NOT is_suspended)
#   Required Tests: 10
#
# Decision 5: while_loop_condition
#   Conditions: 2 (index < len, is_valid)
#   Required Tests: 4
