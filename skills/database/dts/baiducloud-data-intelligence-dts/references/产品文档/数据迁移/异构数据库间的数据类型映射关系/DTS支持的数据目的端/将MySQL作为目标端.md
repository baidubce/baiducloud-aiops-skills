# 将MySQL作为目标端

## DTS支持的Mysql数据类型

下表列出了使用 DTS 时支持的 Mysql 数据类型以及与 DTS 数据类型的默认映射。

| DTS字段类型 | MYSQL数据类型 |
| --- | --- |
| DTS\_TYPE\_INT1 | TINYINT |
| DTS\_TYPE\_INT2 | SMALLINT |
| DTS\_TYPE\_INT4 | INT |
| DTS\_TYPE\_INT8 | BIGINT |
| DTS\_TYPE\_NUMBER | 如果precision <= 65 && scale <= 30时使用DECIMAL (p,s) ,否则使用varchar，字符集ACSII |
| DTS\_TYPE\_FLOAT | FLOAT |
| DTS\_TYPE\_DOUBLE | DOUBLE |
| DTS\_TYPE\_BYTES | 如果定长 && 字节长度 <= 255 字节使用 BINARY  如果字节长度 <= 65536 字节使用 VARBINARY  如果字节长度 <= 16,777,215 字节使用 MEDIUMBLOB   其他使用 LONGBLOB |
| DTS\_TYPE\_DATE | DATE |
| DTS\_TYPE\_TIME | 如果小数位数 => 0 且 <= 6 使用 TIME (Scale) ; 如果小数位数 => 7 且 <= 9，使用 VARCHAR (37)，字符集ACSII |
| DTS\_TYPE\_DATETIME | 如果小数位数 => 0 且 <= 6，使用 DATETIME (Scale) ; 如果小数位数 => 7 且 <= 9，使用 VARCHAR (37)，字符集ACSII |
| DTS\_TYPE\_STRING | 如果定长 && 字节长度 <= 255 字节使用 CHAR   如果字节长度 <= 65536 字节使用 VARCHAR   如果字节长度 <= 16,777,215 字节使用 MEDIUMTEXT  其他使用 LONGTEXT |
