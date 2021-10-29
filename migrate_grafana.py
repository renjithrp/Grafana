#!/usr/bin/env python
import requests
import json
import sys
import os

def __main__():
    
    d = grafana()
    d.validate()
    d.createds()
    d.dashboards(overwrite=False)
        
class api:
    
    def __init__(self,url,auth):
        
        self.url = url
        self.auth = auth
        self.headers = {
                'Content-type': 'application/json',
                'Authorization':'Bearer ' + auth 
              }
    
    def get(self):
        
        r = requests.get(self.url,headers=self.headers)
        j = json.loads(r.text)
        return j
    
    def post(self,data):
        
        self.data = data
        r = requests.post(self.url, data=self.data,headers=self.headers)
        j = json.loads(r.text)
        return j
                               
                
class grafana:
    
    def __init__(self):
    
        envList = ['SOURCE_GRAFANA_URL', 'SOURCE_GRAFANA_KEY', 'DEST_GRAFANA_URL', 'DEST_GRAFANA_KEY']
        error = []
        
        def check(error,env):
            if os.getenv(env, None) is None:
                print("%s is not defined" %(env))
                error.append(env)
        
        for env in envList : 
            check(error,env)
            
        if len(error) != 0:
            sys.exit() 
            
        else:
            self.sourceUrl = os.environ['SOURCE_GRAFANA_URL']
            self.sourceAuth = os.environ['SOURCE_GRAFANA_KEY']
            self.destUrl = os.environ['DEST_GRAFANA_URL']
            self.destAuth = os.environ['DEST_GRAFANA_KEY']
        
    def validate(self):
        
        orgApi = '/api/org/'
        sourceUrl = self.sourceUrl + orgApi
        destUrl = self.destUrl + orgApi
        
        try:
            r = api(sourceUrl,self.sourceAuth)
            org = r.get()
            if org['name']:
                print("Validating %s : Success" %(self.sourceUrl))
                
        except:
            print("Validating %s : Failed" %(self.sourceUrl))
            sys.exit()
        
        try:
            r = api(destUrl,self.destAuth)
            org = r.get() 
            if org['name']:
                print("Validating %s : Success" %(self.destUrl))
        except:
            print("Validating %s : Failed" %(self.destUrl))
            sys.exit()

            
    def createds(self):
        
        dsApi = '/api/datasources'
        sourceUrl = self.sourceUrl + dsApi
        
        r = api(sourceUrl,self.sourceAuth)
        
        for sds in r.get():
            destUrl = self.destUrl + dsApi + '/name/' + sds['name']
            r = api(destUrl,self.destAuth)
            ds = r.get()
            
            try:
                print("Datasource %s exists" %(ds['name']))
                
            except:
                
                r = api(self.destUrl,self.destAuth)
                res = r.post(json.dumps(sds))
                print(res['message'])
                
    def dashboards(self,**flag):
        
        searchApi = '/api/search?folderIds=0'
        sourceUrl = self.sourceUrl + searchApi
        
        r = api(sourceUrl,self.sourceAuth)
        
        def getUid(title,url,auth):
            
            searchApi = '/api/search?query=' + title
            url = url + searchApi
            r = api(url,auth)
            
            for dash in r.get():
                if str(title) == dash['title']:
                    return dash['uid']
        
        for sDash in r.get():
            
            destUid = getUid(sDash['title'],self.destUrl,self.destAuth)
            
            dashApi = '/api/dashboards/uid/' + destUid
            postApi = '/api/dashboards/db'
            
            sourceUrl = self.sourceUrl + dashApi
            r = api(sourceUrl,self.sourceAuth)
            sourceDash = r.get()
            
            destUrl = self.destUrl + dashApi
            r = api(destUrl,self.destAuth)
            destDash = r.get()
            
            
            try:
                flag['overwrite']
                
            except:
                flag['overwrite'] = False
         
            try:
                if destDash['dashboard']:
                    
                    if flag['overwrite'] is True :
                        
                         sourceDash['dashboard']['overwrite'] = 'true'
                         sourceDash['dashboard']['id'] = destDash['dashboard']['id']
                         sourceDash['dashboard']['version'] = destDash['dashboard']['version']
                         sourceDash['dashboard']['uid'] = destUid
                         postUrl = self.destUrl + postApi
                         r = api(postUrl,self.destAuth)
                         res = r.post(json.dumps(sourceDash))  

                         print("Dashboard %s : updated" %(res['slug']))
                            
                    else:
                        print("Dashboard %s : exists" %(destDash['dashboard']['title']))   

            except:
                 sourceDash['dashboard']['id'] = None
                 sourceDash['dashboard']['uid'] = destUid
                 postUrl = self.destUrl + postApi
                 r = api(postUrl,self.destAuth)
                 res = r.post(json.dumps(sourceDash))
                 print("Dashboard %s : created " %(res['slug']))         
                
__main__()




