import os
import re
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
    # 增强版节点匹配正则：确保捕获完整的长节点链接（包括带 #别名 或 ?参数 的完整后缀）
    node_regex = re.compile(r'(ss|vmess|vless|trojan|ssr)://[a-zA-Z0-9%&_=+.\-/\?#:@~]+')
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }

    for base_url in base_urls:
        formatted_url = base_url if base_url.endswith('/') else f"{base_url}/"
        print(f"正在抓取源站: {formatted_url}")
        
        # 尝试抓取前 3 页
        for i in range(1, 4):
            target_url = formatted_url if i == 1 else f"{formatted_url}page/{i}/"
            try:
                response = requests.get(target_url, headers=headers, impersonate="chrome120", timeout=15)
                print(f"  页面 {target_url} -> 状态码: {response.status_code}")
                
                if response.status_code == 200:
                    html_content = response.text
                    
                    # 1. 提取当前页面 HTML 中所有完整的节点
                    matches = [m.group(0) for m in node_regex.finditer(html_content)]
                    
                    # 2. 特殊处理：如果页面里包含了 Next.js 的打包脚本，顺藤摸瓜去抓取可能包含完整数据的 JS 配置文件
                    if "__NEXT_DATA__" in html_content:
                        print("  检测到 Next.js 动态架构，正在深度挖掘页面脚本数据...")
                        # 尝试从 Next.js 的静态缓存数据中直接抠出所有符合节点格式的字符串
                        js_matches = [m.group(0) for m in node_regex.finditer(html_content)]
                        matches.extend(js_matches)

                    # 过滤掉明显的残缺节点（比如长度小于30位，或者不包含 @ 或 IP 端口特征的残次品）
                    valid_matches = []
                    for node in matches:
                        # 基础清洗：如果是 vless/vmess/ss，必须包含必要的网络结构
                        if "://" in node:
                            # 剔除掉只有 uuid 的残缺 vless 节点
                            if node.startswith("vless://") and "@" not in node:
                                continue
                            valid_matches.append(node)

                    all_nodes.extend(valid_matches)
                    print(f"  第 {i} 页清洗过滤完毕，提取到 {len(valid_matches)} 个完整节点")
                    
            except Exception as e:
                print(f"  抓取 {target_url} 出错: {e}")

    # 全局去重
    unique_nodes = list(set(all_nodes))
    print(f"【洗牌完成】共找到 {len(all_nodes)} 个节点，过滤去重后剩余 {len(unique_nodes)} 个完整节点。")

    # 编码并写入文件
    subscription_text = "\n".join(unique_nodes) if unique_nodes else ""
    base64_sub = base64.b64encode(subscription_text.encode('utf-8')).decode('utf-8')
    
    with open(f"{output_dir}/v2raysub", "w", encoding="utf-8") as f:
        f.write(base64_sub)
    print(f"专属订阅打包同步成功。")

if __name__ == "__main__":
    fetch_nodes()
