"""Authentication and authorization utilities."""
from functools import wraps
from flask import session, redirect, url_for, flash, request
from typing import Callable, Any


def login_required(view_func: Callable[..., Any]):
    """Decorator to require user login."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Vui lòng đăng nhập.")
            return redirect(url_for("login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapped


def admin_required(view_func: Callable[..., Any]):
    """Decorator to require admin role."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Vui lòng đăng nhập.")
            return redirect(url_for("login", next=request.path))
        if session.get("role") != "admin":
            flash("Bạn không có quyền truy cập.")
            return redirect(url_for("home"))
        return view_func(*args, **kwargs)
    return wrapped

