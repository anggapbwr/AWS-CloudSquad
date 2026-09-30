"""
WebSocket Gateway for Real-Time Event Streaming
"""
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog
from services.event_bus import event_bus

log = structlog.get_logger()
router = APIRouter()


async def _handle_websocket_connection(websocket: WebSocket, mission_id: UUID):
    await websocket.accept()
    log.info("WebSocket client connected", mission_id=str(mission_id))

    async def on_event(payload: dict):
        try:
            await websocket.send_json(payload)
        except Exception:
            pass

    event_bus.subscribe_mission(mission_id, on_event)

    try:
        while True:
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        log.info("WebSocket client disconnected", mission_id=str(mission_id))
    except Exception as e:
        log.warning("WebSocket connection exception", mission_id=str(mission_id), error=str(e))
    finally:
        event_bus.unsubscribe_mission(mission_id, on_event)


@router.websocket("/missions/{mission_id}")
async def mission_websocket_alt(websocket: WebSocket, mission_id: UUID):
    await _handle_websocket_connection(websocket, mission_id)


@router.websocket("/{mission_id}")
async def mission_websocket(websocket: WebSocket, mission_id: UUID):
    await _handle_websocket_connection(websocket, mission_id)
