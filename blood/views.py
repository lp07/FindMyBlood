
import smtplib
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

import pickle
import numpy as np
from datetime import date


from .utils import distance

import matplotlib.pyplot as plt


import firebase_admin
from firebase_admin import credentials, storage
from firebase_admin import db


import cv2
import os.path

import math, random


cred = credentials.Certificate("static/data/blood-ed205-firebase-adminsdk-eqmtk-cd30934137.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://blood-ed205-default-rtdb.firebaseio.com',
    'storageBucket': 'blood-ed205.appspot.com'
})


def loader(request):
    return render(request,'loader.html')


def index(request):
    

    # ref = db.reference('/users/')
    # users = ref.get()
    # print(users)
    # #print(type(ref.get()))
    # # ref.update({'user2':{'bloodgroup': 'A+', 'location': '(230,430)', 'name': 'kumar', 'password': 'pass123'}})
    # ref.update({'user1':{'bloodgroup': 'A+', 'location': '(230,430)', 'email': 'rahul@gmail.com', 'password': 'pass123'}})
    
    return render(request,'index.html')


@csrf_exempt
def signup(request):

    if request.method == 'POST':
        typeval = request.POST.get('type')

        if(typeval == 'donor'):
            return render(request, 'signup.html',{'n' : range(18,99),'donor':1 })
        else:
            return render(request, 'signup.html',{'n' : range(18,99), 'rec':1 })
    
    # return render(request, 'signup.html',{'n' : range(18,99) })



@csrf_exempt
def signupworker(request):

    if request.method == 'POST':


        email = request.POST.get('email')
        password = request.POST.get('password')
        name = request.POST.get('name')
        lat = request.POST.get('lat')
        longi = request.POST.get('long')
        group = request.POST.get('group')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        DOB = request.POST.get('age')
        utype = request.POST.get('type')
        
        age = calculateAge(DOB)

        dic = {'bloodgroup' : group, 'location':'('+lat+','+longi+')', 'name':name, 'email':email, 'password':password, 'phone':phone, 'gender':gender,'age':age,'type':utype,'DOB':DOB}

        ref = db.reference('/users/')
        users = ref.get()
        for i in users:
            if(users[i]['email'] == email):
                return render(request,'index.html',{'emailalready': 1})


        userind = int(list(sorted(list(ref.get()))[-1])[-1]) + 1
        dic['id'] = userind
        if request.POST.get('radio1'):
            r1 = request.POST.get('radio1')
            r2 = request.POST.get('radio2')
            r3 = request.POST.get('radio3')
            r4 = request.POST.get('radio4')

            if(r1=='1' and r2=='0' and r3=='0' and r4=='0'):
                dic['lastdonated'] = 'NA'
                dic['requests'] = {"request1":{'date':"1",'from':"1",'recid':"1",'id':"1","accepted":"false"}}
                
                
                ref.update({'user'+str(userind): dic})
                return render(request,'index.html',{'signuptoken': 1})
            else:
                return render(request,'index.html',{'signupfailure': 1})
        else:
            
            dic['history'] = {"history1":{'date':"1",'from':"1",'donid':"1",'id':"1","accepted":"false"}}
            
            print(email, password, name, lat, longi, group)
            ref.update({'user'+str(userind): dic})
            #ref.update({str(email): dic})
            return render(request,'index.html',{'signuptoken': 1})


        
 
        

@csrf_exempt
def signin(request):   

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        ref = db.reference('/users/')
        users = ref.get()
        # print(users)
        # print("######",email,password)

        for i in users:
            if(users[i]['email'] == email and users[i]['password'] == password):
                return home(request,users[i])
                #return redirect('home',users[i])
        
        return render(request,'index.html',{'error':1})
        




@csrf_exempt
def donorlist(request):

    if request.method == 'POST':
        group = request.POST.get('group')
        print("session user")
        print(request.session['user'])
        uloc = np.array(list(map(float, request.session['user']['location'].strip('()').split(','))))
        ref = db.reference('/users/')
        donors = ref.get()
        dist = []
        reqdoner = []
        for i in donors:
            if donors[i]['bloodgroup'] == group and donors[i]['type']=='Donor':
                print('found')
                dloc = np.array(list(map(float, donors[i]['location'].strip('()').split(','))))
                dist.append(distance(uloc[0],dloc[0],uloc[1],dloc[1]))
                reqdoner.append(donors[i])


        donordist = zip(dist,reqdoner)
        donordist = sorted(donordist, key=lambda x: x[0])
        print(donordist)
        

        return render(request,'donorlist.html',{'donorlist':donordist,'user':request.session['user']})


def home(request,user):

    
    utype = user['type']
    if utype=="Reciever":
        history = [user['history'][i] for i in user['history']][1:]
    else:
        history = [user['requests'][i] for i in user['requests']][1:]
    request.session['user'] = user
    # print(history)
    #add image

    if os.path.exists('static/uploads/'+str(request.session['user']['id'])+'.png'):
        return render(request,'home.html',{'user':user,'history':history,'pic':1})
    else:
        return render(request,'home.html',{'user':user,'history':history})


    


@csrf_exempt
def sendrequest(request):

    if request.method == 'POST':

        recid = request.POST.get('requesterid')
        recname = request.POST.get('requestername')
        donorname = request.POST.get('donorname')
        donid = request.POST.get('donorid')
        print(recid,donid)
        date = datetime.today().strftime('%m/%d/%Y')

        ref = db.reference('/users/user'+str(donid)+"/requests/")
        dbref = ref.get()
        exists = 0
        for i in dbref:
            # print(dbref[i])
            
            if dbref[i]['from'] == recname:
                exists = 1
        if exists == 0:
            reqind = int(list(sorted(list(ref.get()))[-1])[-1]) + 1
            dic = {'date':date,'from':recname,'recid':recid,'id':reqind,'accepted':"false"}
            ref.update({'request'+str(reqind): dic})
        # print(ref.get(),histind)
        

        ref = db.reference('/users/user'+str(recid)+"/history/")
        dbref = ref.get()
        exists = 0

        for i in dbref:
            # print(dbref[i])
            if dbref[i]['from'] == donorname:
                exists = 1
        if exists == 0:
            histind = int(list(sorted(list(ref.get()))[-1])[-1]) + 1
            dic = {'date':date,'from':donorname,'donid':donid,'id':histind,'accepted':"false"}
            ref.update({'history'+str(histind): dic})


    return HttpResponse()



@csrf_exempt
def handle_uploaded_file(f):
    
    print(f)


@csrf_exempt
def upload(request):


    if request.method == 'POST':

        img = cv2.imdecode(np.fromstring(request.FILES['files[]'].read(), np.uint8), cv2.IMREAD_UNCHANGED)
        cv2.imwrite('static/uploads/'+str(request.session['user']['id'])+'.png',img)
       
        
        
            

    return home(request,request.session['user'])


@csrf_exempt
def acceptrequest(request):

    if request.method == 'POST':

        reqid = request.POST.get('reqid')
        uid = request.POST.get('uid')

        
        ref = db.reference('/users/user'+str(uid)+"/requests/")
        dbref = ref.get()
        
        ref.child("request"+str(reqid)).update({"accepted":"true"})
        
        recid = dbref["request"+str(reqid)]['recid']
        print(recid)
        # ref = db.reference('/users/user'+str(recid)+"/history/")
        ref = db.reference('/users/user'+str(recid)+"/history/")
        dbref = ref.get()
        
        for i in dbref:
            if(dbref[i]['from'] == request.session['user']['name'] ):
                histid = dbref[i]['id']
                ref.child("history"+str(histid)).update({"accepted":"true"})


        ref = db.reference('/users/')
        users = ref.get()
        refreshed_user = users['user'+uid]
        request.session['user'] = refreshed_user

    return home(request,refreshed_user)

def calculateAge(birthDate):
    s = [int(i) for i in birthDate.split('-')]
    birthDate = date(s[0],s[1],s[2])
    today = date.today()
    age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))
 
    return age

@csrf_exempt
def forgot(request):
    if request.method == 'POST':

        email = request.POST.get('email')
        digits = "0123456789"
        OTP = ""
        for i in range(4) :
            OTP += digits[math.floor(random.random() * 10)]
        print(OTP)

        s = smtplib.SMTP('smtp-mail.outlook.com', 587)
        s.starttls()
        emailpass = "Blood@123"
        s.login("findmyblood@outlook.com", emailpass )
        subject = "Forgot My Password"
        body = "Your OTP for changing your password is : "+OTP
        msg = f'Subject: {subject}\n\n{body}'
        s.sendmail("findmyblood@outlook.com",email,msg=msg)
        
        return render(request,'forgot.html',{'otp':OTP,'email':email})
    else:
        return render(request,'forgot.html')


@csrf_exempt
def valforgot(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('pass')

        ref = db.reference('/users/')
        users = ref.get()
        # print(users)
        # print("######",email,password)

        for i in users:
            
            if(users[i]['email'] == email):
                ref.child(i).update({'password':new_password})


    return render(request,'index.html',{'passchange': 1})
