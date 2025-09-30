import os, sys
import logging
from logging.handlers import RotatingFileHandler
import datetime
import boto3
import functools
from wasabi import Printer  # type: ignore[import]
from rich.logging import RichHandler


#https://github.com/explosion/wasabi
msg = Printer(timestamp=True)


def is_lambda():
    c1 = os.environ.get("LAMBDA_TASK_ROOT") is not None
    c2 = os.environ.get("AWS_EXECUTION_ENV") is not None
    c3 = os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None
    return c1 or c2 or c3


class SingletonType(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

def logme(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        msg.info(f'----> {f.__name__}')
        res = f(*args, **kwargs)
        msg.info(f' {f.__name__} <---')
        return res
    return wrapped

# 
class TenxLogger(object, metaclass=SingletonType):
    # __metaclass__ = SingletonType   # python 2 Style
    _logger = None

    def __new__(cls, *args, **kwargs):
        cls._logger = super(TenxLogger, cls).__new__(cls)
        return cls._logger
    
    def __init__(self, log_file_name, 
                        bucket_name="all-tenx-system-logs", 
                        dirname='./logs/',
                        s3_prefix='tenx-logs'):
        
        self._logger = logging.getLogger(log_file_name)
        self._logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s \t %(message)s')

        now = datetime.datetime.now()
        if is_lambda():
            dirname = os.path.join('/tmp', dirname)   

        if not os.path.isdir(dirname):
            os.mkdir(dirname)

        self.logger_file_name = log_file_name 
        self.log_file_path = dirname + "/{log_file_name}_" + now.strftime("%Y-%m-%d")+".log"
        fileHandler = RotatingFileHandler(self.log_file_path, maxBytes=10*1024*1024, backupCount=5)
        fileHandler.setLevel(logging.DEBUG)
        fileHandler.setFormatter(formatter) 
        
        streamHandler = logging.StreamHandler()

        fileHandler.setFormatter(formatter)
        streamHandler.setFormatter(formatter)

        self._logger.addHandler(fileHandler)
        self._logger.addHandler(streamHandler)
        self.msg = msg

        # Initialize S3 client
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name
        self.s3_prefix = s3_prefix        

    def logger(self):
        return self._logger
    
    def compose_log_message(self, *args, **kwargs):        
        message = ''
        if args:
            message = ', '.join([f"{x}" for x in args if isinstance(x, str)])
        if kwargs:
            message += ', '.join([f"{k}={v}" for k,v in kwargs.items() if isinstance(v, str)])

        return message  
    
    def _tmessage(self, *args, **kwargs):
        return self.compose_log_message(*args, **kwargs)

    def divider(self, message):
        self.msg.divider(self._tmessage(message))

    def success(self, message):
        self.msg.good(self._tmessage(message))    

    def good(self, message):
        self.msg.good(self._tmessage(message))     

    def ok(self, message):
        self.msg.info(self._tmessage(message))

    def fail(self, message):
        self.msg.fail(self._tmessage(message))          
          
    def okinfo(self, *args, **kwargs):
        message = self.compose_log_message(self, *args, **kwargs)
        self.msg.info(message)
        self.upload_to_s3(message, 'INFO')  

    def okwarn(self, *args, **kwargs):
        message = self.compose_log_message(self, *args, **kwargs)
        self.msg.warn(message)
        self.upload_to_s3(message, 'WARNING')  

    def info(self, *args, **kwargs):
        caller_line_number = sys._getframe(1).f_lineno        
        caller_filename = sys._getframe(1).f_code.co_filename
        caller_filename = caller_filename.split('/')[-1] if '/' in caller_filename else caller_filename      
        caller_func_name = sys._getframe(1).f_code.co_name

        #
        prefix = f"{caller_filename}:{caller_func_name}:{caller_line_number}"
        message = self.compose_log_message(self, *args, **kwargs)
        message = f"{message}"

        self.msg.info(message)
        self.upload_to_s3(message, 'INFO')  

    def warn(self, *args, **kwargs):
        caller_line_number = sys._getframe(1).f_lineno
        caller_filename = sys._getframe(1).f_code.co_filename
        caller_filename = caller_filename.split('/')[-1] if '/' in caller_filename else caller_filename    
        caller_func_name = sys._getframe(1).f_code.co_name
        
        #
        prefix = f"{caller_filename}:{caller_func_name}:{caller_line_number}"
        message = self.compose_log_message(self, *args, **kwargs)
        message = f"{message}"

        self.msg.warn(message)
        self.upload_to_s3(message, 'WARNING')                

    def error(self, *args, **kwargs):
        caller_line_number = sys._getframe(1).f_lineno
        caller_filename = sys._getframe(1).f_code.co_filename
        caller_filename = caller_filename.split('/')[-1] if '/' in caller_filename else caller_filename      
        caller_func_name = sys._getframe(1).f_code.co_name
        
        #
        prefix = f"{caller_filename}:{caller_func_name}:{caller_line_number}"
        message = self.compose_log_message(self, *args, **kwargs)
        message = f"{message} - {prefix}"

        self.msg.fail(message)
        self.upload_to_s3(message, 'ERROR')

    def log_info(self, *args, **kwargs):
        message = self.compose_log_message(self, *args, **kwargs)
        self.msg.info(message)

    def log_warning(self, *args, **kwargs):
        self.warn(*args, **kwargs)

    def log_error(self, *args, **kwargs):
        self.error(*args, **kwargs)


    def upload_to_s3(self, message, log_level):
        try:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            full_message = f"{self.logger_file_name}: {timestamp} - {message}"
            
            s3_key = f"{self.s3_prefix}/{log_level}/{self.logger_file_name}" if self.s3_prefix else self.logger_file_name
            self.s3_client.put_object(Bucket=self.bucket_name, Key=s3_key, Body=full_message.encode())
        except Exception as e:
            self.logger.warning(f"Failed to upload log to S3: {e}")
        pass
    

# Example usage:
if __name__ == "__main__":
    logger = TenxLogger("test.log", bucket_name="all-tenx-system-logs", s3_prefix='tenx-logs')
   
  
