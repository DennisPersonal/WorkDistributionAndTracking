#!/usr/bin/env python3
"""快速测试脚本"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("🚀 快速测试 Work Distribution and Tracking System")
print("=" * 60)

try:
    # 测试导入
    from src.app import create_app
    print("✅ 模块导入成功")
    
    # 创建应用
    app = create_app()
    print("✅ Flask应用创建成功")
    
    # 测试数据库连接
    with app.app_context():
        from src.app import db
        db.create_all()
        print("✅ 数据库连接正常")
        
        # 测试路由
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(rule.rule)
        
        print(f"✅ 路由加载正常 ({len(routes)} 个路由)")
        
        # 显示主要路由
        print("\n主要路由:")
        main_routes = [r for r in routes if not r.startswith('/static')]
        for route in sorted(main_routes)[:15]:
            print(f"  {route}")
        
        if len(main_routes) > 15:
            print(f"  ... 还有 {len(main_routes)-15} 个路由")
    
    print("\n" + "=" * 60)
    print("🎉 所有测试通过！")
    print("\n启动命令:")
    print("  python run.py")
    print("  或")
    print("  ./develop.sh start")
    print("\n访问 http://localhost:5001")
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)