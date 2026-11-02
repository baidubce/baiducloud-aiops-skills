# 查看备份列表API

### 请求说明

* 查询某个实例备份列表。

### 请求结构

Plain Text

```
GET /v1/instance/{instanceId}/backup  HTTP/1.1
Host: redis.{region}.baidubce.com
Authorization: authorization string
```

### 请求头域

除公共头域外，无其它特殊头域。

### 请求参数

| 参数名称 | 类型 | 是否必须 | 参数位置 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | string | 是 | Path | 集群ID |

  

### 返回头域

除公共头部，无其它特殊头部。

### 返回参数

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| totalCount | Integer | 总数量。 |
| backups | List<BatchBackupRecord> | 结果列表。 |

  

#### BatchBackupRecord 备份信息

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| batchId | String | 备份ID |
| backupType | String | 备份类型- auto表示自动备份 - manual表示手动产生的备份 |
| comment | String | 备注 |
| startTime | String | 开始时间。格式：yyyy-MM-dd'T'HH:mm:ss'Z' |
| recoverable | String | 是否可用于备份恢复。- recoverable - 可用 - non-recoverable - 不可用 |
| records | List<Record> | 按分片备份的列表。 |

  

#### Record 单个备份记录

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| backupRecordId | String | 备份记录ID。 |
| backupId | String | 备份记录ID。 |
| startTime | String | 开始时间。格式：yyyy-MM-dd'T'HH:mm:ss'Z' |
| duration | Long | 持续时间 |
| objectSize | Long | 文件大小 |
| backupType | String | 备份类型。- auto 自动备份 - manual 手动备份 |
| backupStatus | String | 备份状态。- initial 备份中 - success 成功 - doing 备份中 - failed 失败 - expired - recovering 备份恢复中 - recover failed 备份恢复失败 - recover success 备份恢复成功 |
| shardName | String | 分片名称 |
| comment | String | 备注 |

  

### 请求示例

Plain Text

```
GET /v1/instance/scs-bj-ykfiztgpxjny/backup HTTP/1.1
HOST: redis.bj.baidubce.com
Content-Type: application/json 
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2017-11-21T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
```

### 返回示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
Content-Type: application/json
{
  "backups": [
      {
        "backupType": "manual",
        "batchId": "1735873224099928902",
        "batchRecords": [
          {
            "backupId": "4976335",
            "backupRecordId": null,
            "backupStatus": "success",
            "backupType": "manual",
            "comment": "订单11",
            "duration": 1,
            "objectSize": 195,
            "shardName": "Shard-445560",
            "startTime": "2025-01-03T03:00:46Z"
          }
        ],
        "comment": "订单11",
        "recoverable": "recoverable",
        "startTime": "2025-01-03T03:00:46Z"
      }
    ],
    "totalCount": 2
}
```
