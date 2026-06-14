# freenodefetch
自己填更新源地址（多行多地址），每天自动获取最新的节点信息，自己设定订阅地址：https://你的github用户名.github.io/你的仓库名/你设置的UUID/v2raysub

<br>
通过 GitHub Actions 定时执行一个脚本，抓取节点后自动更新到 GitHub Pages，或者直接更新到当前仓库的一个分支（或 Release）中，从而生成一个永久的订阅链接。
<br><br>
整体逻辑<br>
配置：将 UUID 和 SOURCES 配置在 GitHub 仓库的 Secrets 中，确保隐私安全。<br>
<br><br>
定时任务：每天定时（通过 Cron）触发一次工作流。
<br><br>
脚本执行：运行一个 Python 脚本，读取 Secrets 中的网址，抓取前 3 页的节点并进行 Base64 编码。
<br><br>
发布：将编码后的文本保存为文件，自动推送到仓库的 gh-pages 分支（生成一个订阅 URL）。
<br><br>
第一步：fork本项目到自己的Github帐号中<br><br>
第二步：在 GitHub 仓库中配置 Secrets<br>
为了不把隐私暴露在公开代码中，我们需要在 GitHub 仓库中设置两个变量。<br>

打开你的 GitHub 仓库，点击顶部的 Settings。<br>

在左侧菜单中找到 Secrets and variables -> 点击 Actions。<br>

点击右侧的 New repository secret 分别添加以下两个变量：<br>

名称 1：UUID<br>

值：你的专属字符串（例如 my-private-uuid-12345，不需要非得是标准 UUID 格式，只要复杂即可）。<br>

名称 2：SOURCES<br>

值：目标网站，每行一个。例如：<br>

https://shadowmere.xyz/<br>
https://another-site.com/<br>
