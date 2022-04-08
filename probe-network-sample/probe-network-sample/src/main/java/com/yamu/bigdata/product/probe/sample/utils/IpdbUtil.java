package com.yamu.bigdata.product.probe.sample.utils;

import com.alibaba.fastjson.JSON;
import com.yamu.bigdata.product.probe.conf.ConfigUtil;
import com.yamu.bigdata.product.probe.sample.bridge.EmqXSub;
import net.ipip.ipdb.City;
import net.ipip.ipdb.IPFormatException;
import net.ipip.ipdb.InvalidDatabaseException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.List;

/**
 * 查询ip信息
 */
public class IpdbUtil {

    // 工具类
    private static final ConfigUtil configUtil=new ConfigUtil();
    private static final Logger logger = LoggerFactory.getLogger(IpdbUtil.class);

    // 参数
    private static City city=null;
    private static final String[] ipdbDataFilePaths = configUtil.getValueByKey("ip.db.path").split(",");
    private static String ipdbDataFilePath;

    // 初始化
    private static void init() throws FileNotFoundException {
        // select an existed ipdb file for use.
        for (String aFilePath: ipdbDataFilePaths) {
            File aFile = new File(aFilePath.trim());
            if (aFile.exists()) {
                ipdbDataFilePath = aFile.getPath();
                logger.info("using IPDB file: " + ipdbDataFilePath);
                break;
            }
        }
        if (ipdbDataFilePath == null || ipdbDataFilePath.equals("")) {
            logger.error("no IPDB file was found within the following paths: " + JSON.toJSON(ipdbDataFilePaths));
            throw new FileNotFoundException();
        }
        try {
            city = new City(ipdbDataFilePath);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    // 查询

    /**
     *
     * @param ip
     * @param language
     * @return ["国家","省","城市","","运营商","维度","经度","UTC时区","UTC时区","城市编码","国家编码","语言","AP"]
     * ["中国","上海","上海","","电信","31.224349","121.476753","Asia/Shanghai","UTC+8","310000","86","CN","AP"]
     */
    public static String[] queryByIp(String ip, String language) throws FileNotFoundException {
        if(city==null){
            init();
        }
        try {
            return city.find(ip, language);
        } catch (IPFormatException e) {
            e.printStackTrace();
            return null;
        } catch (InvalidDatabaseException e) {
            e.printStackTrace();
            return null;
        }
    }

}
