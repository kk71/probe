package com.yamu.bigdata.product.probe.sample.utils;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.yamu.bigdata.product.probe.conf.ConfigUtil;
import org.apache.http.HttpHost;
import org.apache.http.auth.AuthScope;
import org.apache.http.auth.UsernamePasswordCredentials;
import org.apache.http.client.CredentialsProvider;
import org.apache.http.impl.client.BasicCredentialsProvider;
import org.elasticsearch.action.ActionListener;
import org.elasticsearch.action.admin.indices.alias.Alias;
import org.elasticsearch.action.bulk.BackoffPolicy;
import org.elasticsearch.action.bulk.BulkProcessor;
import org.elasticsearch.action.bulk.BulkRequest;
import org.elasticsearch.action.bulk.BulkResponse;
import org.elasticsearch.action.index.IndexRequest;
import org.elasticsearch.action.index.IndexResponse;
import org.elasticsearch.client.RequestOptions;
import org.elasticsearch.client.RestClient;
import org.elasticsearch.client.RestHighLevelClient;
import org.elasticsearch.client.indices.CreateIndexRequest;
import org.elasticsearch.client.indices.GetIndexRequest;
import org.elasticsearch.common.unit.ByteSizeUnit;
import org.elasticsearch.common.unit.ByteSizeValue;
import org.elasticsearch.common.unit.TimeValue;
import org.elasticsearch.common.xcontent.XContentType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.InputStream;
import java.math.BigInteger;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.text.DateFormat;
import java.text.MessageFormat;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Map;
import java.util.function.BiConsumer;

/**
 * 仅支持单挑消息同步和异步发送
 *
 * @author hexiaoqing
 * @date 2020-12-22 10:42:37
 */
public class EsUtil {

    // elasticsearch的索引
    // 拨测数据集合索引
    public static final String esIndexProbedata = "probedata.mapping";

    private static final Logger logger = LoggerFactory.getLogger(EsUtil.class);

    public static DateFormat dateFormatter = new SimpleDateFormat("yyyy.MM.dd");

    /** es客户端 */
    private RestHighLevelClient client = null;

    private long timeout = 0;
    private boolean isSync;

    private String refreshPolicy = null;
    private JSONObject mapping;
    private BulkProcessor probeDataBulkProcessor;
    private String esMappingFile;

    /**
     * 64进制所有字符串
     */
    public static final String[] TABLE = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_".split("");

    public EsUtil(String esMappingFile) {
        this.esMappingFile = esMappingFile;
        init();
    }

    /**
     * 连接初始化
     */
    private void init() {
        ConfigUtil configUtil = new ConfigUtil();

        timeout = Long.parseLong(configUtil.getValueByKey("es.client.timeout"));
        isSync = Boolean.parseBoolean(configUtil.getValueByKey("es.client.isSync"));
        String[] nodes = configUtil.getValueByKey("es.server.node").split("[,]");
        refreshPolicy = configUtil.getValueByKey("es.client.refreshPolicy");
        String username = configUtil.getValueByKey("es.server.username");
        String password = configUtil.getValueByKey("es.server.password");
        try {
            InputStream is = this.getClass().getClassLoader().getResourceAsStream(this.esMappingFile);
            assert is != null;
            mapping = JSON.parseObject(is, JSONObject.class);
        } catch (IOException e) {
            e.printStackTrace();
        }

        HttpHost[] httpHosts = new HttpHost[nodes.length];
        String host = null;
        int sport = 9200;
        for (int i = 0; i < nodes.length; i++) {
            host = nodes[i].split("[:]")[0];
            sport = Integer.parseInt(nodes[i].split("[:]")[1]);
            httpHosts[i] = new HttpHost(host, sport, "http");
        }

        CredentialsProvider provider = new BasicCredentialsProvider();
        provider.setCredentials(AuthScope.ANY, new UsernamePasswordCredentials(username, password));
        client = new RestHighLevelClient(
                RestClient.builder(httpHosts).setHttpClientConfigCallback(httpAsyncClientBuilder -> {
                    httpAsyncClientBuilder.disableAuthCaching();
                    return httpAsyncClientBuilder.setDefaultCredentialsProvider(provider);
                })
        );

        logger.info(String.format(
                "initialized elasticsearch connection with index: %s", this.esMappingFile));

    }

    /**
     * 发送数据
     */
    public IndexResponse submit(Map<String, Object> data, String index) {
        // 初始化
        if (client == null) {
            init();
        }
        // 发送数据
        if (isSync) {
            return syncSubmit(data, index);
        } else {
            return asyncSubmit(data, index);
        }
    }

    private BulkProcessor getBulkProcessor() {
        BulkProcessor.Listener listener = new BulkProcessor.Listener() {

            @Override
            public void beforeBulk(long executionId, BulkRequest request) {
            }

            @Override
            public void afterBulk(long executionId, BulkRequest request, BulkResponse response) {
                logger.info("successfully write elasticsearch document(s): {}", request.numberOfActions());
            }

            @Override
            public void afterBulk(long executionId, BulkRequest request, Throwable failure) {
                logger.error("failed to execute bulk {0}", failure);
            }
        };
        BiConsumer<BulkRequest, ActionListener<BulkResponse>> bulkConsumer = new BiConsumer<BulkRequest, ActionListener<BulkResponse>>() {
            @Override
            public void accept(BulkRequest bulkRequest, ActionListener<BulkResponse> bulkResponseActionListener) {
                client.bulkAsync(bulkRequest, RequestOptions.DEFAULT, bulkResponseActionListener);
            }
        };

        return BulkProcessor.builder(bulkConsumer, listener).setBulkActions(3000)
                .setBulkSize(new ByteSizeValue(5, ByteSizeUnit.MB))
                .setFlushInterval(TimeValue.timeValueSeconds(5))
                .setConcurrentRequests(1)
                .setBackoffPolicy(BackoffPolicy.exponentialBackoff(TimeValue.timeValueMillis(100), 3))
                .build();

    }

    public void bulkSubmit(Map<String, Object> data, String index) {
        if (null == client) {
            init();
        }
        if (null == probeDataBulkProcessor) {
            probeDataBulkProcessor = getBulkProcessor();
        }
        String id = getDataUniqueAutograph(JSON.toJSONString(data));
        IndexRequest request = new IndexRequest(index).source(data).id(id);
        probeDataBulkProcessor.add(request);
    }

    /**
     * 发送数据
     */
    public IndexResponse submit(String data, String index) {
        // 初始化
        if (client == null) {
            init();
        }
        // 发送数据
        if (isSync) {
            return syncSubmit(data, index);
        } else {
            return asyncSubmit(data, index);
        }
    }

    /**
     * 同步发送
     */
    private IndexResponse syncSubmit(Map<String, Object> data, String index) {
        //数据唯一性签名
        String id = getDataUniqueAutograph(JSON.toJSONString(data));
        IndexRequest request = new IndexRequest(index).source(data).id(id);
        return syncSubmit(request);
    }

    /**
     * 同步发送
     */
    private IndexResponse syncSubmit(String data, String index) {

        String id = getDataUniqueAutograph(data);
        IndexRequest request = new IndexRequest(index).source(data).id(id);
        return syncSubmit(request);
    }

    /**
     * 同步提交数据到Elasticsearch
     *
     * @param request 提交请求
     * @return 请求结果
     */
    private IndexResponse syncSubmit(IndexRequest request) {
        //设置超时
        request.timeout(TimeValue.timeValueSeconds(timeout));
        // 设置刷新策略
        request.setRefreshPolicy(refreshPolicy);

        try {
            createIndexIfNotExists(request.index());
            IndexResponse indexResponse = client.index(request, RequestOptions.DEFAULT);
            logger.info("successfully submitted!");
            return indexResponse;
        } catch (IOException e) {
            e.printStackTrace();
            return null;
        }
    }

    // 异步发送
    private IndexResponse asyncSubmit(Map<String, Object> data, String index) {
        String id = getDataUniqueAutograph(JSON.toJSONString(data));
        IndexRequest request = new IndexRequest(index).source(data).id(id);

        return asyncSubmit(request);
    }

    // 异步发送
    private IndexResponse asyncSubmit(String data, String index) {
        String id = getDataUniqueAutograph(data);
        IndexRequest request = new IndexRequest(index).source(data, XContentType.JSON).id(id);

        return asyncSubmit(request);
    }

    /**
     * 异步提交数据到Elasticsearch
     *
     * @param request 提交请求
     * @return 请求结果
     */
    private IndexResponse asyncSubmit(IndexRequest request) {
        // 设置超时
        request.timeout(TimeValue.timeValueSeconds(timeout));
        // 设置刷新策略
        request.setRefreshPolicy(refreshPolicy);
        ActionListener<IndexResponse> listener = new ActionListener<IndexResponse>() {
            @Override
            public void onResponse(IndexResponse indexResponse) {
                indexResponse.status().getStatus();
            }

            @Override
            public void onFailure(Exception e) {
                e.printStackTrace();
            }
        };

        createIndexIfNotExists(request.index());
        client.indexAsync(request, RequestOptions.DEFAULT, listener);

        logger.info("successfully submitted asynchronously!");

        return null;
    }

    /**
     * 释放资源
     */
    public boolean close() {
        try {
            client.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return true;
    }

    /**
     * 根据另外按天生成Elasticsearch索引名
     * 例如Elasticsearch有一类数据(probe-data)需要按天做索引，
     * 那么另外就叫probe-data
     * 每天的索引名为probe-data_20201222
     * 最终会按天做的索引会指向索引别名
     *
     * @param aliasName 索引别名
     * @return 按天的索引名
     */
    public static String getEsDailyIndexName(String aliasName) {
        Calendar calendar = Calendar.getInstance();
        String d = dateFormatter.format(calendar.getTime());
        return aliasName + "-" + d;
    }
    /**
     * 判断索引是否存在
     * 如果索引不存在的话创建
     * 并添加别名和mappings
     * 索引命名规则为:别名-日期
     *
     * @param indexName 索引别名
     */
    public Boolean createIndexIfNotExists(String indexName) {
        GetIndexRequest getIndexRequest = new GetIndexRequest(indexName);

        boolean exists = false;
        try {
            exists = client.indices().exists(getIndexRequest, RequestOptions.DEFAULT);
        } catch (IOException e) {
            logger.error(MessageFormat.format("Elasticsearch check if index exists error, indexname: {0}", indexName));
            e.printStackTrace();
            return false;
        }
        if (!exists) {
            //索引命名规则为:别名-日期
            String aliasName = indexName.split("-")[0];
            logger.info(MessageFormat.format(
                    "index {0} not existed, creating with alias name({1})} ...",
                    indexName,
                    aliasName
            ));

            //创建索引
            CreateIndexRequest createIndexRequest = new CreateIndexRequest(indexName);

            //添加别名
            Alias alias = new Alias(aliasName);
            createIndexRequest.alias(alias);

            //添加mapping
            createIndexRequest.mapping(getIndexMappingByAliasName(indexName), XContentType.JSON);

            try {
                //执行操作
                client.indices().create(createIndexRequest, RequestOptions.DEFAULT);
                logger.info(MessageFormat.format("create index --> {0}, alias --> {1}", indexName, aliasName));
            } catch (IOException e) {
                logger.error(MessageFormat.format("Elasticsearch create index error: indexname: {0}", indexName));
                e.printStackTrace();
                return false;
            }
        }
        return true;
    }

    /**
     * 根据索引别名获取mapping
     *
     * @param indexName 索引名或别名
     * @return mapping
     */
    public String getIndexMappingByAliasName(String indexName) {
        for (String key : mapping.keySet()) {
            if (indexName.contains(key)) {
                return mapping.getJSONObject(key).getJSONObject("mappings").toJSONString();
            }
        }
        return null;
    }

    public String getDataUniqueAutograph(String data) {
        BigInteger md5 = encodeMd5(data);
        return encodeB64(md5);
    }

    /**
     * 字符串类型的数据进行数据唯一性签名
     *
     * @param data 字符串类型的数据
     * @return 数据唯一性签名(Elasticsearch的_id
     */
    public static BigInteger encodeMd5(String data) {
        byte[] secretBytes = null;
        try {
            secretBytes = MessageDigest.getInstance("md5").digest(data.getBytes());
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        }
        assert secretBytes != null;
        return new BigInteger(1, secretBytes);
    }

    /**
     * 10进制转64进制
     * 64进制字符为:
     * 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_
     */
    public static String encodeB64(BigInteger bi) {
        StringBuilder sb = new StringBuilder();
        BigInteger num64 = BigInteger.valueOf(64);
        do {
            int i = bi.remainder(num64).intValue();
            sb.insert(0, TABLE[i]);
            bi = bi.divide(num64);
        } while (bi.compareTo(BigInteger.ZERO) != 0);

        return sb.toString();
    }

}
