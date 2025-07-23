## 增量爬虫演示

1. **首次运行**  
   `python crawler.py` 会抓取全站并入库。

2. **每日定时**  
   GitHub Actions 每晚 3 点自动跑；Redis 去重，秒级增量。

3. **版面改版**  
   解析失败 → 自动截图 → LLM 生成新 CSS Selector → 写入 selector.json → 重试。

4. **零人工**  
   正常情况不消耗 OpenAI Token，仅异常时介入。