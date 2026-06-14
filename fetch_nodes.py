import os
import re
import base64
import requests

def fetch_nodes():
    # 强制先创建 output 目录，防止后续流程找不到目录而报错
    uuid = os.environ.get("UUID", "default_uuid").strip()
    output_dir = f"output/{uuid}"
    os.makedirs(output_dir, exist_ok=True)

    sources_env = os.environ.get("SOURCES", "")
    base_urls = [url.strip() for url in sources_env.split("\n") if url.strip()]
    
    if not base_urls:
        print("错误: 未配置 SOURCES 环境变量。")
        # 写入一个空订阅，防止部署插件报错
        with open(f"{output_dir}/v2raysub", "w") as f: f.write("")
        return

    all_nodes = []
    node_regex = re.compile(r'(ss|vmess|vless|trojan|ssr)://[a-zA-Z0-9%&_=+.\-/\?#:]+')
    
    # 模拟更真实的现代浏览器请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
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
                response = requests.get(target_url, headers=headers, timeout=15)
                print(f"  请求 {target_url} -> 状态码: {response.status_code}")
                
                if response.status_code == 200:
                    full_matches = [m.group(0) for m in node_regex.finditer(response.text)]
                    all_nodes.extend(full_matches)
                    print(f"  成功解析第 {i} 页，找到 {len(full_matches)} 个节点")
                elif response.status_code in [403, 503]:
                    print(f"  警告: 被网站拦截(盾)。状态码: {response.status_code}。可能需要更换源站或更换支持过盾的库。")
            except Exception as e:
                print(f"  抓取 {target_url} 出错: {e}")

    unique_nodes = list(set(all_nodes))
    print(f"抓取完成。共找到 {len(all_nodes)} 个节点，去重后剩余 {len(unique_nodes)} 个。")

    # 编码并写入
    subscription_text = "\n".join(unique_nodes) if unique_nodes else ""
    base64_bytes = base64.b64encode(subscription_text.encode('utf-8'))
    base64_sub = base64_bytes.decode('utf-8')
    
    with open(f"{output_dir}/v2raysub", "w", encoding="utf-8") as f:
        f.write(base64_sub)
    print(f"订阅文件已处理，保存至 {output_dir}/v2raysub")

if __name__ == "__main__":
    fetch_nodes()
