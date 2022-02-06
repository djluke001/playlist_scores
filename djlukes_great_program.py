import os
import json
import requests
import xlsxwriter
import math
#does not handle songs less the 13 notes 
uuid=76561198253114672
#playlist_list=['aa1.bplist','aa2.bplist','aa3.bplist','aa4.bplist','aa5.bplist'] #list of bplist file names(these will also be the names of the worksheets) #div aa
playlist_list=['a1.bplist','a2.bplist','a3.bplist','a4.bplist','a5.bplist']
Path= r"C:\Users\djluke\Desktop\leaderboardchecker"#working directory (bplist and xcel sheets will be in this folder )
get_canadian_playlist_data=False #whether to grab plylist data
get_player_data=True #whether to grab plyer data
#=(n-13)*8*1.19*115+5611






class leaderboard:
    def __init__(self, playlist_file_name):
        self.playlist=open(playlist_file_name)
        #self.playlist_content=self.playlist.read()
        self.data=json.load(self.playlist)
        self.dcd={'easy':1,'normal':3,'hard':5,'expert':7,'expertPlus':9,1:'easy',3:'normal',5:'hard',7:'expert',9:'expertPlus'}# dcd= difficulty converstion dictionary
        self.hash_difficultie_list=[]
        self.leaderboard_list=[]
        self.leaderboard_data=[]
    def grab_leaderboards(self):
        '''
        workbook = xlsxwriter.Workbook(Path+'\dataexport.xlsx')
        worksheet = workbook.add_worksheet()
        '''
        for i in self.data["songs"]:
            #print(i['hash'])
            #print(self.dcd[(i['difficulties'][0]['name'])])
            self.hash_difficultie_list.append([i['hash']   ,self.dcd[(i['difficulties'][0]['name'])]] )
            #print(self.hash_difficultie_list)
        iterator=-1
        for i in self.hash_difficultie_list:
            iterator+=1
            temp=[]
            data=requests.get('https://scoresaber.com/api/leaderboard/by-hash/'+i[0]+'/info?difficulty='+str(i[1])).json()
            #print(data['songName'])
            maxscore=self.get_maxscore(i[0],i[1])
            temp.append([data['songName'],maxscore])

            #print( temp)
            for g in range(13):
                scores=requests.get('https://scoresaber.com/api/leaderboard/by-hash/'+i[0]+'/scores?difficulty='+str(i[1])+'&countries=CA&page='+str(g+1)).json()
                try:
                    if scores['errorMessage']=='Scores not found':
                        break
                except:
                    pass#lazy fix for invalid entries
                #print(scores)
                #print("{'errorMessage': 'Scores not found'}")
                for f in scores['scores']:
                    temp.append([f['leaderboardPlayerInfo']['name'],f['modifiedScore'],f['timeSet'],f['id'],round(f['baseScore']/maxscore*100,2),f['modifiers'],f['fullCombo']])
            #print(temp)
            print("grabed "+str(iterator+1)+" of "+str(len(self.hash_difficultie_list))+" leaderboards")
            self.leaderboard_list.append(temp)
        '''
            for row in range(len(temp)):
                for col in range(len(temp[row])):
                    worksheet.write(row, col +8*iterator,temp[row][col])
                    '''

       


        #self.create_rankings(worksheet)

        #workbook.close()
        print("complete")







        #print(self.hash_difficultie_list )
    def create_rankings(self,worksheet):#this function only works for playlists of 6 songs
        #print("here")
        #print(self.leaderboard_list) 
        lists=[]
        for i in range(len(self.leaderboard_list)):
            for b in range(1,len(self.leaderboard_list[i])):
                if False==(self.leaderboard_list[i][b][0] in lists):
                    #print(self.leaderboard_list[i][b][0])
                    lists.append(self.leaderboard_list[i][b][0])
        list1=range(len(lists))
        for i in range(len(self.leaderboard_list)):
            worksheet.write(0,5*i+1,self.leaderboard_list[i][0][0])
            for b in range(1,len(self.leaderboard_list[i])):
                
                worksheet.write(lists.index(self.leaderboard_list[i][b][0])+1, 0,self.leaderboard_list[i][b][0])
                worksheet.write(lists.index(self.leaderboard_list[i][b][0])+1, 1 +5*i,self.leaderboard_list[i][b][1])
                worksheet.write(lists.index(self.leaderboard_list[i][b][0])+1, 2 +5*i,self.leaderboard_list[i][b][4])
                worksheet.write(lists.index(self.leaderboard_list[i][b][0])+1, 3 +5*i,self.leaderboard_list[i][b][6])           
                worksheet.write(lists.index(self.leaderboard_list[i][b][0])+1, 4 +5*i,self.leaderboard_list[i][b][2].split('T')[0])   
                
        

    def get_maxscore(self,hash,difficulty_num):

        data=requests.get('https://beatsaver.com/api/maps/hash/'+hash).json()
        for i in data['versions']:
            for diff in range(len(i['diffs'])):

                if i['diffs'][diff]['difficulty'].upper()== self.dcd[difficulty_num].upper():
                    self.id=data['id']
                    self.name=data['name']
                    self.nps_current=i['diffs'][diff]['njs']
                    self.njs_current=i['diffs'][diff]['nps']
                    self.notes_current=int(i['diffs'][diff]['notes'])
                    self.leaderboard_data.append([self.id,self.name,self.nps_current,self.njs_current,self.notes_current,self.dcd[difficulty_num].upper()])
                    return((int(i['diffs'][diff]['notes'])-13)*8*115+4715)
                    break


class playerdata:
    def __init__(self,uuid,amount_of_pages):
        self.dcd={'easy':1,'normal':3,'hard':5,'expert':7,'expertPlus':9,1:'easy',3:'normal',5:'hard',7:'expert',9:'expertPlus'}# dcd= difficulty converstion dictionary
        self.dataset=self.create_player_dataSet(uuid,amount_of_pages)
        
    def create_player_dataSet(self,uuid,amount_of_pages):
    
        temp_list=[]
        for i in range(amount_of_pages):
            data=requests.get('https://scoresaber.com/api/player/'+str(uuid)+'/scores?limit=100&sort=recent&page='+str(i+1)).json()
            print('grabbed page '+str(i))
            if 'errorMessage'in data:
                print([])
                break
            else:
                for b in range(len(data['playerScores'])):
                    #try:
                        #maxscore=self.get_maxscore(data['playerScores'][b]['leaderboard']['songHash'],data['playerScores'][b]['leaderboard']['difficulty']['difficulty'])
                    #except:
                        #self.nps_current='n/a'
                        #self.njs_current='n/a'
                        #self.notes_current='n/a'
                        #maxscore=100
                    temp_list.append([data['playerScores'][b]['leaderboard']['songHash'],data['playerScores'][b]['leaderboard']['songName'],data['playerScores'][b]['leaderboard']['songAuthorName'],data['playerScores'][b]['leaderboard']['levelAuthorName'],data['playerScores'][b]['score']['baseScore'],'placeholder',data['playerScores'][b]['score']['timeSet'].split("T")[0],data['playerScores'][b]['score']['pp'],data['playerScores'][b]['leaderboard']['stars'],data['playerScores'][b]['leaderboard']['difficulty']['difficulty'],'nps','njs','notes'])
        beatsaverdatalist=[]
        for x in range(math.ceil(len(temp_list)/50)):
            print('grabed beat saver data page '+str(x))
            hashlist=[]
            difflist=[]
            if len(temp_list)>(x+1)*50:
                var=50
            else: 
                var=len(temp_list)-(x)*50
            for y in range(var):
                hashlist.append(temp_list[(y+50*x)][0])
                difflist.append(temp_list[(y+50*x)][9])
            beatsaverdatalist.extend(self.get_beatsaverdata(hashlist,difflist))
        for i in range(len(temp_list)):
            #print(temp_list[i][4])
            #print(beatsaverdatalist[i][0])
            temp_list[i][5]=round((temp_list[i][4]/beatsaverdatalist[i][0]*100),2)
            temp_list[i][10]=beatsaverdatalist[i][1]
            temp_list[i][11]=beatsaverdatalist[i][2]
            temp_list[i][12]=beatsaverdatalist[i][3]
        for i in range(len(temp_list)):
            temp_list[i][9]=self.dcd[temp_list[i][9]]
        return(temp_list)


    #haslist=[hash,diff]
    def get_beatsaverdata(self,hashlist,difflist):
        #print('https://api.beatsaver.com/maps/hash/'+",".join(hashlist)) #documentation on scoresaber api swagger ui page is wrong use apostrophe for the call not %
        data=requests.get('https://api.beatsaver.com/maps/hash/'+",".join(hashlist)).json()
        templist=[]
        #print( hashlist)
        #print(difflist)
        iterator=-1 #iterator needed to fix issue where .index chooses first index wich might not necessarly be correct
        for i in hashlist:
            iterator+=1
            #print(data) #scoresabe uses uppercase hash beatsaver uses lowercase
            try:
                for g in data[i.lower()]['versions']:
                    
                    for diff in range(len(g['diffs'])):

                        if g['diffs'][diff]['difficulty'].upper()== self.dcd[difflist[ iterator]].upper():
                            self.nps_current=g['diffs'][diff]['njs']
                            self.njs_current=g['diffs'][diff]['nps']
                            self.notes_current=int(g['diffs'][diff]['notes'])
                            maxscore=((int(g['diffs'][diff]['notes'])-13)*8*115+4715)
                            break
                templist.append([maxscore,self.nps_current,self.njs_current,self.notes_current])
            except:
                templist.append([1,'null','null','null'])
            #print(i)
        return(templist)

    
#print(Path)
if get_canadian_playlist_data:
    workbook = xlsxwriter.Workbook(Path+'\playlistdata.xlsx')

    data_info=[]
    for i in playlist_list:
        worksheet = workbook.add_worksheet(str(i))

        x=leaderboard((Path +'\\'+ i))
        x.grab_leaderboards()
        #print(x.leaderboard_list)
        x.create_rankings(worksheet)
        data_info.append(x.leaderboard_data)
    #print(x.get_maxscore('0CA00077668E64F2382EAECAA43C1CA0459AA2C5',7))
    worksheet=workbook.add_worksheet("song info")
    iterator=0
    worksheet.write(iterator,0,'id')
    worksheet.write(iterator,1,'name')
    worksheet.write(iterator,2,'njs')
    worksheet.write(iterator,3,'nps')
    worksheet.write(iterator,4,'notes')
    worksheet.write(iterator,5,'diff')
    iterator+=1
    for i in data_info:
        
        for f in i:
            worksheet.write(iterator,0,f[0])
            worksheet.write(iterator,1,f[1])
            worksheet.write(iterator,2,f[2])
            worksheet.write(iterator,3,f[3])
            worksheet.write(iterator,4,f[4])
            worksheet.write(iterator,5,f[5])
            iterator+=1
        iterator+=2

    workbook.close()
if get_player_data:#lazymans testing switch
    djluke=playerdata(uuid,100)

    workbook = xlsxwriter.Workbook(Path+'\playersheet.xlsx')
    worksheet = workbook.add_worksheet()
    templist=djluke.dataset
    worksheet.write(0, 0,'hash')
    worksheet.write(0, 1,'songname')
    worksheet.write(0, 2,'artist')
    worksheet.write(0, 3,'mapper')
    worksheet.write(0, 4,'score')
    worksheet.write(0, 5,'percent')
    worksheet.write(0, 6,'date')
    worksheet.write(0, 7,'pp')
    worksheet.write(0, 8,'stars')
    worksheet.write(0, 9,'diff')
    worksheet.write(0, 10,'NPS')
    worksheet.write(0, 11,'NJS')
    worksheet.write(0, 12,'notes')

    for i in templist:
        for t in range(13):
            worksheet.write(templist.index(i)+1, t,i[t])
            
    workbook.close()