数据结构模型
==========

## 约定

### 关于getter和setter

1. 避免累赘的getter和setter，不需要修改实际存储数据的字段，直接使用public定义。
   如果字段读或者写的时候需要修改后写入、修饰后返回，那么必须使用getter和setter。
   
2. getter和setter须成对出现。如果有getter和setter，则实际存放数据的字段必须不能使用public。
