"""
WebSocket support for real-time updates
"""

import json
import asyncio
import logging
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_subscriptions: Dict[WebSocket, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, subscriptions: List[str] = None):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_subscriptions[websocket] = set(subscriptions or ["all"])
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_subscriptions:
            del self.connection_subscriptions[websocket]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str, subscription_type: str = "all"):
        """Broadcast a message to all connected clients with matching subscription."""
        disconnected = []
        for websocket in self.active_connections:
            try:
                subscriptions = self.connection_subscriptions.get(websocket, {"all"})
                if subscription_type in subscriptions or "all" in subscriptions:
                    await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def send_data_update(self, data_type: str, data: Dict):
        """Send a data update to subscribed clients."""
        message = {
            "type": "data_update",
            "data_type": data_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(json.dumps(message), data_type)
    
    async def send_system_notification(self, message: str, level: str = "info"):
        """Send a system notification to all clients."""
        notification = {
            "type": "notification",
            "level": level,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(json.dumps(notification), "notifications")

# Global connection manager
manager = ConnectionManager()

class RealTimeUpdater:
    """Handles real-time data updates."""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.last_update_time = time.time()
        self.update_interval = 30  # seconds
    
    async def start_periodic_updates(self):
        """Start periodic data updates."""
        while True:
            try:
                await asyncio.sleep(self.update_interval)
                await self.update_dashboard_data()
                await self.update_analytics_data()
            except Exception as e:
                logger.error(f"Error in periodic updates: {e}")
    
    async def update_dashboard_data(self):
        """Update dashboard data and broadcast to clients."""
        try:
            dashboard_data = self.db.get_dashboard_data()
            await manager.send_data_update("dashboard", dashboard_data)
            logger.debug("Dashboard data updated and broadcasted")
        except Exception as e:
            logger.error(f"Error updating dashboard data: {e}")
    
    async def update_analytics_data(self):
        """Update analytics data and broadcast to clients."""
        try:
            analytics_data = self.db.get_analytics()
            await manager.send_data_update("analytics", analytics_data)
            logger.debug("Analytics data updated and broadcasted")
        except Exception as e:
            logger.error(f"Error updating analytics data: {e}")
    
    async def notify_new_transaction(self, transaction_data: Dict):
        """Notify clients about a new transaction."""
        try:
            await manager.send_data_update("new_transaction", transaction_data)
            logger.info("New transaction notification sent")
        except Exception as e:
            logger.error(f"Error notifying new transaction: {e}")
    
    async def notify_etl_completion(self, etl_stats: Dict):
        """Notify clients about ETL completion."""
        try:
            await manager.send_system_notification(
                f"ETL process completed. Processed {etl_stats.get('processed', 0)} records.",
                "success"
            )
            await manager.send_data_update("etl_completion", etl_stats)
        except Exception as e:
            logger.error(f"Error notifying ETL completion: {e}")

# Global real-time updater (will be initialized in main app)
realtime_updater = None

def initialize_realtime_updater(db_manager):
    """Initialize the real-time updater with database manager."""
    global realtime_updater
    realtime_updater = RealTimeUpdater(db_manager)
    return realtime_updater
