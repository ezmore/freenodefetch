import os
import re
import base64
import requests

def fetch_nodes():
    # 1. 从环境变量中读取 SOURCES 网址列表
    sources_env = os.environ.get("SOURCES", "")
    base_urls = [url.strip() for url in sources_env.split("\n") if url.strip()]
    
    if not base_urls:
        print("错误: 未配置 SOURCES 环境变量。")
        return

    all_nodes = []
    # 匹配节点的正则表达式
    node_regex = re.compile(r'(ss|vmess|vless|trojan|ssr)://[a-zA-Z0-9%&_=+.\-/\?#:]+')
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    # 2. 遍历每一个网站，抓取前 3 页
    for base_url in base_urls:
        formatted_url = base_url if base_url.endswith('/') else f"{base_url}/"
        print(f"正在开始抓取源站: {formatted_url}")
        
        for i in range(1, 4):
            target_url = formatted_url if i == 1 else f"{formatted_url}page/{i}/"
            try:
                response = requests.get(target_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    matches = node_regex.findall(response.text)
                    # re.findall 如果有分组只会返回分组，这里我们重新用完整匹配
                    full_matches = [m.group(0) for m in node_regex.finditer(response.text)]
                    all_nodes.extend(full_matches)
                    print(f"  成功解析第 {i} 页，找到 {len(full_matches)} 个节点")
                else:
                    print(f"  第 {i} 页请求失败，状态码: {response.status_code}")
            except Exception as e:
                print(f"  抓取 {target_url} 出错: {e}")

    # 3. 全局去重
    unique_nodes = list(set(all_nodes))
    print(f"抓取完成。共找到 {len(all_nodes)} 个节点，去重后剩余 {len(unique_nodes)} 个。")

    if not unique_nodes:
        print("警告: 未提取到任何有效节点。")
        return

    # 4. 合并并进行 Base64 编码
    subscription_text = "\n".join(unique_nodes)
    base64_bytes = base64.b64encode(subscription_text.encode('utf-8'))
    base64_sub = base64_bytes.decode('utf-8')

    # 5. 创建输出目录并将结果写入文件
    # 文件路径将会是：output/<你的UUID>/v2raysub
    uuid = os.environ.get("UUID", "default_uuid").strip()
    output_dir = f"output/{uuid}"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(f"{output_dir}/v2raysub", "w", encoding="utf-8") as f:
        f.write(base64_sub)
    print(f"订阅文件已成功保存至 {output_dir}/v2raysub")

if __name__ == "__main__":
    fetch_nodes()
