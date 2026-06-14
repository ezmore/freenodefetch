import os
import base64

def fetch_nodes():
    # 1. 强制先创建出 output 目录
    uuid = os.environ.get("UUID", "default_uuid").strip()
    output_dir = f"output/{uuid}"
    os.makedirs(output_dir, exist_ok=True)

    sources_env = os.environ.get("SOURCES", "")
    base_urls = [url.strip() for url in sources_env.split("\n") if url.strip()]
    
    if not base_urls:
        print("错误: 未配置 SOURCES 环境变量。")
        with open(f"{output_dir}/v2raysub", "w") as f: f.write("")
        return

    try:
        from curl_cffi import requests
    except ImportError:
        import requests

    all_nodes = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Origin': 'https://shadowmere.xyz',
        'Referer': 'https://shadowmere.xyz/'
    }

    for base_url in base_urls:
        # 兼容处理：如果是 shadowmere.xyz，直接将目标锁定到它的隐藏 API
        if "shadowmere.xyz" in base_url:
            print("检测到 shadowmere.xyz，正在切换至 API JSON 抓取模式...")
            
            # 循环请求 API 的前 3 页
            for page in range(1, 4):
                api_url = f"https://shadowmere.xyz/api/proxies/?format=json&is_active=true&page={page}"
                try:
                    response = requests.get(api_url, headers=headers, impersonate="chrome120", timeout=15)
                    print(f"  请求 API Page {page} -> 状态码: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        # 根据 Next.js 后端常见规范，遍历返回的列表提取 url 字段
                        # 如果返回的是字典且含有 'results'
                        results = data.get("results", []) if isinstance(data, dict) else data
                        
                        page_nodes_count = 0
                        for item in results:
                            if isinstance(item, dict) and "url" in item:
                                all_nodes.append(item["url"])
                                page_nodes_count += 1
                        print(f"  成功从 API 解析第 {page} 页，提取到 {page_nodes_count} 个节点")
                except Exception as e:
                    print(f"  抓取 API {page} 出错: {e}")
                    
        else:
            # ==========================================
            # 其他常规网站保持原本的 HTML 正则匹配逻辑
            # ==========================================
            import re
            node_regex = re.compile(r'(ss|vmess|vless|trojan|ssr)://[a-zA-Z0-9%&_=+.\-/\?#:]+')
            formatted_url = base_url if base_url.endswith('/') else f"{base_url}/"
            print(f"正在开始抓取常规源站: {formatted_url}")
            
            for i in range(1, 4):
                target_url = formatted_url if i == 1 else f"{formatted_url}page/{i}/"
                try:
                    response = requests.get(target_url, headers=headers, impersonate="chrome120", timeout=15)
                    if response.status_code == 200:
                        full_matches = [m.group(0) for m in node_regex.finditer(response.text)]
                        all_nodes.extend(full_matches)
                        print(f"  成功解析常规站第 {i} 页，找到 {len(full_matches)} 个节点")
                except Exception as e:
                    print(f"  抓取常规站出错: {e}")

    # 全局去重
    unique_nodes = list(set(all_nodes))
    print(f"【聚合完毕】共找到 {len(all_nodes)} 个节点，去重后剩余 {len(unique_nodes)} 个。")

    # 编码并写入文件
    subscription_text = "\n".join(unique_nodes) if unique_nodes else ""
    base64_sub = base64.b64encode(subscription_text.encode('utf-8')).decode('utf-8')
    
    with open(f"{output_dir}/v2raysub", "w", encoding="utf-8") as f:
        f.write(base64_sub)
    print(f"工作结束。订阅已打包同步。")

if __name__ == "__main__":
    fetch_nodes()
