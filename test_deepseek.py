#!/usr/bin/env python3
"""Test DeepSeek API connection"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set API key
os.environ["DEEPSEEK_API_KEY"] = "sk-915c1aabb54d4a67941bcbb2bc9af8d0"
os.environ["DEEPSEEK_API_BASE"] = "https://api.deepseek.com/v1"
os.environ["DEEPSEEK_MODEL"] = "deepseek-chat"

from src.llm_client import reset_client, get_client

# Configure LLM
reset_client()
llm = get_client(mode="llm", config={
    "api_key": "sk-915c1aabb54d4a67941bcbb2bc9af8d0",
    "api_base": "https://api.deepseek.com/v1",
    "model": "deepseek-chat"
})

# Test with a simple prompt
print("Testing DeepSeek API...")
response = llm.generate(
    prompt="用一句话概括秦始皇统一六国的意义。",
    system_prompt="你是历史学者。回答简洁准确，不超过50字。",
    temperature=0.3
)
print(f"Response: {response}")
print("✅ DeepSeek API works!" if response else "❌ Failed")
