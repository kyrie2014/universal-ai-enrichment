#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
千问对话API集成模块
通过模拟请求调用千问API获取公司信息
"""

import requests
import json
import time
import uuid
from typing import Optional, Dict, Any


class QianwenChat:
    """千问对话API客户端"""
    
    def __init__(self, cookie: str = "", xsrf_token: str = ""):
        """
        初始化千问客户端
        
        Args:
            cookie: 从浏览器复制的Cookie
            xsrf_token: XSRF Token
        """
        self.api_url = "https://api.qianwen.com/dialog/conversation"
        self.cookie = cookie
        self.xsrf_token = xsrf_token
        self.session_id = None
        self.device_id = str(uuid.uuid4())
        
    def _generate_headers(self) -> Dict[str, str]:
        """生成请求头"""
        return {
            "accept": "text/event-stream",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "content-type": "application/json",
            "cookie": self.cookie,
            "origin": "https://www.qianwen.com",
            "referer": "https://www.qianwen.com/",
            "sec-ch-ua": '"Microsoft Edge";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0",
            "x-deviceid": self.device_id,
            "x-platform": "pc_tongyi",
            "x-xsrf-token": self.xsrf_token
        }
    
    def _create_new_session(self) -> str:
        """创建新会话ID"""
        return str(uuid.uuid4()).replace("-", "")
    
    def query_company_info(self, company_name: str, prompt_template: str = None) -> Optional[str]:
        """
        查询公司信息
        
        Args:
            company_name: 公司名称
            prompt_template: 提示词模板，默认为None使用标准模板
            
        Returns:
            AI返回的文本内容
        """
        if not self.cookie or not self.xsrf_token:
            print("[错误] 未配置千问Cookie和XSRF Token")
            return None
        
        # 创建新会话
        if not self.session_id:
            self.session_id = self._create_new_session()
        
        # 构造提示词
        if prompt_template is None:
            prompt = f"请提供{company_name}的以下工商信息（以JSON格式返回）：\n1. 公司全称\n2. 统一社会信用代码\n3. 法定代表人\n4. 注册地址\n5. 公司类型\n6. 是否上市\n7. 注册资本（单位：亿元）\n8. 员工人数\n9. 成立时间\n\n请直接返回JSON，不要有其他说明文字。"
        else:
            prompt = prompt_template.format(company_name=company_name)
        
        # 构造请求体
        payload = {
            "sessionId": self.session_id,
            "sessionType": "text_chat",
            "parentMsgId": str(uuid.uuid4()).replace("-", ""),
            "model": "",
            "mode": "chat",
            "userAction": "new_top",
            "actionSource": "",
            "contents": [{
                "content": prompt,
                "contentType": "text",
                "role": "user"
            }],
            "action": "next",
            "requestId": str(uuid.uuid4()).replace("-", ""),
            "params": {
                "specifiedModel": "tongyi-qwen3-max-model",
                "lastUseModelList": ["tongyi-qwen3-max-model"],
                "recordModelName": "tongyi-qwen3-max-model",
                "bizSceneInfo": {}
            }
        }
        
        try:
            headers = self._generate_headers()
            
            # 发送请求
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30,
                stream=True  # SSE响应需要流式读取
            )
            
            if response.status_code != 200:
                print(f"[错误] 千问API返回状态码: {response.status_code}")
                return None
            
            # 解析SSE响应
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    # SSE格式: data: {...}
                    if line_text.startswith('data:'):
                        try:
                            data_json = json.loads(line_text[5:].strip())
                            
                            # 提取消息内容
                            if 'contents' in data_json and len(data_json['contents']) > 0:
                                content = data_json['contents'][0].get('content', '')
                                if content:
                                    full_response += content
                            
                            # 检查是否完成
                            if data_json.get('msgStatus') == 'finished':
                                break
                                
                        except json.JSONDecodeError:
                            continue
            
            return full_response.strip() if full_response else None
            
        except requests.exceptions.Timeout:
            print(f"[error] 千问API请求超时")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[error] 千问API请求失败: {e}")
            return None
        except Exception as e:
            print(f"[error] 处理千问响应时出错: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def parse_company_info(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        解析AI返回的公司信息
        
        Args:
            response_text: AI返回的文本
            
        Returns:
            解析后的字典
        """
        if not response_text:
            return None
        
        try:
            # 尝试直接解析JSON
            # 清理可能的markdown代码块标记
            text = response_text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            data = json.loads(text)
            
            # 标准化字段名
            return {
                "full_name": data.get("公司全称") or data.get("full_name") or "N/A",
                "unified_social_credit_code": data.get("统一社会信用代码") or data.get("unified_social_credit_code") or "N/A",
                "legal_representative": data.get("法定代表人") or data.get("legal_representative") or "N/A",
                "registered_address": data.get("注册地址") or data.get("registered_address") or "N/A",
                "company_type": data.get("公司类型") or data.get("company_type") or "N/A",
                "is_listed": data.get("是否上市") == "是" or data.get("is_listed") == True,
                "reg_capital": data.get("注册资本") or data.get("reg_capital") or "N/A",
                "employee_count": data.get("员工人数") or data.get("employee_count") or "N/A",
                "establishment_date": data.get("成立时间") or data.get("establishment_date") or "N/A"
            }
            
        except json.JSONDecodeError:
            # 如果不是JSON，尝试从文本中提取信息
            print(f"[警告] 千问返回非JSON格式，原文: {response_text[:200]}")
            return None
        except Exception as e:
            print(f"[错误] 解析千问响应失败: {e}")
            return None


def test_qianwen():
    """测试千问API"""
    # 这里需要填入真实的Cookie和XSRF Token
    cookie = "your_cookie_here"
    xsrf_token = "your_xsrf_token_here"
    
    client = QianwenChat(cookie=cookie, xsrf_token=xsrf_token)
    
    # 测试查询
    company = "华为技术有限公司"
    print(f"查询: {company}")
    
    response = client.query_company_info(company)
    if response:
        print(f"AI返回:\n{response}")
        
        # 解析结果
        info = client.parse_company_info(response)
        if info:
            print(f"\n解析结果:")
            for key, value in info.items():
                print(f"  {key}: {value}")
    else:
        print("查询失败")


if __name__ == "__main__":
    test_qianwen()

