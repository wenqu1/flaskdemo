"""
测试工单系统 API
包括：/api/orders、/api/orders/{id}/progress、/api/summary
"""
import requests

BASE_URL = "http://127.0.0.1:5000"


def test_get_all_orders():
    """测试获取所有订单"""
    print("=" * 50)
    print("测试 1: 获取所有订单")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/api/orders")
    print(f"状态码：{response.status_code}")
    print(f"响应数据：{response.json()}")
    print()
    return response.json().get('data', [])


def test_filter_by_status():
    """测试按状态筛选订单"""
    print("=" * 50)
    print("测试 2: 按状态筛选 - in_progress")
    print("=" * 50)
    
    response = requests.get(
        f"{BASE_URL}/api/orders",
        params={"status": "in_progress"}
    )
    print(f"状态码：{response.status_code}")
    print(f"响应数据：{response.json()}")
    print()
    
    print("=" * 50)
    print("测试 3: 按状态筛选 - pending")
    print("=" * 50)
    
    response = requests.get(
        f"{BASE_URL}/api/orders",
        params={"status": "pending"}
    )
    print(f"状态码：{response.status_code}")
    print(f"响应数据：{response.json()}")
    print()


def test_update_progress(order_id, completed_value):
    """测试更新工单进度"""
    print("=" * 50)
    print(f"测试：更新工单 {order_id} 的进度为 {completed_value}")
    print("=" * 50)
    
    response = requests.put(
        f"{BASE_URL}/api/orders/{order_id}/progress",
        json={"completed": completed_value}
    )
    print(f"状态码：{response.status_code}")
    print(f"响应数据：{response.json()}")
    print()
    return response.json()


def test_update_progress_invalid(order_id, completed_value):
    """测试更新工单进度 - 无效数据"""
    print("=" * 50)
    print(f"测试：更新工单 {order_id} 的进度为 {completed_value} (预期失败)")
    print("=" * 50)
    
    response = requests.put(
        f"{BASE_URL}/api/orders/{order_id}/progress",
        json={"completed": completed_value}
    )
    print(f"状态码：{response.status_code}")
    print(f"响应数据：{response.json()}")
    print()
    return response.json()


def test_update_progress_missing_param(order_id):
    """测试更新工单进度 - 缺少参数"""
    print("=" * 50)
    print(f"测试：更新工单 {order_id} 但缺少 completed 参数 (预期失败)")
    print("=" * 50)
    
    response = requests.put(
        f"{BASE_URL}/api/orders/{order_id}/progress",
        json={}
    )
    print(f"状态码：{response.status_code}")
    print(f"响应数据：{response.json()}")
    print()
    return response.json()


def test_get_summary():
    """测试获取汇总数据"""
    print("=" * 50)
    print("测试：获取汇总数据")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/api/summary")
    print(f"状态码：{response.status_code}")
    data = response.json()
    print(f"响应数据：{json.dumps(data, indent=2, ensure_ascii=False)}")
    print()
    return data


def test_full_workflow():
    """完整工作流程测试"""
    print("\n" + "=" * 60)
    print("完整工作流程测试")
    print("=" * 60 + "\n")
    
    # 1. 获取所有订单
    orders = test_get_all_orders()
    if not orders:
        print("❌ 没有获取到订单数据，无法继续测试")
        return
    
    # 2. 获取第一个订单进行测试
    order = orders[0]
    order_id = order['id']
    order_no = order['order_no']
    quantity = order['quantity']
    current_completed = order['completed']
    
    print(f"选择测试订单：{order_no} (ID={order_id}, 计划数量={quantity}, 当前完成={current_completed})\n")
    
    # 3. 测试正常更新进度
    new_completed = min(current_completed + 50, quantity)
    result = test_update_progress(order_id, new_completed)
    
    if result.get('success'):
        updated_data = result.get('data', {})
        print(f"✅ 更新成功！")
        print(f"   新的完成数量：{updated_data.get('completed')}")
        print(f"   进度：{updated_data.get('progress')}%")
        print(f"   状态：{updated_data.get('status')}")
    else:
        print(f"❌ 更新失败：{result.get('error')}")
    
    print()
    
    # 4. 测试错误情况 - 超过计划数量
    print("-- 测试边界条件 --")
    test_update_progress_invalid(order_id, quantity + 10)
    
    # 5. 测试错误情况 - 负数
    test_update_progress_invalid(order_id, -5)
    
    # 6. 测试错误情况 - 缺少参数
    test_update_progress_missing_param(order_id)
    
    # 7. 测试完成全部数量
    print("-- 测试完成工单 --")
    test_update_progress(order_id, quantity)
    
    # 8. 验证汇总数据
    print("-- 验证汇总数据 --")
    summary_data = test_get_summary()
    
    if summary_data.get('success'):
        data = summary_data.get('data', {})
        print(f"✅ 汇总数据验证通过")
        print(f"   总工单数：{data.get('total_orders')}")
        print(f"   总计划产量：{data.get('total_quantity')}")
        print(f"   总完成产量：{data.get('total_completed')}")
        print(f"   整体完成率：{data.get('overall_progress')}%")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    import json
    
    try:
        # 运行完整测试流程
        test_full_workflow()
        
    except requests.exceptions.ConnectionError:
        print("❌ 错误：无法连接到服务器")
        print("请先运行：python 面试代码-app_buggy.py")
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
