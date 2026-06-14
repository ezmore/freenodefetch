import os
import re
import base64

def fetch_nodes():
    # 无论如何，先创建出 output 目录，避免 GitHub Action 找不到目录而报错
    uuid = os.environ.get("UUID", "default_uuid").strip()
    output_dir = f"output/{uuid}"
    os.makedirs(output_dir, exist_ok=True)

    sources_env = os.environ.get("SOURCES", "")
    base_urls = [url.strip() for url in sources_env.split("\n") if url.strip()]
    
    if not base_urls:
        print("错误: 未配置 SOURCES 环境变量。")
        with open(f"{output_dir}/v2raysub", "w") as f: f.write("")
        return

    # 在这里延迟导入 curl_cffi，确保 actions 安装完依赖后再调用
    try:
        from curl_cffi import requests
    except ImportError:
        import requests
        print("警告: 未检测到 curl_cffi，降级使用标准 requests。")

    all_nodes = []
    node_regex = re.compile(r'(ss|vmess|vless|trojan|ssr)://[a-zA-Z0-9%&_=+.\-/\?#:]+')
    
    # 模拟真实现代浏览器
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }

    for base_url in base_urls:
        formatted_url = base_url if base_url.endswith('/') else f"{base_url}/"
        print(f"正在开始抓取源站: {formatted_url}")
        
        for i in range(1, 4):
            target_url = formatted_url if i == 1 else f"{formatted_url}page/{i}/"
            try:
                # 使用 curl_cffi 模拟 chrome120 浏览器指纹，极强过盾能力
                # 如果降级到了标准 requests，impersonate 参数会被忽略
                kwargs = {"headers": headers, "timeout": 15}
                if 'curl_cffi' in globals() or 'curl_cffi' in locals() or 'requests' in str(requests.__file__):
                    try:
                        response = requests.get(target_url, impersonate="chrome120", **kwargs)
                    except TypeError:
                        response = requests.get(target_url, **kwargs)
                
                print(f"  请求 {target_url} -> 状态码: {response.status_code}")
                
                if response.status_code == 200:
                    full_matches = [m.group(0) for m in node_regex.finditer(response.text)]
                    all_nodes.extend(full_matches)
                    print(f"  成功解析第 {i} 页，找到 {len(full_matches)} 个节点")
                else:
                    print(f"  页面请求失败，状态码: {response.status_code}。可能是遇到高强度人机验证。")
            except Exception as e:
                print(f"  抓取 {target_url} 出错: {e}")

    unique_nodes = list(set(all_nodes))
    print(f"抓取完成。共找到 {len(all_nodes)} 个节点，去重后剩余 {len(unique_nodes)} 个。")

    # 编码并写入文件
    subscription_text = "\n".join(unique_nodes) if unique_nodes else ""
    base64_bytes = base64.b64encode(subscription_text.encode('utf-8'))
    base64_sub = base64_bytes.decode('utf-8')
    
    with open(f"{output_dir}/v2raysub", "w", encoding="utf-8") as f:
        f.write(base64_sub)
    print(f"订阅文件处理完毕，成功保存至 {output_dir}/v2raysub")

if __name__ == "__main__":
    fetch_nodes()
