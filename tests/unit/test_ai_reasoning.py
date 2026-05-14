import pytest
from unittest.mock import MagicMock, AsyncMock
import json
from src.asta_brain.ai.reasoning import AIReasoningLayer
from src.asta_brain.infrastructure.schemas.trade import TradeSide
from src.asta_brain.infrastructure.schemas.market import OHLCV
from datetime import datetime

@pytest.mark.asyncio
async def test_ai_reasoning_success(monkeypatch):
    # Mock GEMINI_API_KEY
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    
    # Mock google.generativeai
    mock_genai = MagicMock()
    mock_model = MagicMock()
    mock_response = MagicMock()
    
    mock_response.text = '{"confidence_multiplier": 0.85, "reasoning": "Strong trend confirmed by RSI and EMA crossover."}'
    mock_model.generate_content_async = AsyncMock(return_value=mock_response)
    
    monkeypatch.setattr("google.generativeai.configure", lambda api_key: None)
    monkeypatch.setattr("google.generativeai.GenerativeModel", lambda model_name: mock_model)
    
    ai_layer = AIReasoningLayer()
    
    # Mock data
    ohlcv_data = [
        OHLCV(symbol="EURUSD", timeframe="M1", time=datetime.utcnow(), open=1.1, high=1.11, low=1.09, close=1.105, volume=100)
        for _ in range(10)
    ]
    
    result = await ai_layer.analyze_signal(
        symbol="EURUSD",
        side=TradeSide.BUY,
        market_context={"market_regime": "trending"},
        recent_ohlcv=ohlcv_data
    )
    
    assert result["confidence_multiplier"] == 0.85
    assert result["reasoning"] == "Strong trend confirmed by RSI and EMA crossover."

@pytest.mark.asyncio
async def test_ai_reasoning_no_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    
    ai_layer = AIReasoningLayer()
    
    result = await ai_layer.analyze_signal(
        symbol="EURUSD",
        side=TradeSide.BUY,
        market_context={},
        recent_ohlcv=[]
    )
    
    assert result["confidence_multiplier"] == 1.0
    assert "disabled" in result["reasoning"]

@pytest.mark.asyncio
async def test_ai_reasoning_error_fallback(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    
    mock_model = MagicMock()
    mock_model.generate_content_async = AsyncMock(side_effect=Exception("API Error"))
    
    monkeypatch.setattr("google.generativeai.configure", lambda api_key: None)
    monkeypatch.setattr("google.generativeai.GenerativeModel", lambda model_name: mock_model)
    
    ai_layer = AIReasoningLayer()
    
    result = await ai_layer.analyze_signal(
        symbol="EURUSD",
        side=TradeSide.BUY,
        market_context={},
        recent_ohlcv=[]
    )
    
    assert result["confidence_multiplier"] == 0.5
    assert "Error" in result["reasoning"]
