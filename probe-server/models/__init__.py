# Author: kk.Fang(fkfkbill@gmail.com)

from settings import Setting


async def init_models(include_mysql: bool = False):
    """
    初始化数据库连接
    :param include_mysql: 是否连接mysql？（默认是不用的，目前业务数据库仅用redis）
    :return:
    """

    print("Initializing database connections ...")

    # TODO mysql的模块现在不用了所以暂时是没有加入requirements.txt的
    #      如果需要使用请先加入
    if include_mysql:
        # connect to mysql
        global Session, engine, base
        from sqlalchemy import create_engine
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker
        engine = create_engine(
            f"mysql+pymysql://{Setting.MYSQL_USERNAME}:{Setting.MYSQL_PASSWORD}@"
            f"{Setting.MYSQL_IP}:{Setting.MYSQL_PORT}/{Setting.MYSQL_DB_NAME}",
            echo=Setting.MYSQL_ECHO)
        base = declarative_base()
        Session = sessionmaker(bind=engine)

    # connect to redis
    from .redis import BaseRedis
    await BaseRedis.process()
    from .redis import RedisAuth
    RedisAuth.init_for_internal_user()

    # connect to elasticsearch
    from elasticsearch_dsl import connections
    connections.create_connection(
        hosts=[f"{Setting.ES_IP}:{Setting.ES_PORT}"],
        http_auth=(Setting.ES_USERNAME, Setting.ES_PASSWORD)
    )
