import configparser
import sys
import os
import json
import yaml
from dict_util import MyDict

class Config:
    config = None
    error  = None
    def __init__(self,**kwargs):
        config_data_type = kwargs.get('data_type')
        if config_data_type == None:
            config_data_type = "json"
        config_file_type = kwargs.get('file_class')
        if config_file_type == None:
            config_file_type = "file"
        config_data      = kwargs.get('config_datas')
        print(config_data_type,config_file_type,config_data)
        try:
            self.config = MyDict()
            tmp = None
            if config_file_type == "file":
                self.config.LoadFile(config_data,config_data_type)
            elif config_file_type == "string":
                self.config.LoadString(config_data,config_data_type)
            else:
                return True

        except Exception as e:
            self.error = e
            print("Error(init):",e)
            return False

    def GetData(self):
        return self.config.data

    def GetError(self):
        return self.error

    def GetConfigData(self,*arg):
        _dot_str = self.config._change_dot(*arg)
        return  self.config.ReadData(_dot_str)

    def GetConfigObject(self,*arg):
        _dot_str = self.config._change_dot(*arg)
        return self.config.GetData(_dot_str)

    def SetConfigData(self,pos,value,isjson=False):
        if self.config.SetData(pos,value) == False:
            self.error = self.config.GetError()
            return False
        return True

    def AddConfigData(self,pos,value,isjson=False):
        if self.config.AddData(pos,value) == False:
            self.error = self.config.GetError()
            return False
        return True

    def WriteString(self,_format=None):
        return self.config.WriteString(_format)

    def PrintString(self,_format=None):
        print(self.config.WriteString(_format))

    def WriteFile(self,save_filename,_format=None):
        return self.config.WriteFile(save_filename,_format)

    def LoadFile(self,filename,_format=None):
        return self.config.LoadFile(filename,_format)

    def LoadString(self,_str_datas,_format=None):
        return self.config.LoadFile(_str_datas,_format)
