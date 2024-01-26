## gz-yaohao
## 广州中小客车指标摇号是否过期监控
识别验证码，自动登录，检查是否过期

docker run --rm -v /Users/jacky/Downloads/logs:/logs \
 -e phone="13800138000" \
 -e pwd="密码不是原始密码，可以通过浏览器控制台看提交的密码，是经过加密的" \
 -e ding_token="钉钉的token，要添加 报警 关键字" \
 mafgwo/gz-yaohao-check sh -c "python /app/__main__.py > /logs/log.txt"

 
 如果状态不是待审核或者审核通过 都会报警

