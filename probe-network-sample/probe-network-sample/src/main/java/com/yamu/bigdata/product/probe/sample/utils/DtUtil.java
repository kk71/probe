package com.yamu.bigdata.product.probe.sample.utils;

import java.text.ParseException;
import java.util.Calendar;
import java.util.Date;
import java.text.SimpleDateFormat;

/**
 * 时间日期处理工具，
 */
public class DtUtil {
    /**
     * 用于将python通用的"yyyy-MM-dd HH:mm:ss"（local）转换为(utc)
      */
    public static String localToUtc(String localDatetime) {
        if (localDatetime == "" | localDatetime == null) {
            return null;
        }
        SimpleDateFormat pyDateTimeFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        SimpleDateFormat esDateTimeFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'");
        Date dt;
        Calendar c = Calendar.getInstance();
        try {
            dt = pyDateTimeFormat.parse(localDatetime);
            c.setTime(dt);
            c.add(Calendar.HOUR, -8);
            dt = c.getTime();
        } catch (ParseException e) {
            System.out.println(String.format(
                    "invalid original time format coming from python: %s", pyDateTimeFormat));
            return null;
        }
        return esDateTimeFormat.format(dt);
    }

}
