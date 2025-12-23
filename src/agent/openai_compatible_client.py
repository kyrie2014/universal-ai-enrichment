"""
OpenAI兼容API客户端
支持DeepSeek、千问（通义千问）等通过OpenAI兼容接口访问的AI模型
"""

import logging
import re
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class OpenAICompatibleClient:
    """OpenAI兼容API客户端"""
    
    def __init__(self, api_key: str = "", base_url: str = "", model: str = "", enable_deep_thinking: bool = True, enable_web_search: bool = False):
        """
        初始化OpenAI兼容客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
            enable_deep_thinking: 是否启用深度思考模式（针对DeepSeek v3等支持的模型）
            enable_web_search: 是否启用AI联网搜索（实时获取网络信息）
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.enable_deep_thinking = enable_deep_thinking
        self.enable_web_search = enable_web_search
        self.client = None
        
        # 打印配置状态和模型兼容性检查
        logger.info(f"OpenAI客户端配置: enable_deep_thinking={enable_deep_thinking}, enable_web_search={enable_web_search}")
        
        # 检查模型是否支持联网搜索
        if enable_web_search and model:
            supported_search_models = ["deepseek-r1", "qwen", "gpt-4o-search", "gpt-4-search"]
            model_supports_search = any(model_name in model.lower() for model_name in supported_search_models)
            
            if model_supports_search:
                print(f"[OpenAI客户端] 配置: 深度思考={'启用' if enable_deep_thinking else '禁用'}, 联网搜索=启用（模型支持）")
            else:
                print(f"[OpenAI客户端] 配置: 深度思考={'启用' if enable_deep_thinking else '禁用'}, 联网搜索=启用但模型可能不支持")
                print(f"[OpenAI客户端] 当前模型 '{model}' 可能不支持 enable_search 参数")
                print(f"[OpenAI客户端] 建议使用：DeepSeek-R1、通义千问系列等支持联网搜索的模型")
        else:
            print(f"[OpenAI客户端] 配置: 深度思考={'启用' if enable_deep_thinking else '禁用'}, 联网搜索={'启用' if enable_web_search else '禁用'}")
        
        if self.api_key and self.base_url:
            try:
                from openai import OpenAI
                # 增加超时时间，批量查询需要更长时间
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                    timeout=180.0,  # 3分钟超时，适合批量查询
                    max_retries=2   # 允许重试2次
                )
                logger.info(f"OpenAI兼容客户端初始化成功: {self.base_url}, 模型: {self.model}")
            except ImportError:
                logger.error("未安装openai库，请运行: pip install openai")
            except Exception as e:
                logger.error(f"OpenAI客户端初始化失败: {e}")
    
    def chat(self, prompt: str, stream: bool = True, parse_response: bool = True) -> Optional[Dict[str, Any]]:
        """
        发送对话请求
        
        Args:
            prompt: 提示词
            stream: 是否使用流式响应
            parse_response: 是否解析响应为字典（False则返回原始文本）
            
        Returns:
            dict或str: 默认返回解析后的字典，若parse_response=False则返回原始文本字符串
        """
        if not self.client:
            logger.error("OpenAI客户端未初始化")
            return None
        
        if not self.model:
            logger.error("未配置模型名称")
            return None
            
        try:
            logger.info(f"OpenAI API查询: {prompt[:50]}...")
            
            messages = [{"role": "user", "content": prompt}]
            
            # 构建请求参数
            completion_args = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.1,  # 降低随机性，提高准确性
            }
            
            # 深度思考模式和Web搜索控制
            # 深度思考：批量查询(parse_response=False)不启用thinking以提速，仅支持DeepSeek v3模型
            # Web搜索：仅部分模型支持（DeepSeek-R1、通义千问等）
            extra_body_params = {}
            
            enable_thinking = self.enable_deep_thinking and not parse_response and "deepseek" in self.model.lower() and "v3" in self.model.lower()
            if enable_thinking:
                extra_body_params["enable_thinking"] = True
                logger.info("已启用DeepSeek深度思考模式")
            
            # AI联网搜索（检查模型是否支持）
            # 支持列表：deepseek-r1、qwen系列、gpt-4o-search等
            supported_search_models = ["deepseek-r1", "qwen", "gpt-4o-search", "gpt-4-search"]
            model_supports_search = any(model_name in self.model.lower() for model_name in supported_search_models)
            
            if self.enable_web_search:
                if model_supports_search:
                    extra_body_params["enable_search"] = True
                    logger.info("已启用AI联网搜索模式")
                    print(f"[AI查询] 联网搜索已启用 - 将通过网络获取最新信息")
                else:
                    logger.warning(f"模型 {self.model} 可能不支持 enable_search 参数")
                    print(f"[AI查询] 当前模型 ({self.model}) 可能不支持联网搜索")
                    print(f"[AI查询] 支持联网搜索的模型：DeepSeek-R1、通义千问系列")
            else:
                print(f"[AI查询] 联网搜索未启用 - 仅使用训练数据")
            
            if extra_body_params:
                completion_args["extra_body"] = extra_body_params
            
            if stream:
                completion_args["stream"] = True
                completion_args["stream_options"] = {"include_usage": True}
                
                # 流式响应
                completion = self.client.chat.completions.create(**completion_args)
                
                reasoning_content = ""  # 思考过程
                answer_content = ""  # 回复内容
                chunk_count = 0
                
                for chunk in completion:
                    chunk_count += 1
                    if not chunk.choices:
                        # Token使用信息
                        if hasattr(chunk, 'usage') and chunk.usage:
                            logger.info(f"Token使用: {chunk.usage}")
                        continue
                    
                    delta = chunk.choices[0].delta
                    
                    # 收集思考内容（DeepSeek特有）
                    if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                        reasoning_content += delta.reasoning_content
                    
                    # 收集回复内容
                    if hasattr(delta, "content") and delta.content:
                        answer_content += delta.content
                
                response_text = answer_content
                
                # 输出思考过程摘要（如果有）
                if reasoning_content:
                    reasoning_preview = reasoning_content[:200] + "..." if len(reasoning_content) > 200 else reasoning_content
                    logger.info(f"DeepSeek思考过程长度: {len(reasoning_content)}字符")
                    logger.info(f"思考摘要: {reasoning_preview}")
                    print(f"[DeepSeek思考] 进行了 {len(reasoning_content)} 字符的深度思考")
                
                logger.info(f"OpenAI API响应长度: {len(response_text)}")
                
            else:
                # 非流式响应
                try:
                    completion = self.client.chat.completions.create(**completion_args)
                    response_text = completion.choices[0].message.content
                    
                    logger.info(f"OpenAI API响应长度: {len(response_text)}")
                except Exception as timeout_error:
                    raise
            
            if not response_text:
                logger.warning("OpenAI API返回空响应")
                return None
            
            # 根据参数决定是否解析响应
            if not parse_response:
                # 批量查询模式：直接返回原始文本
                return response_text
            
            # 单个查询模式：解析AI响应，提取结构化信息
            extracted_data = self._parse_ai_response(response_text, prompt)
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"OpenAI API请求失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _parse_ai_response(self, response_text: str, original_query: str) -> Dict[str, Any]:
        """
        解析AI响应，提取结构化公司信息（支持多公司输出）
        
        Args:
            response_text: AI响应文本
            original_query: 原始查询
            
        Returns:
            结构化的公司信息，可能包含多家公司
            - 单公司：返回普通字典
            - 多公司：返回 {"multiple_companies": True, "companies": [公司1, 公司2, ...]}
        """
        # 检测是否为多公司响应
        if re.search(r'【发现\s*\d+\s*家匹配公司】', response_text) or \
           (re.search(r'公司1[:：]', response_text) and re.search(r'公司2[:：]', response_text)):
            # 多公司情况
            logger.info("检测到多家公司响应")
            return self._parse_multiple_companies(response_text)
        
        # 单公司情况（原有逻辑）
        data = {
            "full_name": "N/A",
            "unified_social_credit_code": "N/A",
            "legal_representative": "N/A",
            "registered_address": "N/A",
            "company_type": "N/A",
            "industry": "N/A",  # 所属行业
            "is_top500": False,  # 是否为中国企业500强
            "is_listed": False,
            "reg_capital": "N/A",
            "employee_count": "N/A",
            "establishment_date": "N/A",
            "revenue": {},
            "net_profit": {},
            "ai_source": "openai_compatible"
        }
        
        # 使用更精确的正则表达式提取信息（完全匹配prompt中的格式）
        patterns = {
            "full_name": r'公司全名[:：]\s*([^\n]+?)(?:\n|$)',
            "unified_social_credit_code": r'统一社会信用代码[:：]\s*([A-Z0-9]{15,18}|[^\n]+?)(?:\n|$)',
            "legal_representative": r'法定代表人[:：]\s*([^\n]+?)(?:\n|$)',
            "registered_address": r'注册地址[:：]\s*([^\n]+?)(?:\n|$)',
            "company_type": r'公司类型[:：]\s*([^\n]+?)(?:\n|$)',
            "industry": r'所属行业[:：]\s*([^\n]+?)(?:\n|$)',  # 新增：所属行业
            "reg_capital": r'注册资金[（(]亿元[)）][:：]\s*([0-9.]+)',
            "employee_count": r'员工人数[:：]\s*([0-9,]+)',
            "establishment_date": r'成立时间[:：]\s*([0-9]{4}[-年/][0-9]{1,2}[-月/][0-9]{1,2})',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, response_text)
            if match:
                value = match.group(1).strip()
                if value and value not in ["N/A", "无", "未知", "暂无"]:
                    data[key] = value
        
        # 判断是否为中国企业500强（精确匹配）
        is_top500_match = re.search(r'是否为中国企业500强[:：]\s*(是|否)', response_text)
        if is_top500_match:
            data["is_top500"] = (is_top500_match.group(1) == "是")
        else:
            # 尝试其他可能的表述
            if re.search(r'(?:中国500强|企业500强|500强企业)[:：]\s*是', response_text):
                data["is_top500"] = True
        
        # 判断是否上市（精确匹配）
        is_listed_match = re.search(r'是否上市[:：]\s*(是|否)', response_text)
        if is_listed_match:
            data["is_listed"] = (is_listed_match.group(1) == "是")
        else:
            # 如果格式不对，尝试其他匹配
            if re.search(r'(?:已上市|股票代码|证券代码)[:：]\s*[A-Z0-9]+', response_text):
                data["is_listed"] = True
        
        # 如果没有提取到公司全名，使用原始查询中的公司名
        if data["full_name"] == "N/A":
            # 尝试从查询中提取公司名（查询格式：请提供以下公司的详细信息：XXX公司）
            query_match = re.search(r'公司[的详细信息：]{5,}([^\n]+)', original_query)
            if query_match:
                data["full_name"] = query_match.group(1).strip()
            else:
                # 尝试更宽松的匹配
                query_match = re.search(r'[：:]\s*([^\n，,。.]+)', original_query)
                if query_match:
                    data["full_name"] = query_match.group(1).strip()
        
        # 确保所有字段都有值（避免None）
        for key in ["full_name", "unified_social_credit_code", "legal_representative", 
                    "registered_address", "company_type", "reg_capital", 
                    "employee_count", "establishment_date"]:
            if data.get(key) is None or data.get(key) == "":
                data[key] = "N/A"
        
        # 记录提取结果（显示完整性）
        filled_fields = sum(1 for v in data.values() if v and v != "N/A" and (not isinstance(v, dict) or v))
        total_fields = 12  # 基本字段数量（新增is_top500）
        logger.info(f"AI数据提取完成: 公司={data['full_name']}, 完整度={filled_fields}/{total_fields}, 500强={data.get('is_top500', False)}, 营业额={len(data['revenue'])}年, 净利润={len(data['net_profit'])}年")
        
        # 如果提取的信息太少，记录警告
        if filled_fields < 5:
            logger.warning(f"提取信息不完整，仅获取{filled_fields}个字段。AI响应前200字符: {response_text[:200]}")
        
        # 提取营业额和净利润（精确匹配表格列名格式）
        # 格式：2023年营业额（亿元）：7042 或 -5.2（支持负数）
        revenue_pattern = r'([0-9]{4})年营业额[（(]亿元[)）][:：]\s*(-?[0-9.]+)'
        for match in re.finditer(revenue_pattern, response_text):
            year = int(match.group(1))
            value = match.group(2).strip()
            if value and value not in ["N/A", "无", "未知", "暂无"]:
                try:
                    data["revenue"][year] = float(value)
                except ValueError:
                    pass
        
        # 格式：2023年净利润（亿元）：870 或 -5.2（支持负数，亏损）
        profit_pattern = r'([0-9]{4})年净利润[（(]亿元[)）][:：]\s*(-?[0-9.]+)'
        for match in re.finditer(profit_pattern, response_text):
            year = int(match.group(1))
            value = match.group(2).strip()
            if value and value not in ["N/A", "无", "未知", "暂无"]:
                try:
                    data["net_profit"][year] = float(value)
                except ValueError:
                    pass
        
        return data
    
    def _parse_multiple_companies(self, response_text: str) -> Dict[str, Any]:
        """
        解析多公司响应
        
        Args:
            response_text: AI响应文本（包含多家公司）
            
        Returns:
            {"multiple_companies": True, "companies": [公司1, 公司2, ...]}
        """
        companies = []
        
        # 按"公司N："分割
        # 匹配模式：公司1：、公司2：、公司3：等
        sections = re.split(r'公司\d+[:：]', response_text)
        
        # 第一部分通常是前言，跳过
        for section_text in sections[1:]:  # 跳过第一个元素（前言部分）
            if not section_text.strip():
                continue
            
            company_data = self._parse_single_company_section(section_text)
            if company_data and company_data.get("full_name") != "N/A":
                companies.append(company_data)
        
        logger.info(f"解析到 {len(companies)} 家公司")
        
        return {
            "multiple_companies": True,
            "companies": companies,
            "count": len(companies)
        }
    
    def _parse_single_company_section(self, section_text: str) -> Dict[str, Any]:
        """
        解析单个公司的文本块
        
        Args:
            section_text: 单个公司的文本
            
        Returns:
            公司信息字典
        """
        data = {
            "full_name": "N/A",
            "unified_social_credit_code": "N/A",
            "legal_representative": "N/A",
            "registered_address": "N/A",
            "company_type": "N/A",
            "industry": "N/A",
            "is_top500": False,
            "is_listed": False,
            "reg_capital": "N/A",
            "employee_count": "N/A",
            "establishment_date": "N/A",
            "revenue": {},
            "net_profit": {},
            "ai_source": "openai_compatible"
        }
        
        # 使用相同的patterns解析
        patterns = {
            "full_name": r'公司全名[:：]\s*([^\n]+?)(?:\n|$)',
            "unified_social_credit_code": r'统一社会信用代码[:：]\s*([A-Z0-9]{15,18}|[^\n]+?)(?:\n|$)',
            "legal_representative": r'法定代表人[:：]\s*([^\n]+?)(?:\n|$)',
            "registered_address": r'注册地址[:：]\s*([^\n]+?)(?:\n|$)',
            "company_type": r'公司类型[:：]\s*([^\n]+?)(?:\n|$)',
            "industry": r'所属行业[:：]\s*([^\n]+?)(?:\n|$)',
            "reg_capital": r'注册资金[（(]亿元[)）][:：]\s*([0-9.]+)',
            "employee_count": r'员工人数[:：]\s*([0-9,]+)',
            "establishment_date": r'成立时间[:：]\s*([0-9]{4}[-年/][0-9]{1,2}[-月/][0-9]{1,2})',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, section_text)
            if match:
                value = match.group(1).strip()
                if value and value not in ["N/A", "无", "未知", "暂无"]:
                    data[key] = value
        
        # 500强判断
        is_top500_match = re.search(r'是否为中国企业500强[:：]\s*(是|否)', section_text)
        if is_top500_match:
            data["is_top500"] = (is_top500_match.group(1) == "是")
        
        # 上市判断
        is_listed_match = re.search(r'是否上市[:：]\s*(是|否)', section_text)
        if is_listed_match:
            data["is_listed"] = (is_listed_match.group(1) == "是")
        
        # 营业额
        revenue_pattern = r'([0-9]{4})年营业额[（(]亿元[)）][:：]\s*(-?[0-9.]+)'
        for match in re.finditer(revenue_pattern, section_text):
            year = int(match.group(1))
            try:
                data["revenue"][year] = float(match.group(2))
            except:
                pass
        
        # 净利润
        profit_pattern = r'([0-9]{4})年净利润[（(]亿元[)）][:：]\s*(-?[0-9.]+)'
        for match in re.finditer(profit_pattern, section_text):
            year = int(match.group(1))
            try:
                data["net_profit"][year] = float(match.group(2))
            except:
                pass
        
        return data
    
    def test_connection(self):
        """
        测试连接是否正常
        
        Returns:
            tuple: (success: bool, message: str)
                success: True if connection is successful, False otherwise
                message: 成功或错误信息
        """
        if not self.client:
            logger.error("OpenAI客户端未初始化")
            return (False, "OpenAI客户端未初始化")
        
        if not self.model:
            logger.error("未配置模型名称")
            return (False, "未配置模型名称")
        
        try:
            # 发送一个简单的测试请求
            messages = [{"role": "user", "content": "你好，请回复'OK'"}]
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=50,
                stream=False
            )
            
            response = completion.choices[0].message.content
            logger.info(f"测试响应: {response}")
            return (True, f"连接成功！模型响应: {response[:50]}")
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"测试连接失败: {e}")
            
            # 解析常见错误并给出友好提示
            if "402" in error_str or "Payment Required" in error_str or "Insufficient Balance" in error_str:
                return (False, "[Error] Insufficient API account balance\n\nPlease recharge at:\n- DeepSeek: https://platform.deepseek.com\n- Alibaba Cloud: https://bailian.console.aliyun.com/")
            elif "401" in error_str or "Unauthorized" in error_str or "Invalid API Key" in error_str:
                return (False, "[Error] Invalid or expired API Key\n\nPlease check:\n1. API Key is correctly copied\n2. API Key is activated\n3. API Key permissions are valid")
            elif "404" in error_str or "Not Found" in error_str:
                return (False, "[Error] API endpoint or model not found\n\nPlease check:\n1. Base URL is correct\n2. Model name is supported")
            elif "429" in error_str or "Rate Limit" in error_str:
                return (False, "[Error] Rate limit exceeded\n\nPlease try again later or upgrade API plan")
            elif "timeout" in error_str.lower() or "timed out" in error_str.lower():
                return (False, "[Error] Connection timeout\n\nPlease check:\n1. Network connection\n2. Proxy settings if needed\n3. Base URL is correct")
            else:
                return (False, f"[Error] Connection failed\n\nError details:\n{error_str[:200]}")


# 预定义的模型配置
MODEL_CONFIGS = {
    "DeepSeek-Chat（官网）": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "provider": "DeepSeek官网",
        "description": "DeepSeek官方API，需在 https://platform.deepseek.com 申请API Key"
    },
    "DeepSeek-V3（官网）": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-reasoner",
        "provider": "DeepSeek官网",
        "description": "DeepSeek-V3推理模型（含深度思考）"
    },
    "DeepSeek-V3（阿里云）": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "deepseek-v3",
        "provider": "阿里云百炼",
        "description": "通过阿里云百炼访问DeepSeek-V3"
    },
    "DeepSeek-V3.2（阿里云）": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "deepseek-v3.2",
        "provider": "阿里云百炼",
        "description": "通过阿里云百炼访问DeepSeek-V3.2"
    },
    "DeepSeek-R1（阿里云，支持联网搜索）": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "deepseek-r1",
        "provider": "阿里云百炼",
        "description": "DeepSeek-R1推理模型，支持联网搜索（公测）"
    },
    "通义千问-Turbo": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-turbo",
        "provider": "阿里云百炼",
        "description": "通义千问高速版"
    },
    "通义千问-Plus": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
        "provider": "阿里云百炼",
        "description": "通义千问增强版"
    },
    "通义千问-Max": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-max",
        "provider": "阿里云百炼",
        "description": "通义千问旗舰版"
    },
    "自定义模型": {
        "base_url": "",
        "model": "",
        "provider": "自定义",
        "description": "自定义OpenAI兼容API"
    }
}


def test_client():
    """测试OpenAI兼容客户端"""
    import os
    
    # 从环境变量读取API Key
    api_key = os.getenv("DASHSCOPE_API_KEY", "your_api_key_here")
    
    if api_key == "your_api_key_here":
        print("[错误] 请设置DASHSCOPE_API_KEY环境变量")
        return
    
    # 测试DeepSeek
    client = OpenAICompatibleClient(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="deepseek-v3"
    )
    
    # 测试连接
    if client.test_connection():
        print("[成功] 连接成功")
        
        # 测试查询
        result = client.chat("查询华为技术有限公司的详细信息")
        if result:
            print(f"[成功] 查询成功:")
            print(f"  公司全名: {result.get('full_name', 'N/A')}")
            print(f"  信用代码: {result.get('unified_social_credit_code', 'N/A')}")
            print(f"  法人: {result.get('legal_representative', 'N/A')}")
        else:
            print("[错误] 查询失败")
    else:
        print("[错误] 连接失败")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_client()

