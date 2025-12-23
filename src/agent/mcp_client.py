"""
MCP (Model Context Protocol) 客户端
支持连接到各种MCP服务器，提供实时数据查询能力
"""

import json
import subprocess
import threading
import queue
from typing import Dict, List, Optional, Any
import time


class MCPServer:
    """MCP服务器实例"""
    
    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config
        self.process = None
        self.running = False
        self.tools = []
        
    def start(self):
        """启动MCP服务器"""
        if not self.config.get("enabled", False):
            return False
        
        try:
            command = self.config.get("command", "")
            args = self.config.get("args", [])
            env = self.config.get("env", {})
            
            if not command:
                print(f"[MCP] {self.name}: 缺少启动命令")
                return False
            
            # 构建完整命令
            full_command = [command] + args
            
            # 启动子进程
            self.process = subprocess.Popen(
                full_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**subprocess.os.environ, **env},
                text=True,
                bufsize=1
            )
            
            self.running = True
            print(f"[MCP] {self.name}: 服务器已启动")
            
            # 初始化握手
            self._initialize()
            
            return True
            
        except Exception as e:
            print(f"[MCP] {self.name}: 启动失败 - {e}")
            return False
    
    def stop(self):
        """停止MCP服务器"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                print(f"[MCP] {self.name}: 服务器已停止")
            except:
                self.process.kill()
            finally:
                self.running = False
                self.process = None
    
    def _initialize(self):
        """初始化MCP连接"""
        try:
            # 发送初始化请求
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "universal-ai-agent",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = self._send_request(init_request)
            
            if response and "result" in response:
                # 获取服务器能力
                capabilities = response["result"].get("capabilities", {})
                print(f"[MCP] {self.name}: 初始化成功")
                
                # 列出可用工具
                self._list_tools()
            
        except Exception as e:
            print(f"[MCP] {self.name}: 初始化失败 - {e}")
    
    def _list_tools(self):
        """列出可用工具"""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            response = self._send_request(request)
            
            if response and "result" in response:
                self.tools = response["result"].get("tools", [])
                print(f"[MCP] {self.name}: 发现 {len(self.tools)} 个工具")
                for tool in self.tools:
                    print(f"  - {tool.get('name')}: {tool.get('description', 'N/A')}")
        
        except Exception as e:
            print(f"[MCP] {self.name}: 获取工具列表失败 - {e}")
    
    def _send_request(self, request: dict, timeout: int = 10) -> Optional[dict]:
        """发送请求到MCP服务器"""
        if not self.process or not self.running:
            return None
        
        try:
            # 发送请求
            request_str = json.dumps(request) + "\n"
            self.process.stdin.write(request_str)
            self.process.stdin.flush()
            
            # 读取响应（带超时）
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.process.stdout.readable():
                    line = self.process.stdout.readline()
                    if line:
                        return json.loads(line.strip())
                time.sleep(0.1)
            
            return None
            
        except Exception as e:
            print(f"[MCP] {self.name}: 请求失败 - {e}")
            return None
    
    def call_tool(self, tool_name: str, arguments: dict) -> Optional[Any]:
        """调用MCP工具"""
        if not self.running:
            return None
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": int(time.time() * 1000),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            response = self._send_request(request, timeout=30)
            
            if response and "result" in response:
                return response["result"]
            
            return None
            
        except Exception as e:
            print(f"[MCP] {self.name}: 调用工具 {tool_name} 失败 - {e}")
            return None


class MCPClient:
    """MCP客户端管理器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.servers: Dict[str, MCPServer] = {}
        self.enabled = config.get("enable_mcp", False)
        
        if self.enabled:
            self._initialize_servers()
    
    def _initialize_servers(self):
        """初始化MCP服务器"""
        mcp_servers = self.config.get("mcp_servers", [])
        
        for server_config in mcp_servers:
            if server_config.get("enabled", False):
                name = server_config.get("name")
                server = MCPServer(name, server_config)
                
                if server.start():
                    self.servers[name] = server
                    print(f"[MCP] 服务器 {name} 已就绪")
    
    def is_enabled(self) -> bool:
        """检查MCP是否启用"""
        return self.enabled and len(self.servers) > 0
    
    def search_web(self, query: str) -> Optional[str]:
        """使用MCP进行网页搜索"""
        if not self.is_enabled():
            return None
        
        # 查找web_search服务器
        web_search = self.servers.get("web_search")
        if not web_search:
            return None
        
        try:
            # 调用搜索工具
            result = web_search.call_tool("brave_web_search", {
                "query": query,
                "count": 5
            })
            
            if result and "content" in result:
                # 提取搜索结果
                content = result["content"]
                if isinstance(content, list):
                    return "\n\n".join([item.get("text", "") for item in content])
                elif isinstance(content, str):
                    return content
            
            return None
            
        except Exception as e:
            print(f"[MCP] 网页搜索失败: {e}")
            return None
    
    def query_database(self, sql: str) -> Optional[Any]:
        """使用MCP查询数据库"""
        if not self.is_enabled():
            return None
        
        # 查找database服务器
        database = self.servers.get("database")
        if not database:
            return None
        
        try:
            result = database.call_tool("execute_query", {
                "sql": sql
            })
            
            return result
            
        except Exception as e:
            print(f"[MCP] 数据库查询失败: {e}")
            return None
    
    def enhance_prompt(self, prompt: str, context_type: str = "auto") -> str:
        """使用MCP增强提示词"""
        if not self.is_enabled():
            return prompt
        
        try:
            # 根据提示词自动搜索相关信息
            if "公司" in prompt or "企业" in prompt:
                # 提取公司名称
                import re
                company_match = re.search(r'公司名称[：:]\s*([^\n]+)', prompt)
                if company_match:
                    company_name = company_match.group(1).strip()
                    
                    # 搜索公司信息
                    search_result = self.search_web(f"{company_name} 公司信息 官网")
                    
                    if search_result:
                        enhanced_prompt = f"{prompt}\n\n【实时搜索结果】\n{search_result[:1000]}\n\n请结合以上搜索结果回答。"
                        return enhanced_prompt
            
            return prompt
            
        except Exception as e:
            print(f"[MCP] 提示词增强失败: {e}")
            return prompt
    
    def get_available_tools(self) -> List[dict]:
        """获取所有可用工具"""
        tools = []
        
        for server_name, server in self.servers.items():
            for tool in server.tools:
                tools.append({
                    "server": server_name,
                    "name": tool.get("name"),
                    "description": tool.get("description", ""),
                    "parameters": tool.get("inputSchema", {})
                })
        
        return tools
    
    def shutdown(self):
        """关闭所有MCP服务器"""
        for server in self.servers.values():
            server.stop()
        
        self.servers.clear()
        print("[MCP] 所有服务器已关闭")
    
    def __del__(self):
        """析构函数，确保清理资源"""
        self.shutdown()


class SimpleMCPClient:
    """简化版MCP客户端（不依赖外部MCP服务器）"""
    
    def __init__(self, config: dict):
        self.config = config
        self.enabled = config.get("enable_mcp", False)
        print(f"[SimpleMCP] 初始化，启用状态: {self.enabled}")
    
    def is_enabled(self) -> bool:
        """检查MCP是否启用"""
        return self.enabled
    
    def search_web(self, query: str) -> Optional[str]:
        """简化的网页搜索（使用requests实现）"""
        if not self.is_enabled():
            return None
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # 使用搜索引擎API或直接爬取
            # 这里提供一个简单的实现示例
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # 可以使用免费的搜索API，或者直接爬取
            # 这里仅作为示例，实际使用需要配置API
            print(f"[SimpleMCP] 搜索: {query}")
            
            # TODO: 实现实际的搜索功能
            # 可以使用：
            # 1. SerpAPI (需要API Key)
            # 2. Google Custom Search API (需要API Key)
            # 3. DuckDuckGo API (免费)
            # 4. 直接爬取搜索结果页面
            
            return None
            
        except Exception as e:
            print(f"[SimpleMCP] 搜索失败: {e}")
            return None
    
    def enhance_prompt(self, prompt: str, context: dict = None) -> str:
        """增强提示词（添加搜索建议）"""
        if not self.is_enabled():
            return prompt
        
        # 在提示词中添加MCP搜索提示
        enhanced = f"""{prompt}

【提示】如果需要最新信息，请：
1. 使用AI的联网搜索功能
2. 优先查询官方网站
3. 验证信息的时效性
"""
        
        return enhanced
    
    def shutdown(self):
        """关闭（无需操作）"""
        pass


# 根据配置选择使用哪个MCP客户端
def create_mcp_client(config: dict) -> Any:
    """创建MCP客户端"""
    
    # 检查是否安装了MCP相关依赖
    try:
        # 尝试使用完整版MCP客户端
        client = MCPClient(config)
        if client.is_enabled():
            return client
    except Exception as e:
        print(f"[MCP] 完整版MCP客户端初始化失败: {e}")
    
    # 使用简化版
    return SimpleMCPClient(config)


if __name__ == "__main__":
    # 测试MCP客户端
    test_config = {
        "enable_mcp": True,
        "mcp_servers": []
    }
    
    client = create_mcp_client(test_config)
    print(f"MCP客户端已创建，启用状态: {client.is_enabled()}")
    
    # 测试提示词增强
    original_prompt = "请查询华为公司的信息"
    enhanced_prompt = client.enhance_prompt(original_prompt)
    print(f"\n原始提示词:\n{original_prompt}")
    print(f"\n增强后:\n{enhanced_prompt}")

