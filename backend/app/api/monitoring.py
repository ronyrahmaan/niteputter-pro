"""
Monitoring and Health Check Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
from datetime import datetime, UTC
import asyncio
import psutil
import os
from app.database import get_database, mongodb_client
from app.core.config import settings
from app.core.security import get_current_user
from app.models.user import User
import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

async def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client"""
    if settings.redis_url:
        try:
            return await redis.from_url(
                settings.redis_url,
                decode_responses=settings.redis_decode_responses
            )
        except Exception:
            return None
    return None


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint
    Returns 200 if service is running
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "service": settings.app_name,
        "environment": settings.app_env,
        "version": "1.0.0"
    }


@router.get("/readiness", status_code=status.HTTP_200_OK)
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check for Kubernetes
    Checks if all dependencies are available
    """
    checks = {
        "mongodb": False,
        "redis": False,
        "stripe": False
    }
    details = {}
    
    # Check MongoDB
    try:
        db = await get_database()
        await db.command("ping")
        checks["mongodb"] = True
        details["mongodb"] = "Connected"
    except Exception as e:
        details["mongodb"] = f"Error: {str(e)}"
    
    # Check Redis
    try:
        redis_client = await get_redis_client()
        if redis_client:
            await redis_client.ping()
            checks["redis"] = True
            details["redis"] = "Connected"
        else:
            details["redis"] = "Not configured"
    except Exception as e:
        details["redis"] = f"Error: {str(e)}"
    
    # Check Stripe
    try:
        import stripe
        stripe.api_key = settings.get_stripe_key()
        # Simple API call to check connectivity
        stripe.Balance.retrieve()
        checks["stripe"] = True
        details["stripe"] = "Connected"
    except Exception as e:
        details["stripe"] = f"Error: {str(e)}"
    
    # Determine overall status
    all_healthy = all(checks.values())
    status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content={
            "ready": all_healthy,
            "checks": checks,
            "details": details,
            "timestamp": datetime.now(UTC).isoformat()
        }
    )


@router.get("/metrics", status_code=status.HTTP_200_OK)
async def get_metrics(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get application metrics
    Requires admin authentication
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # System metrics
    process = psutil.Process(os.getpid())
    system_metrics = {
        "cpu_percent": process.cpu_percent(),
        "memory_mb": process.memory_info().rss / 1024 / 1024,
        "memory_percent": process.memory_percent(),
        "num_threads": process.num_threads(),
        "uptime_seconds": (datetime.now(UTC) - datetime.fromtimestamp(process.create_time(), UTC)).total_seconds()
    }
    
    # Database metrics
    db_metrics = {}
    try:
        db = await get_database()
        
        # Get collection stats
        collections = ["products", "users", "orders", "carts", "reviews"]
        for collection in collections:
            count = await db[collection].count_documents({})
            db_metrics[f"{collection}_count"] = count
        
        # Get database stats
        stats = await db.command("dbStats")
        db_metrics["database_size_mb"] = stats.get("dataSize", 0) / 1024 / 1024
        db_metrics["index_size_mb"] = stats.get("indexSize", 0) / 1024 / 1024
    except Exception as e:
        db_metrics["error"] = str(e)
    
    # Redis metrics
    redis_metrics = {}
    try:
        redis_client = await get_redis_client()
        if redis_client:
            info = await redis_client.info()
            redis_metrics = {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_mb": info.get("used_memory", 0) / 1024 / 1024,
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            }
    except Exception as e:
        redis_metrics["error"] = str(e)
    
    # Application metrics
    app_metrics = {
        "environment": settings.app_env,
        "debug_mode": settings.app_debug,
        "features": settings.get_feature_flags()
    }
    
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "system": system_metrics,
        "database": db_metrics,
        "redis": redis_metrics,
        "application": app_metrics
    }


@router.get("/status", status_code=status.HTTP_200_OK)
async def detailed_status(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get detailed system status
    Requires admin authentication
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    status_report = {
        "timestamp": datetime.now(UTC).isoformat(),
        "environment": settings.app_env,
        "services": {}
    }
    
    # MongoDB Status
    try:
        db = await get_database()
        server_info = await db.command("serverStatus")
        status_report["services"]["mongodb"] = {
            "status": "operational",
            "version": server_info.get("version"),
            "uptime": server_info.get("uptime"),
            "connections": {
                "current": server_info.get("connections", {}).get("current"),
                "available": server_info.get("connections", {}).get("available")
            }
        }
    except Exception as e:
        status_report["services"]["mongodb"] = {
            "status": "error",
            "message": str(e)
        }
    
    # Redis Status
    try:
        redis_client = await get_redis_client()
        if redis_client:
            info = await redis_client.info("server")
            status_report["services"]["redis"] = {
                "status": "operational",
                "version": info.get("redis_version"),
                "uptime": info.get("uptime_in_seconds")
            }
        else:
            status_report["services"]["redis"] = {
                "status": "not_configured"
            }
    except Exception as e:
        status_report["services"]["redis"] = {
            "status": "error",
            "message": str(e)
        }
    
    # Stripe Status
    try:
        import stripe
        stripe.api_key = settings.get_stripe_key()
        balance = stripe.Balance.retrieve()
        status_report["services"]["stripe"] = {
            "status": "operational",
            "mode": "test" if "test" in settings.stripe_publishable_key else "live",
            "currency": balance.get("available", [{}])[0].get("currency", "usd") if balance.get("available") else "usd"
        }
    except Exception as e:
        status_report["services"]["stripe"] = {
            "status": "error",
            "message": str(e)
        }
    
    # Email Service Status (SendGrid)
    if settings.sendgrid_api_key:
        try:
            # Basic check - would need actual SendGrid API call in production
            status_report["services"]["email"] = {
                "status": "configured",
                "provider": "SendGrid"
            }
        except Exception as e:
            status_report["services"]["email"] = {
                "status": "error",
                "message": str(e)
            }
    else:
        status_report["services"]["email"] = {
            "status": "not_configured"
        }
    
    # Storage Status (AWS S3)
    if settings.aws_access_key_id:
        try:
            status_report["services"]["storage"] = {
                "status": "configured",
                "provider": "AWS S3",
                "bucket": settings.aws_s3_bucket_name,
                "region": settings.aws_s3_region
            }
        except Exception as e:
            status_report["services"]["storage"] = {
                "status": "error",
                "message": str(e)
            }
    else:
        status_report["services"]["storage"] = {
            "status": "not_configured"
        }
    
    # Calculate overall health score
    operational_services = sum(
        1 for service in status_report["services"].values()
        if service.get("status") == "operational"
    )
    total_services = len(status_report["services"])
    health_score = (operational_services / total_services) * 100 if total_services > 0 else 0
    
    status_report["health_score"] = round(health_score, 2)
    status_report["overall_status"] = "healthy" if health_score >= 80 else "degraded" if health_score >= 50 else "unhealthy"
    
    return status_report


@router.post("/test-error", status_code=status.HTTP_200_OK)
async def test_error_handling(
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Test error handling and logging
    Requires admin authentication
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # This would trigger error logging
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Test error for monitoring"
    )