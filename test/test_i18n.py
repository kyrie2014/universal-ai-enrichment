"""
测试国际化功能
Test internationalization functionality
"""

from i18n import get_language_manager, t

def test_i18n():
    """测试国际化功能"""
    print("=" * 60)
    print("测试国际化功能 / Testing I18N Functionality")
    print("=" * 60)
    
    # 获取语言管理器
    lang_manager = get_language_manager()
    
    # 测试中文
    print("\n【测试中文 / Testing Chinese】")
    lang_manager.set_language("zh_CN")
    print(f"app_title: {t('app_title')}")
    print(f"start_button: {t('start_button')}")
    print(f"ai_settings_button: {t('ai_settings_button')}")
    print(f"help_button: {t('help_button')}")
    print(f"language_button: {t('language_button')}")
    
    # 测试英文
    print("\n【测试英文 / Testing English】")
    lang_manager.set_language("en_US")
    print(f"app_title: {t('app_title')}")
    print(f"start_button: {t('start_button')}")
    print(f"ai_settings_button: {t('ai_settings_button')}")
    print(f"help_button: {t('help_button')}")
    print(f"language_button: {t('language_button')}")
    
    # 测试带格式化的文本
    print("\n【测试格式化文本 / Testing Formatted Text】")
    lang_manager.set_language("zh_CN")
    print(t("rows_read", "默认文本").format(100))
    
    lang_manager.set_language("en_US")
    print(t("rows_read", "Default text").format(100))
    
    print("\n" + "=" * 60)
    print("✅ 国际化功能测试完成！ / I18N Test Completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_i18n()

