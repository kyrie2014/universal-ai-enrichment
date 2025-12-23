"""
腾讯元宝AI客户端
支持通过浏览器Cookie方式调用腾讯元宝对话接口
"""

import requests
import json
import logging
import uuid
import time
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class TencentYuanbaoClient:
    """腾讯元宝AI客户端"""
    
    def __init__(self, cookie: str = "", csrf_token: str = "", api_url: str = "https://yuanbao.tencent.com/api/chat"):
        """
        初始化腾讯元宝客户端
        
        Args:
            cookie: 浏览器Cookie字符串
            csrf_token: CSRF Token (如果需要)
            api_url: API地址 (默认为腾讯元宝对话接口)
        """
        self.cookie = cookie
        self.csrf_token = csrf_token
        self.api_url = api_url
        self.timeout = 30
        self.session = requests.Session()
        
    def _send_request(self, prompt: str, session_id: str = None) -> Optional[Dict[str, Any]]:
        """
        发送请求到腾讯元宝API
        
        Args:
            prompt: 提示词
            session_id: 会话ID
            
        Returns:
            API响应数据
        """
        if not self.cookie:
            logger.error("腾讯元宝客户端未配置Cookie")
            return None
            
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Content-Type": "application/json",
            "Cookie": self.cookie,
            "Origin": "https://yuanbao.tencent.com",
            "Referer": "https://yuanbao.tencent.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        }
        
        # 如果有CSRF Token，添加到headers
        if self.csrf_token:
            headers["X-CSRF-Token"] = self.csrf_token
            
        # 构建payload (需要根据实际抓包调整)
        payload = {
            "query": prompt,
            "session_id": session_id if session_id else str(uuid.uuid4()).replace('-', ''),
            "stream": False,  # 非流式响应
            "model": "hunyuan",  # 混元模型
            "timestamp": int(time.time() * 1000)
        }
        
        try:
            response = self.session.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"腾讯元宝API请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"解析腾讯元宝响应失败: {e}")
            return None
            
    def chat(self, prompt: str, session_id: str = None) -> Optional[Dict[str, Any]]:
        """
        与腾讯元宝AI对话
        
        Args:
            prompt: 提示词
            session_id: 会话ID (可选)
            
        Returns:
            提取的结构化信息
        """
        if not self.cookie:
            logger.error("腾讯元宝客户端未配置Cookie")
            return None
            
        logger.info(f"腾讯元宝AI查询: {prompt[:50]}...")
        
        # 发送请求
        result = self._send_request(prompt, session_id)
        
        if not result:
            return None
            
        # 提取AI回复内容 (需要根据实际响应结构调整)
        try:
            # 尝试多种可能的响应格式
            response_text = None
            
            if isinstance(result, dict):
                # 尝试常见的响应字段
                response_text = (
                    result.get("answer") or
                    result.get("response") or
                    result.get("content") or
                    result.get("text") or
                    result.get("data", {}).get("answer") or
                    result.get("data", {}).get("content")
                )
                
            if not response_text:
                logger.warning(f"未能从响应中提取内容: {result}")
                return None
                
            logger.info(f"腾讯元宝AI响应: {response_text[:100]}...")
            
            # 解析AI响应，提取结构化信息
            extracted_data = self._parse_ai_response(response_text, prompt)
            return extracted_data
            
        except Exception as e:
            logger.error(f"处理腾讯元宝响应时发生错误: {e}")
            return None
            
    def _parse_ai_response(self, response_text: str, original_query: str) -> Dict[str, Any]:
        """
        解析AI响应，提取结构化公司信息
        
        Args:
            response_text: AI响应文本
            original_query: 原始查询
            
        Returns:
            结构化的公司信息
        """
        # 这是一个简化的解析实现
        # 实际应用中可能需要更复杂的NLP或正则匹配
        
        data = {
            "full_name": "N/A",
            "unified_social_credit_code": "N/A",
            "legal_representative": "N/A",
            "registered_address": "N/A",
            "company_type": "N/A",
            "is_listed": False,
            "reg_capital": "N/A",
            "employee_count": "N/A",
            "establishment_date": "N/A",
            "revenue": {},
            "net_profit": {},
            "ai_source": "tencent_yuanbao"
        }
        
        # 尝试从响应中提取公司全名
        if "公司全名" in response_text or "企业名称" in response_text:
            import re
            # 简单的正则匹配
            name_match = re.search(r'(?:公司全名|企业名称)[:：]\s*([^\n，,。.]+)', response_text)
            if name_match:
                data["full_name"] = name_match.group(1).strip()
        
        # 如果AI没有返回全名，使用原始查询
        if data["full_name"] == "N/A":
            data["full_name"] = original_query
            
        # TODO: 添加更多字段的提取逻辑
        # 可以使用正则表达式、NLP工具或结构化提示词来提取
        
        return data
        
    def test_connection(self) -> bool:
        """
        测试连接是否正常
        
        Returns:
            True if connection is successful, False otherwise
        """
        if not self.cookie:
            logger.error("未配置Cookie")
            return False
            
        try:
            # 发送一个简单的测试请求
            result = self.chat("你好")
            return result is not None
        except Exception as e:
            logger.error(f"测试连接失败: {e}")
            return False


def test_client():
    """测试腾讯元宝客户端"""
    # 这里需要替换为实际的Cookie
    cookie = "your_cookie_here"
    
    client = TencentYuanbaoClient(cookie=cookie)
    
    # Test connection
    if client.test_connection():
        print("[OK] Connection successful")
        
        # Test query
        result = client.chat("查询华为技术有限公司的详细信息")
        if result:
            print(f"[OK] Query successful: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print("[Error] Query failed")
    else:
        print("[Error] Connection failed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_client()

