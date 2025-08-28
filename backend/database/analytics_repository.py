from motor.motor_asyncio import AsyncIOMotorDatabase
from models.analytics import (
    SalesAnalyticsReport, SalesMetric, ProductPerformance, CategoryPerformance,
    CustomerAnalyticsReport, CustomerMetric, CustomerBehavior, CustomerSegment,
    TrafficAnalyticsReport, TrafficMetric, PageMetric,
    FinancialAnalyticsReport, FinancialMetric,
    InventoryAnalyticsReport, InventoryAnalytics, InventoryMetric,
    CustomReport, CustomReportCreate, CustomReportUpdate,
    SystemPerformance, PerformanceAlert, TimePeriod
)
from models.product import ProductStatus
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging
import asyncio

logger = logging.getLogger(__name__)

class AnalyticsRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        
        # Collections
        self.orders_collection = database.payment_transactions
        self.products_collection = database.products
        self.users_collection = database.users
        self.activities_collection = database.user_activities
        self.custom_reports_collection = database.custom_reports
        self.performance_metrics_collection = database.performance_metrics
        self.performance_alerts_collection = database.performance_alerts
        
    async def create_indexes(self):
        """Create database indexes for analytics queries"""
        try:
            # Performance metrics indexes
            await self.performance_metrics_collection.create_index("timestamp")
            await self.performance_alerts_collection.create_index("alert_type")
            await self.performance_alerts_collection.create_index("triggered_at")
            await self.performance_alerts_collection.create_index("is_active")
            
            # Custom reports indexes
            await self.custom_reports_collection.create_index("report_type")
            await self.custom_reports_collection.create_index("created_by")
            await self.custom_reports_collection.create_index("is_active")
            await self.custom_reports_collection.create_index("next_run")
            
            logger.info("Analytics collection indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create analytics indexes: {e}")
    
    # Sales Analytics
    async def get_sales_analytics(
        self, 
        start_date: datetime, 
        end_date: datetime,
        time_granularity: TimePeriod = TimePeriod.DAY
    ) -> SalesAnalyticsReport:
        """Generate sales analytics report"""
        try:
            report = SalesAnalyticsReport(
                period_start=start_date,
                period_end=end_date,
                time_granularity=time_granularity
            )
            
            # Base query for paid orders
            base_query = {
                "payment_status": "paid",
                "created_at": {"$gte": start_date, "$lte": end_date}
            }
            
            # Get total metrics
            total_pipeline = [
                {"$match": base_query},
                {"$group": {
                    "_id": None,
                    "total_revenue": {"$sum": "$amount"},
                    "total_orders": {"$sum": 1},
                    "total_units": {"$sum": "$quantity"},
                    "avg_order_value": {"$avg": "$amount"}
                }}
            ]
            
            total_result = await self.orders_collection.aggregate(total_pipeline).to_list(1)
            if total_result:
                result = total_result[0]
                report.total_revenue = result.get("total_revenue", 0.0)
                report.total_orders = result.get("total_orders", 0)
                report.total_units = result.get("total_units", 0)
                report.avg_order_value = result.get("avg_order_value", 0.0)
            
            # Get metrics over time
            time_format = self._get_time_format(time_granularity)
            time_pipeline = [
                {"$match": base_query},
                {"$group": {
                    "_id": {"$dateToString": {"format": time_format, "date": "$created_at"}},
                    "revenue": {"$sum": "$amount"},
                    "orders": {"$sum": 1},
                    "units_sold": {"$sum": "$quantity"},
                    "avg_order_value": {"$avg": "$amount"}
                }},
                {"$sort": {"_id": 1}}
            ]
            
            time_results = await self.orders_collection.aggregate(time_pipeline).to_list(None)
            
            for result in time_results:
                metric = SalesMetric(
                    period=result["_id"],
                    revenue=result.get("revenue", 0.0),
                    orders=result.get("orders", 0),
                    units_sold=result.get("units_sold", 0),
                    avg_order_value=result.get("avg_order_value", 0.0)
                )
                report.metrics_over_time.append(metric)
            
            # Get top products
            products_pipeline = [
                {"$match": base_query},
                {"$group": {
                    "_id": "$package_id",
                    "revenue": {"$sum": "$amount"},
                    "orders": {"$sum": 1},
                    "units_sold": {"$sum": "$quantity"},
                    "avg_price": {"$avg": "$amount"}
                }},
                {"$sort": {"revenue": -1}},
                {"$limit": 10}
            ]
            
            product_results = await self.orders_collection.aggregate(products_pipeline).to_list(None)
            
            # Enrich with product details
            for result in product_results:
                product_id = result["_id"]
                product = await self.products_collection.find_one({"id": product_id})
                
                performance = ProductPerformance(
                    product_id=product_id,
                    product_name=product.get("name", "Unknown") if product else "Unknown",
                    sku=product.get("sku", "") if product else "",
                    category=product.get("category", "") if product else "",
                    revenue=result.get("revenue", 0.0),
                    units_sold=result.get("units_sold", 0),
                    orders=result.get("orders", 0),
                    avg_price=result.get("avg_price", 0.0)
                )
                report.top_products.append(performance)
            
            # Get category performance
            category_pipeline = [
                {"$match": base_query},
                {"$lookup": {
                    "from": "products",
                    "localField": "package_id",
                    "foreignField": "id",
                    "as": "product"
                }},
                {"$unwind": {"path": "$product", "preserveNullAndEmptyArrays": True}},
                {"$group": {
                    "_id": "$product.category",
                    "revenue": {"$sum": "$amount"},
                    "orders": {"$sum": 1},
                    "units_sold": {"$sum": "$quantity"},
                    "avg_order_value": {"$avg": "$amount"}
                }},
                {"$sort": {"revenue": -1}}
            ]
            
            category_results = await self.orders_collection.aggregate(category_pipeline).to_list(None)
            
            for result in category_results:
                category_name = result["_id"] or "Unknown"
                
                # Get product count for category
                product_count = await self.products_collection.count_documents({
                    "category": category_name,
                    "status": ProductStatus.ACTIVE
                })
                
                performance = CategoryPerformance(
                    category=category_name,
                    revenue=result.get("revenue", 0.0),
                    units_sold=result.get("units_sold", 0),
                    orders=result.get("orders", 0),
                    product_count=product_count,
                    avg_order_value=result.get("avg_order_value", 0.0),
                    market_share=(result.get("revenue", 0.0) / report.total_revenue * 100) if report.total_revenue > 0 else 0.0
                )
                report.category_performance.append(performance)
            
            # Calculate growth rate (compare with previous period)
            prev_start = start_date - (end_date - start_date)
            prev_query = {
                "payment_status": "paid",
                "created_at": {"$gte": prev_start, "$lte": start_date}
            }
            
            prev_result = await self.orders_collection.aggregate([
                {"$match": prev_query},
                {"$group": {"_id": None, "prev_revenue": {"$sum": "$amount"}}}
            ]).to_list(1)
            
            if prev_result and prev_result[0].get("prev_revenue", 0) > 0:
                prev_revenue = prev_result[0]["prev_revenue"]
                report.growth_rate = ((report.total_revenue - prev_revenue) / prev_revenue) * 100
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate sales analytics: {e}")
            return SalesAnalyticsReport(
                period_start=start_date,
                period_end=end_date,
                time_granularity=time_granularity
            )
    
    # Customer Analytics
    async def get_customer_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        time_granularity: TimePeriod = TimePeriod.DAY
    ) -> CustomerAnalyticsReport:
        """Generate customer analytics report"""
        try:
            report = CustomerAnalyticsReport(
                period_start=start_date,
                period_end=end_date,
                time_granularity=time_granularity
            )
            
            # Get total customer counts
            report.total_customers = await self.users_collection.count_documents({})
            
            # New customers in period
            report.new_customers = await self.users_collection.count_documents({
                "created_at": {"$gte": start_date, "$lte": end_date}
            })
            
            # Customers with orders in period
            customer_orders_pipeline = [
                {"$match": {
                    "payment_status": "paid",
                    "created_at": {"$gte": start_date, "$lte": end_date}
                }},
                {"$group": {"_id": "$customer_info.email"}},
                {"$count": "returning_customers"}
            ]
            
            returning_result = await self.orders_collection.aggregate(customer_orders_pipeline).to_list(1)
            if returning_result:
                report.returning_customers = returning_result[0]["returning_customers"]
            
            # Customer metrics over time
            time_format = self._get_time_format(time_granularity)
            
            # New customers over time
            new_customers_pipeline = [
                {"$match": {"created_at": {"$gte": start_date, "$lte": end_date}}},
                {"$group": {
                    "_id": {"$dateToString": {"format": time_format, "date": "$created_at"}},
                    "new_customers": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
            
            new_customers_results = await self.users_collection.aggregate(new_customers_pipeline).to_list(None)
            
            # Convert to time metrics
            new_customers_dict = {result["_id"]: result["new_customers"] for result in new_customers_results}
            
            # Active customers over time (customers with activity)
            active_customers_pipeline = [
                {"$match": {
                    "created_at": {"$gte": start_date, "$lte": end_date}
                }},
                {"$group": {
                    "_id": {
                        "period": {"$dateToString": {"format": time_format, "date": "$created_at"}},
                        "user_id": "$user_id"
                    }
                }},
                {"$group": {
                    "_id": "$_id.period",
                    "active_customers": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
            
            active_customers_results = await self.activities_collection.aggregate(active_customers_pipeline).to_list(None)
            active_customers_dict = {result["_id"]: result["active_customers"] for result in active_customers_results}
            
            # Combine metrics
            all_periods = set(new_customers_dict.keys()) | set(active_customers_dict.keys())
            
            for period in sorted(all_periods):
                metric = CustomerMetric(
                    period=period,
                    new_customers=new_customers_dict.get(period, 0),
                    total_active_customers=active_customers_dict.get(period, 0)
                )
                report.metrics_over_time.append(metric)
            
            # Top customers
            top_customers_pipeline = [
                {"$match": {"payment_status": "paid"}},
                {"$group": {
                    "_id": "$customer_info.email",
                    "total_orders": {"$sum": 1},
                    "total_spent": {"$sum": "$amount"},
                    "avg_order_value": {"$avg": "$amount"},
                    "last_order_date": {"$max": "$created_at"}
                }},
                {"$sort": {"total_spent": -1}},
                {"$limit": 20}
            ]
            
            top_customers_results = await self.orders_collection.aggregate(top_customers_pipeline).to_list(None)
            
            for result in top_customers_results:
                email = result["_id"]
                user = await self.users_collection.find_one({"email": email})
                
                last_order_date = result.get("last_order_date")
                days_since_last_order = None
                if last_order_date:
                    days_since_last_order = (datetime.utcnow() - last_order_date).days
                
                # Determine customer segment
                segment = self._determine_customer_segment(
                    result.get("total_orders", 0),
                    result.get("total_spent", 0.0),
                    days_since_last_order
                )
                
                behavior = CustomerBehavior(
                    customer_id=user.get("id", "") if user else "",
                    email=email,
                    first_name=user.get("first_name") if user else None,
                    last_name=user.get("last_name") if user else None,
                    segment=segment,
                    total_orders=result.get("total_orders", 0),
                    total_spent=result.get("total_spent", 0.0),
                    avg_order_value=result.get("avg_order_value", 0.0),
                    last_order_date=last_order_date,
                    days_since_last_order=days_since_last_order,
                    lifetime_value=result.get("total_spent", 0.0)
                )
                report.top_customers.append(behavior)
            
            # Customer segments distribution
            segments_count = {}
            for customer in report.top_customers:
                segment = customer.segment.value
                segments_count[segment] = segments_count.get(segment, 0) + 1
            
            report.customer_segments = segments_count
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate customer analytics: {e}")
            return CustomerAnalyticsReport(
                period_start=start_date,
                period_end=end_date,
                time_granularity=time_granularity
            )
    
    # Inventory Analytics
    async def get_inventory_analytics(self) -> InventoryAnalyticsReport:
        """Generate inventory analytics report"""
        try:
            now = datetime.utcnow()
            report = InventoryAnalyticsReport(
                period_start=now - timedelta(days=30),
                period_end=now
            )
            
            # Get all active products
            products = await self.products_collection.find({
                "status": ProductStatus.ACTIVE
            }).to_list(None)
            
            report.total_products = len(products)
            total_stock_value = 0.0
            low_stock_count = 0
            out_of_stock_count = 0
            
            for product in products:
                inventory_count = product.get("inventory_count", 0)
                base_price = product.get("base_price", 0.0)
                low_stock_threshold = product.get("low_stock_threshold", 5)
                
                stock_value = inventory_count * base_price
                total_stock_value += stock_value
                
                # Get sales data for last 30 days
                sales_30d = await self.orders_collection.count_documents({
                    "package_id": product["id"],
                    "payment_status": "paid",
                    "created_at": {"$gte": now - timedelta(days=30)}
                })
                
                # Calculate turnover rate
                turnover_rate = 0.0
                if inventory_count > 0:
                    turnover_rate = sales_30d / inventory_count * 30  # Monthly turnover
                
                # Calculate days of supply
                days_of_supply = 0
                if sales_30d > 0:
                    daily_sales = sales_30d / 30
                    days_of_supply = int(inventory_count / daily_sales) if daily_sales > 0 else 999
                
                # Determine stock status
                stock_status = "normal"
                if inventory_count == 0:
                    stock_status = "out"
                    out_of_stock_count += 1
                elif inventory_count <= low_stock_threshold:
                    stock_status = "low"
                    low_stock_count += 1
                elif inventory_count > low_stock_threshold * 3:
                    stock_status = "overstock"
                
                analytics = InventoryAnalytics(
                    product_id=product["id"],
                    product_name=product.get("name", ""),
                    sku=product.get("sku", ""),
                    current_stock=inventory_count,
                    stock_value=stock_value,
                    units_sold_30d=sales_30d,
                    stock_turnover_rate=turnover_rate,
                    days_of_supply=days_of_supply,
                    reorder_point=low_stock_threshold,
                    stock_status=stock_status,
                    last_restocked=product.get("updated_at")
                )
                report.product_analytics.append(analytics)
            
            report.total_stock_value = total_stock_value
            report.low_stock_alerts = low_stock_count
            report.out_of_stock_alerts = out_of_stock_count
            
            # Calculate average turnover rate
            if report.product_analytics:
                avg_turnover = sum(p.stock_turnover_rate for p in report.product_analytics) / len(report.product_analytics)
                report.avg_turnover_rate = avg_turnover
            
            # Generate reorder recommendations
            for product in report.product_analytics:
                if product.stock_status in ["low", "out"] or product.days_of_supply < 7:
                    recommended_qty = max(product.units_sold_30d * 2, product.reorder_point * 2)
                    
                    recommendation = {
                        "product_id": product.product_id,
                        "product_name": product.product_name,
                        "sku": product.sku,
                        "current_stock": product.current_stock,
                        "recommended_qty": recommended_qty,
                        "urgency": "high" if product.stock_status == "out" else "medium",
                        "reason": f"Stock status: {product.stock_status}, Days of supply: {product.days_of_supply}"
                    }
                    report.reorder_recommendations.append(recommendation)
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate inventory analytics: {e}")
            return InventoryAnalyticsReport(
                period_start=datetime.utcnow() - timedelta(days=30),
                period_end=datetime.utcnow()
            )
    
    # Custom Reports Management
    async def create_custom_report(self, report: CustomReportCreate, created_by: Optional[str] = None) -> Optional[CustomReport]:
        """Create custom report"""
        try:
            report_obj = CustomReport(**report.dict(), created_by=created_by)
            
            await self.custom_reports_collection.insert_one(report_obj.dict())
            return report_obj
        except Exception as e:
            logger.error(f"Failed to create custom report: {e}")
            return None
    
    async def get_custom_reports(self, created_by: Optional[str] = None, active_only: bool = True) -> List[CustomReport]:
        """Get custom reports"""
        try:
            query = {}
            if created_by:
                query["created_by"] = created_by
            if active_only:
                query["is_active"] = True
            
            cursor = self.custom_reports_collection.find(query).sort("created_at", -1)
            report_docs = await cursor.to_list(length=None)
            
            return [CustomReport(**doc) for doc in report_docs]
        except Exception as e:
            logger.error(f"Failed to get custom reports: {e}")
            return []
    
    # Performance Monitoring
    async def log_performance_metric(self, metric: SystemPerformance) -> bool:
        """Log system performance metric"""
        try:
            await self.performance_metrics_collection.insert_one(metric.dict())
            
            # Check for alerts
            await self._check_performance_alerts(metric)
            
            return True
        except Exception as e:
            logger.error(f"Failed to log performance metric: {e}")
            return False
    
    async def get_performance_metrics(self, hours: int = 24) -> List[SystemPerformance]:
        """Get performance metrics for the last N hours"""
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            cursor = self.performance_metrics_collection.find({
                "timestamp": {"$gte": start_time}
            }).sort("timestamp", -1)
            
            metric_docs = await cursor.to_list(length=None)
            return [SystemPerformance(**doc) for doc in metric_docs]
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return []
    
    # Helper Methods
    def _get_time_format(self, granularity: TimePeriod) -> str:
        """Get MongoDB date format string for time granularity"""
        formats = {
            TimePeriod.HOUR: "%Y-%m-%d %H:00",
            TimePeriod.DAY: "%Y-%m-%d",
            TimePeriod.WEEK: "%Y-%U",  # Year-Week
            TimePeriod.MONTH: "%Y-%m",
            TimePeriod.QUARTER: "%Y-Q%q",  # Not directly supported
            TimePeriod.YEAR: "%Y"
        }
        return formats.get(granularity, "%Y-%m-%d")
    
    def _determine_customer_segment(self, total_orders: int, total_spent: float, days_since_last_order: Optional[int]) -> CustomerSegment:
        """Determine customer segment based on behavior"""
        if days_since_last_order is None:
            return CustomerSegment.NEW
        
        if days_since_last_order > 365:
            return CustomerSegment.CHURNED
        elif days_since_last_order > 90:
            return CustomerSegment.DORMANT
        elif total_spent > 1000 or total_orders > 5:
            return CustomerSegment.VIP
        elif total_orders > 1:
            return CustomerSegment.RETURNING
        else:
            return CustomerSegment.NEW
    
    async def _check_performance_alerts(self, metric: SystemPerformance):
        """Check performance metrics against alert thresholds"""
        try:
            alerts = []
            
            # CPU usage alert
            if metric.cpu_usage > 80:
                alerts.append(PerformanceAlert(
                    alert_type="cpu",
                    threshold=80.0,
                    current_value=metric.cpu_usage,
                    severity="error" if metric.cpu_usage > 90 else "warning",
                    message=f"High CPU usage: {metric.cpu_usage:.1f}%"
                ))
            
            # Memory usage alert
            if metric.memory_usage > 80:
                alerts.append(PerformanceAlert(
                    alert_type="memory",
                    threshold=80.0,
                    current_value=metric.memory_usage,
                    severity="error" if metric.memory_usage > 90 else "warning",
                    message=f"High memory usage: {metric.memory_usage:.1f}%"
                ))
            
            # Response time alert
            if metric.api_response_time > 2000:  # 2 seconds
                alerts.append(PerformanceAlert(
                    alert_type="response_time",
                    threshold=2000.0,
                    current_value=metric.api_response_time,
                    severity="error" if metric.api_response_time > 5000 else "warning",
                    message=f"Slow API response time: {metric.api_response_time:.0f}ms"
                ))
            
            # Error rate alert
            if metric.error_rate > 5:  # 5% error rate
                alerts.append(PerformanceAlert(
                    alert_type="error_rate",
                    threshold=5.0,
                    current_value=metric.error_rate,
                    severity="error" if metric.error_rate > 10 else "warning",
                    message=f"High error rate: {metric.error_rate:.1f}%"
                ))
            
            # Insert alerts
            for alert in alerts:
                await self.performance_alerts_collection.insert_one(alert.dict())
                
        except Exception as e:
            logger.error(f"Failed to check performance alerts: {e}")
    
    # Analytics Aggregation Helpers
    async def get_kpi_summary(self) -> Dict[str, Any]:
        """Get key performance indicators summary"""
        try:
            now = datetime.utcnow()
            last_30_days = now - timedelta(days=30)
            
            # Revenue metrics
            revenue_pipeline = [
                {"$match": {
                    "payment_status": "paid",
                    "created_at": {"$gte": last_30_days}
                }},
                {"$group": {
                    "_id": None,
                    "total_revenue": {"$sum": "$amount"},
                    "total_orders": {"$sum": 1},
                    "avg_order_value": {"$avg": "$amount"}
                }}
            ]
            
            revenue_result = await self.orders_collection.aggregate(revenue_pipeline).to_list(1)
            revenue_data = revenue_result[0] if revenue_result else {}
            
            # Customer metrics
            new_customers = await self.users_collection.count_documents({
                "created_at": {"$gte": last_30_days}
            })
            
            total_customers = await self.users_collection.count_documents({})
            
            # Product metrics
            total_products = await self.products_collection.count_documents({
                "status": ProductStatus.ACTIVE
            })
            
            low_stock_products = await self.products_collection.count_documents({
                "$expr": {"$lte": ["$inventory_count", "$low_stock_threshold"]},
                "inventory_count": {"$gt": 0},
                "status": ProductStatus.ACTIVE
            })
            
            return {
                "revenue_30d": revenue_data.get("total_revenue", 0.0),
                "orders_30d": revenue_data.get("total_orders", 0),
                "avg_order_value_30d": revenue_data.get("avg_order_value", 0.0),
                "new_customers_30d": new_customers,
                "total_customers": total_customers,
                "total_products": total_products,
                "low_stock_products": low_stock_products,
                "generated_at": now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate KPI summary: {e}")
            return {}