import sys
import os
import json
import yaml

class MyDict:
    data    =   None
    error   =   None
    def __init__(self,keys=None, value=None):
        try:
            if keys != None:
                self.data = dict({keys: value})
            else:
                self.data = dict()
        except Exception as e:
            self.error = e

    # Error 정보
    def GetError(self):
        return self.error

    # Dictionary Clear
    def Clear(self):
        if self.data != None:
            self.data.clear()
            self.data = None

    # ex)dictdata= {
    #       "game_id": "123456",
    #       "golf": {
    #           "ordering": {
    #               "id": 1,
    #               "desc": "white ball"
    #           }
    #       }
    #     }
    # Root Dictionary keys
    # return list
    # GetKeys() ==> ['game_id', 'golf']
    def GetKeys(self,keys=None):
        if self.data != None:
            if keys == None:
                return list(self.data.keys())
            else:
                key,result = self.GetData(keys)
                if result == None:
                    return None
                if isinstance(result, dict):
                    return list(result.keys())
                else:
                    #print("None 1",type(result),result)
                    return None

        return None

    def GetKeysExt(self,keys):
        try:
            temp = self.data
            if keys == None:
                return list(self.data.keys())
            count,klist = self._get_split(keys,".")
            for k in klist:
                index = self._get_list_index(k)
                if index != -1:
                    if isinstance(temp, list):
                        if isinstance(temp[index], dict):
                            if k == klist[count-1]:
                                return list(temp.keys())
                            else:
                                temp = temp[index]
                        else:
                            if k == klist[count-1]:
                                return temp[index]
                            else:
                                print("DATA",temp)
                                return None
                    else:
                        return None
                else:
                    temp = self._exist_data(k,temp)
                if temp is None:
                    return temp
            if isinstance(temp,dict):
                return list(temp.keys())
            else:
                return None
        except Exception as e:
            #print(e)
            self.error = e
            return None
    # Root Dictionary values
    # return list
    # GetValues() ==> ['ordering': {'id': 1, 'desc': 'white ball'}}]
    def GetValues(self):
        if self.data != None:
            return self.data.values()
        return None

    # Get Root Dictionary
    # return dict
    def GetDictionary(self):
        return self.data

    # Set Root Dictionay
    # 이미 존재 할 경우 덮어 쓴다.
    def SetDictionary(self,dictdata):
        if self.data != None:
            self.Clear()
        self.data = dictdata

    # split function
    # return 갯수, 스프릿된 문자열
    # strdata = "company.team.part"
    # _get_split(strdata,".") ==> 3, ['company','team','part']
    def _get_split(self,div_str,keywords):
        str_list = None
        count    = 0
        try:
            str_list = div_str.split(keywords)
            count = len(str_list)
            return count,str_list
        except Exception as e:
            self.error = e
            return count,str_list

    def _get_list_index(self,keys):
        try:
            conv_key = keys.split("{")
            if len(conv_key) == 1:
                return -1
            conv_key = conv_key[1].split("}")
            return int(conv_key[0])
        except Exception as e:
            self.error = e
            return -1

    # dictionay에 key가 존재하는 판단
    # _exist_data("game_id",dictdata) ==>  "123456"
    # _exist_data("name",dictdata) ==> None
    def _exist_data(self,key,dictdata):
        try:
            return dictdata[key]
        except Exception as e:
            return None

    # mydict에 데이터 추가
    # 이미 존재할 경우 False ==> 값 변경시에는 SetData() 사용
    # 성공할 경우 True

    def new_data(self,key,value):
        try:
            data = dict({key:value})
            return data
        except Exception as e:
            print(e)
            return None
    def update_data(self,src,key,value):
        try:
            src.update({key:value})
            return True
        except Exception as e:
            print(e)
            return False


    def AddData(self,arg_keys,value,_source=None):
        try:
            #print("\n",arg_keys,"\n")
            if _source is None and self.IsExist(arg_keys) == True:
                #print("exist",arg_keys,value)
                return False
            count , klist = self._get_split(arg_keys,".")
            subkeys_idx = arg_keys.find(".")

            dataptr = self.data
            for idx,key in enumerate(klist):
                # 현재 key의 데이터 타입
                curr_type = self._get_list_index(key)
                if idx < count-1:
                    next_type = self._get_list_index(klist[idx+1])
                else:
                    next_type = -2

                #print(idx,"===>",key,count)
                #print("[START]",idx,"===>",key,curr_type,next_type)
                ## dictionary 인 경우 key가 존재하는지 확인
                if curr_type == -1:
                    #print("\t",idx,"    [1.1.데이터",dataptr)
                    if key not in dataptr:
                        #print("\t",idx,"    [1.키가 없다]",key,dataptr)
                        dataptr.update({key:None})
                    data = dataptr.get(key)
                    if data is None:
                        #print("\t",idx,"    [2.추가해야 딘다.] next",next_type)
                        if next_type > -1:
                            listdata = list()
                            dataptr.update({key:listdata})
                            #print("\t","DATA",dataptr)
                            dataptr = listdata
                            #print("\t",idx,"    [3.리스트 데이터 추가]",next_type)
                        else:
                            if idx == count-1:
                                #print("\t",idx,"    [4.데이터 추가] ",key,value)
                                dataptr.update({key:value})
                            else:
                                data = dict()
                                dataptr.update({key:data})
                                #print("\t",idx,"    [4-1.데이터 추가] ",key,value)
                                dataptr = data
                    else:
                        #print("\t",idx,"    [5.하위 데이터를 찾아 인서트] ",key,value,data)
                        if isinstance(data,list):
                            # 데이터가 list이면 추가한다.
                            if idx == count-1:
                                data.append(value)
                            else:
                                dataptr = data
                        elif isinstance(data,dict):
                            #print("\t",idx,"    [5-1.하위 데이터를 찾아 인서트] ",count-1)
                            if idx == count -1:
                                #print("\t",idx,"    [5-1-1.하위 데이터를 찾아 변경] ",count-1)
                                datatptr.update({key:value})
                            else:
                                #print("\t",key,klist[idx+1],"DATA",data)
                                #print("\t",idx,"    [5-1-2.하위 데이터를 찾아 변경] ")
                                        #,count-1,klist[idx+1],data[klist[idx+1]])
                                if klist[idx+1] in data:
                                    dataptr = data
                                    #print("\t\t존재",data)
                                else:
                                    dataptr = data
                else:
                    #print("\t","DATAPTR",dataptr,"길이",len(dataptr),curr_type)
                    if len(dataptr)-1 >= curr_type:
                        #print("\t","index에서 데이터를 찾는다 ",dataptr,len(dataptr),curr_type)
                        dataptr = dataptr[curr_type]
                    else:
                        if idx == count -1:
                            #print("\t","마지막 데이터 추가",dataptr,len(dataptr),curr_type)
                            dataptr.append(value)
                        else:
                            data = dict()
                            #print("\t","다음 딕셔너리에 추가 ",dataptr,len(dataptr),curr_type)
                            dataptr.append(data)
                            dataptr = data
            return True

        except Exception as e:
            self.error = e
            #print(e)
            return False


    # mydict에 데이터 추가
    # 이미 존재할 경우 False ==> 값 변경시에는 SetData() 사용
    # 성공할 경우 True
    def RemoveItem(self,keys):
        try:
            prev = None
            if self.IsExist(keys) == False:
                return True
            count,klist = self._get_split(keys,".")
            temp = self.data
            lastkey = klist[count-1]
            for k in klist:
                index = self._get_list_index(k)
                #print(k,index,type(temp),temp)
                if k == lastkey:
                    if temp == None:
                        temp = prev
                    if isinstance(temp, list):
                        del(temp[index])
                    else:
                        temp.pop(lastkey)
                if index != -1:
                    temp = temp[index]
                prev = temp
                temp = self._exist_data(k,temp)
            return True
        except Exception as e:
            self.error = e
            print(e)
            return False

    # mydict에 데이터값 변경
    # key가 존재할 경우 값 변경
    # 존재하지 않을 경우 False ==> 새로 입력 할 경우 AddData() 사용
    def SetData(self,keys,value):
        index = 0
        try:
            if self.IsExist(keys) == False:
                return False
            count,klist = self._get_split(keys,".")
            temp = self.data
            for k in klist:
                prev = temp
                index = self._get_list_index(k)
                if index != -1:
                    if isinstance(temp, list):
                        if isinstance(temp[index], dict):
                            if k == klist[count-1]:
                                break
                            else:
                                temp = temp[index]
                        else:
                            if k == klist[count-1]:
                                break;
                            else:
                                return False
                    else:
                        return False
                else:
                    temp = self._exist_data(k,temp)
                if temp is None:
                    prev.update({k:dict()})
                    temp = prev[k]
            if isinstance(prev,dict):
                if isinstance(value, MyDict):
                    prev.update({k:value.GetDictionary()})
                else:
                    prev.update({k:value})
            elif isinstance(prev,list):
                prev[index] = value

            return True
        except Exception as e:
            self.error = e
            #print(e)
            return False

    # mydict에서 key에 해당하는 값을 가져온다.
    # 반환 값: key, value
    # 하위 계층까지 찾을 경우 "."으로 계층 구조를 표현
    # GetData("golf.ordering.id") ==> id, 1
    # 해당되는 key가 존재하지 않을 경우 None
    def GetData(self,keys):
        try:
            temp = self.data
            count,klist = self._get_split(keys,".")
            for k in klist:
                index = self._get_list_index(k)
                if index != -1:
                    if isinstance(temp, list):
                        if isinstance(temp[index], dict):
                            if k == klist[count-1]:
                                #return klist[count-2]+"."+k,temp
                                return keys,temp
                            else:
                                temp = temp[index]
                        else:
                            if k == klist[count-1]:
                                return keys,temp[index]
                            else:
                                return None,None
                    else:
                        return None,None
                else:
                    temp = self._exist_data(k,temp)
                if temp is None:
                    return keys,temp
            return keys,temp
        except Exception as e:
            #print(e)
            self.error = e
            return None,None

    def ReadData(self,keys):
        try:
            temp = self.data
            count,klist = self._get_split(keys,".")
            for k in klist:
                index = self._get_list_index(k)
                if index != -1:
                    if isinstance(temp, list):
                        if isinstance(temp[index], dict):
                            if k == klist[count-1]:
                                #return klist[count-2]+"."+k,temp
                                return temp
                            else:
                                temp = temp[index]
                        else:
                            if k == klist[count-1]:
                                return temp[index]
                            else:
                                return None
                    else:
                        return None
                else:
                    temp = self._exist_data(k,temp)
                if temp is None:
                    return temp
            return temp
        except Exception as e:
            #print(e)
            self.error = e
            return None
    # 데이터가 존재하는지 확인
    # 존재할 경우 True, 없을 경우 False
    def IsExist(self,keys):
        try:
            temp = self.data
            count,klist = self._get_split(keys,".")
            for k in klist:
                index = self._get_list_index(k)
                if index != -1:
                    if isinstance(temp, list):
                        if isinstance(temp[index], dict):
                            if k == klist[count-1]:
                                return True
                            else:
                                temp = temp[index]
                        else:
                            if k == klist[count-1]:
                                return True
                            else:
                                return False
                    else:
                        return False
                else:
                    temp = self._exist_data(k,temp)
                if temp is None:
                    return False
            return True
        except Exception as e:
            self.error = e
            return False

    def MoveData(self,source,target):
        try:
            key,data = self.GetData(source)
            if data == None:
                return False
            if self.RemoveItem(source) == False:
                return False
            return self.AddData(target,data)
        except Exception as e:
            self.error = e
            return False


    # json stream 데이터를 dictionary로 변환
    def LoadJsonString(self, json_string):
        try:
            self.data = json.loads(json_string)
            return True
        except Exception as e:
            self.error = e
            return False

    # json 파일을 로드하여  dictionary로 변환
    def LoadJsonFile(self, json_filename):
        try:
            with open(json_filename) as json_file:
                self.data = json.load(json_file)
                return True
        except Exception as e:
            self.error = e
            return False

    # dictionary를 json stream으로 변환
    def WriteJsonString(self,val=4):
        try:
            return json.dumps(self.data, ensure_ascii=False, indent=val)
        except Exception as e:
            self.error = e
            print(e)
            return False

    # dictionary를 json File으로 변환
    def WriteJsonFile(self,savefile):
        try:
            with open(savefile, 'w') as f:
                json.dump(self.data,f,ensure_ascii=False,indent=4)
            return True
        except Exception as e:
            self.error = e
            print(e)
            return False

    # yaml 파일을 로드하여  dictionary로 변환
    def LoadYamlFile(self, yaml_filename):
        try:
            with open(yaml_filename) as yaml_file:
                self.data = yaml.safe_load(yaml_file)
                return True
        except Exception as e:
            self.error = e
            return False

    # yaml stream 데이터를 dictionary로 변환
    def LoadYamlString(self, yaml_string):
        try:
            self.data = yaml.safe_load(yaml_string)
            return True
        except Exception as e:
            self.error = e
            return False

    # dictionary를 yaml stream으로 변환
    def WriteYamlString(self):
        try:
            return json.dumps(self.dictdata, indent=4)
        except Exception as e:
            self.error = e
            return False
    # dictionary를 yaml File으로 변환
    def WriteYamlFile(self,savefile):
        try:
            with open(savefile, 'w') as f:
                yaml.dump(self.data,f)
            return True
        except Exception as e:
            self.error = e
            print(e)
            return False

    # json/yaml 파일을 로드하여 dict로 변환
    def LoadFile(self,load_filename,_format):
        if _format == None:
            return False
        datatypes = str(_format).lower()
        if datatypes == "json":
            return self.LoadJsonFile(load_filename)
        elif datatypes == "yaml":
            return self.LoadYamlFile(load_filename)
        else:
            return False

    # stream 데이터를 로드하여 dict로 변환
    def LoadString(self,_str_datas,_format):
        datatypes = str(_format).lower()
        if datatypes == "json":
            return self.LoadJsonString(_str_datas)
        elif datatypes == "yaml":
            return self.LoadYamlString(_str_datas)
        else:
            return False


    def WriteFile(self,save_filename,_format):
        if _format == None:
            return self.WriteJsonFile(save_filename)
        datatypes = str(_format).lower()
        if datatypes == "json":
            return self.WriteJsonFile(save_filename)
        elif datatypes == "yaml":
            return self.self.WriteYamlFile(save_filename)
        else:
            return self.WriteJsonFile(save_filename)

    def WriteString(self,_format=None):
        if _format == None:
            return self.WriteJsonString()
        datatypes = str(_format).lower()
        if datatypes == "json":
            return self.WriteJsonString()
        elif datatypes == "yaml":
            return self.WriteYamlString()
        else:
            return self.WriteJsonString()

    def _change_dot(self,*args):
        _arg_str = str(args)
        count,arglist = self._get_split(_arg_str,".")
        if count != 1:
            _arg_str = args[0]
        else:
            _arg_str = _arg_str.replace("(","")
            _arg_str = _arg_str.replace("'","")
            _arg_str = _arg_str.replace("\"","")
            _arg_str = _arg_str.replace(")","")
            _arg_str = _arg_str.replace(", ",".")
            _arg_str = _arg_str.replace(",","")
        return _arg_str

