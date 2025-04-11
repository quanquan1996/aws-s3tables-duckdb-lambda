# Quick Start
## Step 1
```
git clone https://github.com/quanquan1996/aws-s3tables-duckdb-lambda.git  

cd aws-s3tables-duckdb-lambda   

aws ecr get-login-password --region {yourRegion} | docker login --username AWS --password-stdin {yourAccountID}.dkr.ecr.{yourRegion}.amazonaws.com  
    
sudo docker buildx build --platform linux/amd64 --provenance=false -t docker-image:{yourImageName} .    
    
sudo docker tag docker-image:{yourImageName} {yourAccountID}.dkr.ecr.{yourRegion}.amazonaws.com/{yourEcrRepoName}:latest    
    
sudo docker push {yourAccountID}.dkr.ecr.{yourRegion}.amazonaws.com/{yourEcrRepoName}:latest   
```   
    
## Step 2
use your ECR repo name in the lambda function, and you are ready to go  

## 性能
### 测试数据集 
行数：13亿
ddl:
```
CREATE TABLE s3tablesbucket.testdb.commerce_shopping_big (
user_id    STRING    COMMENT '用户ID（非真实ID），经抽样&字段脱敏处理后得到',
item_id    STRING    COMMENT '商品ID（非真实ID），经抽样&字段脱敏处理后得到',
item_category    STRING    COMMENT '商品类别ID（非真实ID），经抽样&字段脱敏处理后得到',
behavior_type    STRING    COMMENT '用户对商品的行为类型,包括浏览、收藏、加购物车、购买，pv,fav,cart,buy)',
behavior_time    STRING    COMMENT '行为时间,精确到小时级别' ) USING iceberg
```
测试sql:              
用户行为数据漏斗分析
``` 
-- 用户行为漏斗分析
-- 总用户数(total_users)
-- 浏览过商品的用户数(users_with_views)
-- 收藏过商品的用户数(users_with_favorites)
-- 加入购物车的用户数(users_with_cart_adds)
-- 完成购买的用户数(users_with_purchases)
-- 浏览率(view_rate)：浏览用户占总用户百分比
-- 浏览到收藏转化率(view_to_favorite_rate)
-- 收藏到加购转化率(favorite_to_cart_rate)
-- 加购到购买转化率(cart_to_purchase_rate)
-- 整体转化率(overall_conversion_rate)：购买用户占总用户百分比
WITH user_behavior_counts AS (
    SELECT
        user_id,
        SUM(CASE WHEN behavior_type = 'pv' THEN 1 ELSE 0 END) AS view_count,
        SUM(CASE WHEN behavior_type = 'fav' THEN 1 ELSE 0 END) AS favorite_count,
        SUM(CASE WHEN behavior_type = 'cart' THEN 1 ELSE 0 END) AS cart_count,
        SUM(CASE WHEN behavior_type = 'buy' THEN 1 ELSE 0 END) AS purchase_count
    FROM testtable.testdb.commerce_shopping
    GROUP BY user_id
),
funnel_stages AS (
    SELECT
        COUNT(DISTINCT user_id) AS total_users,
        COUNT(DISTINCT CASE WHEN view_count > 0 THEN user_id END) AS users_with_views,
        COUNT(DISTINCT CASE WHEN favorite_count > 0 THEN user_id END) AS users_with_favorites,
        COUNT(DISTINCT CASE WHEN cart_count > 0 THEN user_id END) AS users_with_cart_adds,
        COUNT(DISTINCT CASE WHEN purchase_count > 0 THEN user_id END) AS users_with_purchases
    FROM user_behavior_counts
)
SELECT
    total_users,
    users_with_views,
    users_with_favorites,
    users_with_cart_adds,
    users_with_purchases,
    ROUND(100.0 * users_with_views / total_users, 2) AS view_rate,
    ROUND(100.0 * users_with_favorites / users_with_views, 2) AS view_to_favorite_rate,
    ROUND(100.0 * users_with_cart_adds / users_with_favorites, 2) AS favorite_to_cart_rate,
    ROUND(100.0 * users_with_purchases / users_with_cart_adds, 2) AS cart_to_purchase_rate,
    ROUND(100.0 * users_with_purchases / total_users, 2) AS overall_conversion_rate
FROM funnel_stages;
```
lambda测试结果：
消耗内存:1934M  
用时:37s  
