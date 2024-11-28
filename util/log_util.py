import logging
import logging.config
import logging.handlers as handlers
import json
import os
import sys
import inspect
import re
import socket
#from kafka_handler import KafkaLogHandler
# from kafka_logger.handlers import KafkaLoggingHandler
# from kafka_util import KafkaHandler
from  dict_util import MyDict
from cfg_util import Config
import logging.config

########################JSONFormmater######################################
import collections
import datetime
from typing import Any, Dict, Optional

standard_attributes = (
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "message",
    "asctime",
)


def _extra_attributes(record: logging.LogRecord) -> Dict[str, Any]:
    return {
        name: record.__dict__[name]
        for name in set(record.__dict__).difference(standard_attributes)
    }


def _value(record: logging.LogRecord, field_name_or_value: Any) -> Any:
    """
    Retrieve value from record if possible. Otherwise use value.
    :param record: The record to extract a field named as in field_name_or_value.
    :param field_name_or_value: The field name to extract from record or the default value to use if not present.
    """
    try:
        return getattr(record, field_name_or_value)
    except:
        return field_name_or_value


def default_converter(obj: Any) -> str:
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    return str(obj)


class JSONFormatter(logging.Formatter):
    def __init__(
        self,
        *args,
        fields: Dict[str, Any] = None,
        message_field_name: str = "message",
        exception_field_name: Optional[str] = "exception",
        **kwargs,
    ):
        # Allow to provide any formatter setting (useful to provide a custom date format)
        super().__init__(*args, **kwargs)
        self.fields = fields or {}
        self.usesTime = lambda: "asctime" in self.fields.values()
        self.message_field_name = message_field_name
        self.exception_field_name = exception_field_name

    def format(self, record: logging.LogRecord):
        # Let python set every additional record field
        super().format(record)

        message = {
            field_name: _value(record, field_value)
            for field_name, field_value in self.fields.items()
        }
        if isinstance(record.msg, collections.abc.Mapping):
            message.update(record.msg)
        else:
            message[self.message_field_name] = super().formatMessage(record)

        message.update(_extra_attributes(record))

        if self.exception_field_name and record.exc_info:
            message[self.exception_field_name] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "stack": self.formatException(record.exc_info),
            }

        if len(message) == 1 and self.message_field_name in message:
            return super().formatMessage(record)

        return json.dumps(message, default=default_converter, ensure_ascii=False)

    def formatMessage(self, record: logging.LogRecord) -> str:
        # Speed up this step by doing nothing
        return ""
############################################################################


LOG_SCREEN = 1
LOG_FILE = 2
LOG_KAFKA = 4
LOG_DEFAULT = LOG_FILE | LOG_KAFKA

LOG_DEBUG = 1
LOG_INFO = 2
LOG_WARNING = 4
LOG_ERROR = 8
LOG_CRITICAL = 16

CFG_JSON = 1
CFG_YAML = 2
CFG_FILE = 1
CFG_STRING = 2

class Log:
    error = None
    logger = None
    log_config = None
    kstream_hdl = None
    kstream_formatter = None
    user_prefix = None

    # initializer
    def __init__(self, name=None):
        if name is not None:
            self.log_name = name
            self.logger = logging.getLogger(name)
        return

    def GetError(self):
        return self.error

    # JSON 포맷 로그 생성시 Prefix 용 데이터 처리
    def SetUserPrefix(self,prefixtdata):
        self.user_prefix = prefixtdata

    def GetConfig(self):
        return self.log_config

    def OpenLog(self, logname, dict_data):
        try:
            if dict_data is not None:
                if logname is not None:
                    new_logging = dict_data.get('logging')
                    new_loggers = new_logging.get('loggers')
                    isFound = False
                    logger_count = 0
                    defaultLoggerName = None
                    # log name Config Name을 지정한 이름으로 변경
                    for l in new_loggers:
                        if l is logname:
                            isFound = True
                            break
                        name = l.lower()
                        if name == "default":
                            defaultLoggerName = l
                        logger_count = logger_count + 1
                    if defaultLoggerName == None:
                        defaultLoggerName = l
                    if isFound:
                        logging.config.dictConfig(dict_data.get('logging'))
                    else:
                        if logger_count is 0:
                            self.logger = logging.getLogger(logname)
                            return True
                        changeLogger = {
                            logname: new_loggers.get(defaultLoggerName)}
                        new_loggers.update(changeLogger)
                        new_logging.update(new_loggers)
                        logging.config.dictConfig(new_logging)
                else:
                    logging.config.dictConfig(dict_data.get('logging'))
                self.logger = logging.getLogger(logname)

                if dict_data.get('kafka'):
                    self.AddKafkaLog(dict_data.get('kafka'))
            else:
                self.logger = logging.getLogger(logname)
            self.log_config = dict_data
            return True
        except Exception as e:
            print("OpenLog ERROR ", e, dict_data)
            import traceback
            print(traceback.format_exc())
            self.error = e
            return False

    def OpenLogFromJsonFile(self, logname, config_path):
        try:
            config = Config(
                data_type="json",
                file_class="file",
                config_datas=config_path)
            log_config = config.GetConfigData("LOG")
            self.OpenLog(logname, log_config)
            #config = json.load(open(config_path))
            # logging.config.dictConfig(config['LOG']['logging'])
            #self.logger = logging.getLogger(logname)

            # if config['LOG'].get('kafka'):
            #   self.AddKafkaLog(config['LOG'].get('kafka'))
            return True
        except Exception as e:
            self.error = e
            print("OpenLogFromJsonFile ERROR:", e)
            return False

    def OpenLogFromJsonString(self, logname, jsonstring):
        try:
            config = json.loads(jsonstring)
            #self.config_print(config)
            logging.config.dictConfig(config['LOG']['logging'])
            self.logger = logging.getLogger(logname)
            if config['LOG'].get('kafka'):
                self.AddKafkaLog(config['LOG'].get('kafka'))
            return True
        except Exception as e:
            self.error = e
            return False

    def AddKafkaLog(self, kwargs):
        try:
            topic = kwargs.get("topic")
            #host        = kwargs.get("bootstrap_servers")
            config = kwargs.get("kafka_config")
            host = config.get("bootstrap_servers")
            format_str = kwargs.get("format")
            # print(topic,config,format_str)
            self.kstream_hdl = KafkaHandler(topic, host)
            self.kstream_formatter = logging.Formatter(format_str)
            self.kstream_hdl.setFormatter(self.kstream_formatter)
            self.logger.addHandler(self.kstream_hdl)
            return True
        except Exception as e:
            self.error = e
            print("AddKafkaLog ERROR:", e)
            return False

    def record_log(self, kafka_msg):
        message = kafka_msg.value
        jsonlog = json.loads(message)
        jsonlog['level'] = jsonlog['levelno']
        record = logging.LogRecord(**jsonlog)
        if self.logger is None:
            print("LOGGER NONE")
        else:
            if record.levelname == "DEBUG":
                self.debug_log(
                    " [%s(%d)] %s %s",
                    jsonlog.get('name'),
                    jsonlog.get('process'),
                    jsonlog.get('asctime'),
                    jsonlog.get('message'))
            elif record.levelname == "INFO":
                self.info_log(
                    "\033[1;35m [%s\033[0;39m\033[0;35m(%d)\033[0;39m] %s %s",
                    jsonlog.get('name'),
                    jsonlog.get('process'),
                    jsonlog.get('asctime'),
                    jsonlog.get('message'))
            elif record.levelname == "ERROR":
                self.error_log(
                    "\033[1;31m [%s\033[0;39m\033[0;31m(%d)\033[0;39m] %s %s",
                    jsonlog.get('name'),
                    jsonlog.get('process'),
                    jsonlog.get('asctime'),
                    jsonlog.get('message'))
            elif record.levelname == "WARNING":
                self.warning_log(
                    "\033[1;33m [%s\033[0;39m\033[0;33m(%d)\033[0;39m] %s %s",
                    jsonlog.get('name'),
                    jsonlog.get('process'),
                    jsonlog.get('asctime'),
                    jsonlog.get('message'))
            elif record.levelname == "CRITICAL":
                self.critical_log(
                    " \033[1;31m[%s\033[0;39m\033[1;31m(%d)\033[0;39m] %s %s",
                    jsonlog.get('name'),
                    jsonlog.get('process'),
                    jsonlog.get('asctime'),
                    jsonlog.get('message'))

    def debug_log(self, _msg, *_args):
        if self.kstream_hdl is not None:
            msgstr = "IP(" + socket.gethostbyname(socket.getfqdn()) + ") "
            msgstr = msgstr + _msg.format(*_args)
        else:
            msgstr = _msg.format(*_args)

        lineno = inspect.stack()[1][1:3]
        msgstr = msgstr + " FILE=" + lineno[0] + ":" + str(lineno[1])

        if self.logger is not None:
            if self.user_prefix != None:
                self.logger.debug(msgstr,extra=self.user_prefix)
            else:
                self.logger.debug(msgstr)
        else:
            print("Not Exist Logger", _msg, *_args)

    def info_log(self, _msg, *_args):
        if self.kstream_hdl is not None:
            msgstr = "IP(" + socket.gethostbyname(socket.getfqdn()) + ") "
            msgstr = msgstr + _msg.format(*_args)
        else:
            msgstr = _msg.format(*_args)

        if self.logger is not None:
            if self.user_prefix != None:
                self.logger.info(msgstr,extra=self.user_prefix)
            else:
                self.logger.info(msgstr)
        else:
            print("Not Exist Logger", _msg, *_args)

    def warning_log(self, _msg, *_args):
        if self.kstream_hdl is not None:
            msgstr = "IP(" + socket.gethostbyname(socket.getfqdn()) + ") "
            msgstr = msgstr + _msg.format(*_args)
        else:
            msgstr = _msg.format(*_args)
        if self.logger is not None:
            if self.user_prefix != None:
                self.logger.warning(msgstr,extra=self.user_prefix)
            else:
                self.logger.warning(msgstr)
        else:
            print("Not Exist Logger", _msg, *_args)

    def error_log(self, _msg, *_args):
        if self.kstream_hdl is not None:
            msgstr = "IP(" + socket.gethostbyname(socket.getfqdn()) + ") "
            msgstr = msgstr + _msg.format(*_args)
        else:
            msgstr = _msg.format(*_args)
        lineno = inspect.stack()[1][1:3]
        msgstr = msgstr + " FILE=" + lineno[0] + ":" + str(lineno[1])
        if self.logger is not None:
            if self.user_prefix != None:
                self.logger.error(msgstr,extra=self.user_prefix)
            else:
                self.logger.error(msgstr)
        else:
            print("Not Exist Logger", _msg, *_args)

    def critical_log(self, _msg, *_args):
        if self.kstream_hdl is not None:
            msgstr = "IP(" + socket.gethostbyname(socket.getfqdn()) + ") "
            msgstr = msgstr + _msg.format(*_args)
        else:
            msgstr = _msg.format(*_args)
        lineno = inspect.stack()[1][1:3]
        msgstr = msgstr + " FILE=" + lineno[0] + ":" + str(lineno[1])
        if self.logger is not None:
            if self.user_prefix != None:
                self.logger.critical(msgstr,extra=self.user_prefix)
            else:
                self.logger.critical(msgstr)
        else:
            print("Not Exist Logger", _msg, *_args)
