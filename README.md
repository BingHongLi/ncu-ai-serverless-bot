# 目標

使用sam command 創建project，並修改部分設定，使全部程式碼均能被引入，並在本地進行調度

# 流程

### 創造專案

```
# 切換至專案資料夾
cd lambda_docker_tutorial

# 創造專案資料夾
sam init
    Template type -> 1 - AWS Quick Start Templates
    Package type -> 2 - Image (artifact is an image uploaded to an ECR image repository)
    Base image -> 4 - amazon/python3.7-base
    Project name -> 001_local_integrate_docker

```

### 更新Dockerfile

找到hello_world資料夾，將其內容移到最頂端，以利python專案的路徑搜尋，裡面有Dockerfile

將COPY檔案的部分，改為

```
COPY . "./"
```
### 本地開發前，先設置環境變數

```
export DYNAMODB_LOCAL_PATH=http://localhost:8080
export LINE_CHANNEL_SECRET=""
export LINE_CHANNEL_ACCESS_TOKEN=""
export USER_INFO_GS_BUCKET_NAME=""
```

### 建置docker-compose.yml，裡面設置了模擬的dynamodb與s3

參照專案內的docker-compose.yml，並啟用

```
docker-compose up -d
```

### 開發到一個階段後，進行更為逼真的測試，更新template.yaml

追加Parameter大項，並在Resource內追加Environment項

參照專案內的templates.yaml

### 設置env.json，其變數欄位與templates.yaml對應

```
{
    "HelloWorldFunction":{
        "DYNAMODB_LOCAL_PATH":"http://cxcxc-db:8000",
        "LINE_CHANNEL_SECRET":"",
        "LINE_CHANNEL_ACCESS_TOKEN":"",
        "USER_INFO_GS_BUCKET_NAME":""
    }
}
```

### 本地編譯，驗證執行

```
sam build
sam local start-api --env-vars env.json --docker-network cxcxc-sam

```
### 下載ngrok，並啟用對應

```
./ngrok http --region ap  3000
```

# 部署

## 流程簡述

### 建置IAM User

必須有以下服務的權限

```
DynamoDB
S3
CloudWatch logs
Elastic Container Registry
```

### 建置S3 Bucket

請將Bucket名字記錄下來，稍後會繼續使用


### 建置DynamoDB(optional)

### 建置IAM Role

必須有以下服務權限

```
DynamoDB
S3
CloudWatch logs
Elastic Container Registry
```

### 建置ECR Repo

### 在本地將程式碼封裝成docker image，並推入先前建置的雲端ECR Repo

```
# 在專案根目錄下執行
# 事前必須已經使用aws configure登入過
aws ecr get-login-password --region YOUR-REGION | docker login --username AWS --password-stdin YOUR-ACCOUNT-ID.dkr.ecr.YOUR-REGION.amazonaws.com
docker build -t YOUR-ACCOUNT-ID.dkr.ecr.YOUR-REGION.amazonaws.com/YOUR-REPO-NAME .
docker push YOUR-ACCOUNT-ID.dkr.ecr.YOUR-REGION.amazonaws.com/YOUR-REPO-NAME
```

### 創建Lambda Function，選用Container Image方案，並引入環境變數

```
LINE_CHANNEL_SECRET
LINE_CHANNEL_ACCESS_TOKEN
USER_INFO_GS_BUCKET_NAME
```

### 創建API Gateway，並集成先前的Lambda函數

### 將API Gateway 生成的URI，貼回LINE Develop Console
