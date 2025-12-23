"""
创建测试数据 - 生成示例Excel文件用于测试通用AI Agent
"""

import pandas as pd
import os


def create_company_test_data():
    """创建企业信息补充测试数据"""
    data = {
        '公司': [
            '华为',
            '小米',
            'OPPO',
            'vivo',
            '比亚迪',
            '阿里巴巴',
            '腾讯',
            '字节跳动',
            '美团',
            '拼多多'
        ]
    }
    
    df = pd.DataFrame(data)
    df.to_excel('测试数据_企业信息.xlsx', index=False)
    print("✅ 已创建：测试数据_企业信息.xlsx")


def create_product_test_data():
    """创建产品信息查询测试数据"""
    data = {
        '产品名称': [
            'iPhone 15 Pro',
            '小米14 Ultra',
            '华为Mate 60 Pro',
            'OPPO Find X7 Ultra',
            'vivo X100 Pro',
            'iPad Pro',
            'MacBook Pro',
            'Surface Pro',
            'ThinkPad X1',
            'Dell XPS 13'
        ]
    }
    
    df = pd.DataFrame(data)
    df.to_excel('测试数据_产品信息.xlsx', index=False)
    print("✅ 已创建：测试数据_产品信息.xlsx")


def create_person_test_data():
    """创建人物信息补充测试数据"""
    data = {
        '姓名': [
            '雷军',
            '马化腾',
            '张一鸣',
            '王兴',
            '黄峥',
            '马云',
            '李彦宏',
            '刘强东',
            '任正非',
            '李书福'
        ],
        '公司': [
            '小米',
            '腾讯',
            '字节跳动',
            '美团',
            '拼多多',
            '阿里巴巴',
            '百度',
            '京东',
            '华为',
            '吉利'
        ]
    }
    
    df = pd.DataFrame(data)
    df.to_excel('测试数据_人物信息.xlsx', index=False)
    print("✅ 已创建：测试数据_人物信息.xlsx")


def create_restaurant_test_data():
    """创建餐厅信息查询测试数据"""
    data = {
        '餐厅名称': [
            '海底捞',
            '西贝莜面村',
            '外婆家',
            '绿茶餐厅',
            '云海肴',
            '小龙坎',
            '巴奴毛肚火锅',
            '新荣记',
            '金鼎轩',
            '呷哺呷哺'
        ],
        '城市': [
            '北京',
            '上海',
            '杭州',
            '杭州',
            '昆明',
            '成都',
            '郑州',
            '台州',
            '北京',
            '北京'
        ]
    }
    
    df = pd.DataFrame(data)
    df.to_excel('测试数据_餐厅信息.xlsx', index=False)
    print("✅ 已创建：测试数据_餐厅信息.xlsx")


def create_movie_test_data():
    """创建电影信息查询测试数据"""
    data = {
        '电影名称': [
            '流浪地球2',
            '满江红',
            '长安三万里',
            '封神第一部',
            '消失的她',
            '八角笼中',
            '热辣滚烫',
            '飞驰人生2',
            '第二十条',
            '周处除三害'
        ]
    }
    
    df = pd.DataFrame(data)
    df.to_excel('测试数据_电影信息.xlsx', index=False)
    print("✅ 已创建：测试数据_电影信息.xlsx")


def create_all_test_data():
    """创建所有测试数据"""
    print("开始创建测试数据...\n")
    
    create_company_test_data()
    create_product_test_data()
    create_person_test_data()
    create_restaurant_test_data()
    create_movie_test_data()
    
    print("\n✅ 所有测试数据创建完成！")
    print("\n可用于测试的文件：")
    print("  1. 测试数据_企业信息.xlsx - 使用 company_enrichment 方案")
    print("  2. 测试数据_产品信息.xlsx - 使用 product_enrichment 方案")
    print("  3. 测试数据_人物信息.xlsx - 使用 person_enrichment 方案")
    print("  4. 测试数据_餐厅信息.xlsx - 需要创建 restaurant_info 方案")
    print("  5. 测试数据_电影信息.xlsx - 需要创建 movie_info 方案")


if __name__ == "__main__":
    create_all_test_data()

