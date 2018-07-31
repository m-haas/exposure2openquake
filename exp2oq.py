#from the census file create an exposure model with specified building types
#and create vulnerability class distribution for each building type

#import psycopg2
#import ppygis
import csv
import math

#database things
#db_conn='host=localhost user=postgres password=postgres dbname=deserve'

#conn = psycopg2.connect(db_conn)
#cur = conn.cursor()


#taxonomy:
#Country iso - EMS98 type - Height - Precode - RC Frame Masonry infill - Old Stone - PSE since 68 - Height
#ISO-EMS98-PC-RCM-Old-PSE68-H

#############################################
# Taxonomy
#############################################

def taxonomy(row,height,year):
    '''
    Creates a taxonomy string from the census row,pc,pse68, height info(LMH)
    '''
    iso=row[0]
    #things fixed by iso
    if iso=='JOR':
        descr = row[2]
        pc = precode(year)
        pse68 = False
        old = False
    elif iso=='PSE':
        descr = row[3]
        pc = True
        pse68 = palestine68(year)
        old = old_mat(descr)
    else:
        print 'unknown iso'

    main = EMS98_bt(descr,iso)
    RCM = masonry_infill(descr)
    height = height
    HR = high_rise(height)
    #iso string, EMS98 type string, height int,precode boolean, RC frame masonry infill boolean, old stone boolean,pse68 boolean,high rise boolean
    return [iso,main,height,pc,RCM,old,pse68,HR]

def tax_str(tax):
    '''
    Turns taxonomy list in taxonomy string
    '''
    #iso string, EMS98 type string, height int,precode boolean, RC frame masonry infill boolean, old stone boolean,pse68 boolean,high rise boolean
    return '{}-{}-{}-{}-{}-{}-{}-{}'.format(tax[0],tax[1],str(tax[2]),str(tax[3])[0],str(tax[4])[0],str(tax[5])[0],str(tax[6])[0],str(tax[7])[0])

def EMS98_bt(description,iso):
    '''
    Return EMS98 building type string depending on description
    '''
    bt_map =  {'JOR':{
                      'Cement Bricks':'MURmanufactured',
                      'Concrete':'RCFw/oERD',
                      'Cut Stone':'MURsimplestone',
                      'Cut Stone & Concrete':'RCFw/oERD',
                      'Mud Bricks & Rubble':'MURadobe'
                      },
               'PSE':{
                      'Old Stone':'MURsimplestone',
                      'Adobe Clay':'MURadobe',
                      'Cement Block':'MURmanufactured',
                      'Concrete':'RCFw/oERD',
                      'Stone and Concrete':'RCFw/oERD',
                      'Cleaned Stone':'MURsimplestone'
                   }
               }

    return bt_map[iso][description]

#####################################
# Boolean checks for VI modification
#####################################

def old_mat(description):
    '''
    Determines if material is defined as old
    '''
    return description=='Old Stone'

def masonry_infill(description):
    '''
    Determines if RC Frame infill material is masonry
    '''
    return description in ['Cut Stone & Concrete','Stone and Concrete']

def precode(year):
    '''
    Determine precode for JOR
    '''
    return year<1990

def palestine68(year):
    '''
    Determine if build after 67 in PSE
    '''
    return year>1967

def high_rise(height):
    '''
    Determine if high rise
    '''
    return height>5

##############################
# Vulnerability
##############################

def EMS98_vc_dist(EMS98_bt):
    '''
    Function returning EMS-98 Vulnerability class distribution depending on the census material description for JOR and PSE
    '''
    #EMS98 vulnerability class distribution: most probable 0.75 probable 0.25 less probable 0.125 and normalized to 1
    # share of VC [A,B,C,D,E,F]
    vc_map = {'MURmanufactured':[0.125,0.75,0.125,0,0,0],
               'MURsimplestone': [0.143,0.857,0,0,0,0],
               'MURadobe': [0.75,0.25,0,0,0,0],
               'Mrubble/fieldstone': [1,0,0,0,0,0],
               'RCFw/oERD': [0.1,0.2,0.6,0.1,0,0]
               }
    #return the ems-98 vulnerability class distribution
    return vc_map[EMS98_bt]

def vulnerabilityIndex(bt_vul):
    '''
    Returns VI according to Giovinazzi 2005 using vulnerability class shares of
    a building type
    '''
    #means&sigma of Vul Class A-F
    means = [0.90,0.74,0.58,0.42,0.26,0.10]
    sigma = 0.04
    bt_VI=0
    for vulClass in range(6):
        #mean for vulClass
        VI_dist = means[vulClass]
        #VI_dist * share, added to previous classes
        bt_VI += bt_vul[vulClass]*VI_dist

    return bt_VI

def modify_VI(VI,tax):
    '''
    Modifies the VI according to some defined properties for the census row
    '''
    #effect on VI
    not_Europe = 0.04
    pc = 0.08
    rcm = 0.02
    old = 0.02
    pse68 = 0.01
    hr = -0.02
    #taxonomy: [iso,main,height,pc,RCM,old,pse68,HR]
    new_VI = VI + not_Europe + tax[3]*pc + tax[4]*rcm + tax[5]*old + tax[6]*pse68 + tax[7]*hr

    return new_VI

################################
# Occupancy
################################

def occupancy(tax):
    '''
    Determines occ_d, occ_n, occ_t
    '''
    bt = tax[1]
    if bt in ['MURmanufactured','MURsimplestone','MURadobe','Mrubble/fieldstone']:
        occ = [int(tax[2])*x for x in [2,5,3]]
    elif bt in ['RCFw/oERD']:
        occ = [int(tax[2])*x for x in [5,20,12]]
    else:
        print 'unknown bt'
    return occ

##############
# Output
##############

def write_csv(data,filename):
    '''
    Write the dictionary to a single csv
    '''
    with open(filename, 'w') as f:
        fieldnames=[
        'asset_id',
        'longitude',
        'latitude',
        'taxonomy',
        'num_buildings',
        'built_up_area',
        'structural_replacement_cost',
        'structural_retrofit_cost',
        'structural_insurance_limit',
        'structural_insurance_deductible',
        'nonstructural_replacement_cost',
        'nonstructural_retrofit_cost',
        'nonstructural_insurance_limit',
        'nonstructural_insurance_deductible',
        'contents_replacement_cost',
        'contents_retrofit_cost',
        'contents_insurance_limit',
        'contents_insurance_deductible',
        'downtime_cost',
        'downtime_insurance_limit',
        'downtime_insurance_deductible',
        'day_occupants',
        'night_occupants',
        'transit_occupants'
        ]
        writer = csv.DictWriter(f,fieldnames=fieldnames)
        writer.writeheader()
        for i in range(len(data[fieldnames[0]])):
            row = {}
            for key in data:
                row[key] = data[key][i]
            writer.writerow(row)

def write_frag(data,filename):
    '''
    Write the dictionary to a single csv
    '''
    with open(filename, 'w') as f:
        fieldnames=['tax','vi']
        writer = csv.DictWriter(f,fieldnames=fieldnames)
        writer.writeheader()
        for i in range(len(data[fieldnames[1]])):
            row = {}
            for key in data:
                row[key] = data[key][i]
            writer.writerow(row)

################################

################################
# Main Program
################################
count=0
#dictionary to keep all data
data = {'iso':[],
        'name':[],
        'tax':[],
        'lon':[],
        'lat':[],
        'bnr':[],
        'vi':[],
        'occ_d':[],
        'occ_n':[],
        'occ_t':[]
       }

#read in Jordanian census and process it
with open('JOR_regional.csv','r') as csvfile:
    headerlines = 1
    delimiter = ','
    reader = csv.reader(csvfile,delimiter=delimiter)
    #skip header
    for i in range(headerlines):
        next(reader,None)
    #JOR destinguishes btw urban and rural
    # --> row1=urban row2=rural row3=urban...
    idx = -1
    for row in reader:
        idx += 1
        #get one row
        #remove whitespace
        row = [x.strip() for x in row]
        if(idx%2)==0:
            #urban nr of buildings
            tmp_nrbdgs=int(row[4])
            #floors row[5]:row[15]
            #urban share LR,MR,HR + redistribute unknown nr floors row[15]
            total = sum([float(x) for x in row[5:15]])
            #for each floor
            tmp_H=[]
            for i in range(5,15):
                tmp_H.append(float(row[i])/total)

            #urban precode + redistribute unknown age row[29]
            total = sum([float(x) for x in row[16:29]])
            tmp_pc = sum([float(x) for x in row[16:22]])/total
            tmp_npc = sum([float(x) for x in row[22:29]])/total
        else:
            #nr bdgs rural+urban
            nr_bdgs = tmp_nrbdgs + int(row[4])
            #rural+urban share LR,MR,HR + redistribute unknown nr floors row[15]
            total = sum([float(x) for x in row[5:15]])
            #for each floor
            H=[]
            for i in range(5,15):
                H.append(tmp_H[i-5]+float(row[i])/total)

            #urban+rural precode + redistribute unknown age row[29]
            total = sum([float(x) for x in row[16:29]])
            if total == 0: total=1
            pc = tmp_pc + sum([float(x) for x in row[16:22]])/total
            npc = tmp_npc + sum([float(x) for x in row[22:29]])/total

            #store in seperate rows L,M,H,pc(pse68) with taxonomy and VI
            #iso,name,tax,bnr,vi,occ_d,occ_n,occ_t
            # get taxonomy
            tax = []
            for y in [1980,1990]:
                for h in range(1,11):
                    tax.append(taxonomy(row,str(h),y))

            #get tax as strings
            tax_as_string = []
            for t in tax:
                tax_as_string.append(tax_str(t))

            #store fix things
            data['iso']=data['iso']+20*[row[0]]
            data['name']=data['name']+20*[row[1]]
            #store taxonomy strings
            data['tax']=data['tax']+tax_as_string
            #get bnr per bt(EMS,H,pc)
            bnr = []
            for p in [npc,pc]:
                for h in H:
                    bnr.append(int(round(nr_bdgs*h*p)))

            data['bnr']=data['bnr']+bnr

            #iso,name,tax,bnr,vi,occ_d,occ_n,occ_t
            #get EMS-98 vi
            bt = EMS98_bt(row[2],row[0])
            vc = EMS98_vc_dist(bt)
            ems_vi = vulnerabilityIndex(vc)
            #modify for each taxonomy
            vi = []
            for t in tax:
                vi.append(modify_VI(ems_vi,t))

            data['vi']=data['vi']+vi

            #get occ
            occ = []
            for t in tax:
                occ.append(occupancy(t))

            occ_d = [x[0] for x in occ]
            occ_n = [x[1] for x in occ]
            occ_t = [x[2] for x in occ]
            #store occ's
            data['occ_d']=data['occ_d']+occ_d
            data['occ_n']=data['occ_n']+occ_n
            data['occ_t']=data['occ_t']+occ_t


#every 1st row of a district is unknown material and every second other
#thus first get whole file than redistribute than process
PSE = []
#read in Palestinian census and process it
with open('PSE_regional.csv','r') as csvfile:
    headerlines = 1
    delimiter = ','
    reader = csv.reader(csvfile,delimiter=delimiter)
    #skip header
    for i in range(headerlines):
        next(reader,None)

    for row in reader:
        #get one row
        #remove whitespace
        row = [x.strip() for x in row]
        #store
        PSE.append(row)

#redistribute the unknown material
nrb = [int(x[4]) for x in PSE]
nr_distr=len(PSE)/8

for i in range(nr_distr):
    #go through each district
    start_idx=i*8
    end_idx=i*8+8
    #initial distr
    idist = nrb[start_idx:end_idx+1]
    #new distr w/o unknown+other
    ndist = nrb[start_idx+2:end_idx+1]
    #buildings(ukn+other) to distribute
    uk_sum = sum(nrb[start_idx:start_idx+2])
    #total some of all (needed for weight)
    distr_sum = sum(nrb[start_idx+2:end_idx+1])
    #go through loop an distribute the buildings according to weights
    for j in range(start_idx+2,end_idx):
        weight = float(nrb[j])/distr_sum
        add = math.ceil(weight*uk_sum)
        nrb[j]+=add



    #redistribute unknown+other
    #for j in range(2,8):
    #    nrb[start_idx+j]=int(nrb[start_idx+j]/float(distr_sum)*uk_sum+nrb[start_idx+j])

#replace with new building numbers
for i in range(len(PSE)):
    PSE[i][4]=nrb[i]
#delete row with unknown material backwards
PSE=[x for x in PSE if x[3]!='Unknown' and x[3]!='Other']

#now normal processing of PSE
for row in PSE:
    #nr bdgs
    nr_bdgs = int(row[4])
    #redistribute unknown nr floors row[11]
    total = sum([float(x) for x in row[5:11]])
    #for each floor
    H=[]
    for i in range(5,11):
        H.append(float(row[i])/total)

    # pse1968 + redistribute unknown age row[18]
    total = sum([float(x) for x in row[12:18]])
    npse68 = sum([float(x) for x in row[12:14]])/total
    pse68 = sum([float(x) for x in row[14:18]])/total

    #store in seperate rows L,M,H,pc(pse68) with taxonomy and VI
    #iso,name,tax,bnr,vi,occ_d,occ_n,occ_t
    # get taxonomy
    tax = []
    for y in [1960,1970]:
        for h in range(1,7):
            tax.append(taxonomy(row,str(h),y))

    #get tax as strings
    tax_as_string = []
    for t in tax:
        tax_as_string.append(tax_str(t))

    if len(tax_as_string)-len(tax) !=0: print 'error'

    #store fix things
    data['iso']=data['iso']+12*[row[0]]
    data['name']=data['name']+12*[row[2]]
    #store taxonomy strings
    data['tax']=data['tax']+tax_as_string
    #get bnr per bt(EMS,H,pc)
    bnr = []
    for p in [npse68,pse68]:
        for h in H:
            bnr.append(int(round(nr_bdgs*h*p)))

    data['bnr']=data['bnr']+bnr

    #iso,name,tax,bnr,vi,occ_d,occ_n,occ_t
    #get EMS-98 vi
    bt = EMS98_bt(row[3],row[0])
    vc = EMS98_vc_dist(bt)
    ems_vi = vulnerabilityIndex(vc)
    #modify for each taxonomy
    vi = []
    for t in tax:
        vi.append(modify_VI(ems_vi,t))

    data['vi']=data['vi']+vi

    #get occ
    occ = []
    for t in tax:
        occ.append(occupancy(t))

    occ_d = [x[0] for x in occ]
    occ_n = [x[1] for x in occ]
    occ_t = [x[2] for x in occ]
    #store occ's
    data['occ_d']=data['occ_d']+occ_d
    data['occ_n']=data['occ_n']+occ_n
    data['occ_t']=data['occ_t']+occ_t


#get coordinates
coords={'x':[],
        'y':[],
        'name':[]
        }
with open('centroids.csv','r') as csvfile:
    headerlines = 1
    delimiter = ','
    reader = csv.reader(csvfile,delimiter=delimiter)
    #skip header
    for i in range(headerlines):
        next(reader,None)

    for row in reader:
        #get one row
        #remove whitespace
        row = [x.strip() for x in row]
        coords['x'].append(row[0])
        coords['y'].append(row[1])
        coords['name'].append(row[3])


#associate exposure with coordinates
for i in range(len(data['name'])):
        name = data['name'][i]
        lon = [coords['x'][j] for j,n in enumerate(coords['name']) if n==name]
        lat = [coords['y'][j] for j,n in enumerate(coords['name']) if n==name]
        data['lon'].append(lon[0])
        data['lat'].append(lat[0])

#organize in OQ form
ass_id = [i for i in range(len(data['iso']))]
zs = [1 for i in ass_id]
oq_exp = {
        'asset_id':                             ass_id,
        'longitude':                            data['lon'],
        'latitude':                             data['lat'],
        'taxonomy':                             data['tax'],
        'num_buildings':                        data['bnr'],
        'built_up_area':                        zs,
        'structural_replacement_cost':          zs,
        'structural_retrofit_cost':             zs,
        'structural_insurance_limit':           zs,
        'structural_insurance_deductible':      zs,
        'nonstructural_replacement_cost':       zs,
        'nonstructural_retrofit_cost':          zs,
        'nonstructural_insurance_limit':        zs,
        'nonstructural_insurance_deductible':   zs,
        'contents_replacement_cost':            zs,
        'contents_retrofit_cost':               zs,
        'contents_insurance_limit':             zs,
        'contents_insurance_deductible':        zs,
        'downtime_cost':                        zs,
        'downtime_insurance_limit':             zs,
        'downtime_insurance_deductible':        zs,
        'day_occupants':                        data['occ_d'],
        'night_occupants':                      data['occ_n'],
        'transit_occupants':                    data['occ_t']
}

#write the csv file
write_csv(oq_exp,'exp_model.csv')

#prepare file for fragility curve creation
#taxonomy,vi
vi = []
tax = set(data['tax'])
for t in tax:
    tmp = [data['vi'][i] for i,tx in enumerate(data['tax']) if tx==t]
    vi.append(tmp[0])

data2 = {'tax':list(tax),
         'vi':vi
         }
write_frag(data2,'frag_vis.csv')


#Converts the oq-like csv from exp2oq.py to nrml format
import rmtk.parsers.exposure_model_converter as emc

emc.csv_to_xml('exp_model.csv', 'exp_metadata.csv', 'exp_model.xml')

##create table to hold exposure model
#cur.execute("CREATE TABLE exposure.tmp_census_based(id serial PRIMARY KEY,iso character(80),name character(80),cell GEOMETRY,centroid GEOMETRY,bts real[])")
#
#
#cur.execute("CREATE TABLE exposure.census_based(asset_id,longitude,latitude,taxonomy,num_buildings,built_up_area,structural_replacement_cost,structural_retrofit_cost,structural_insurance_limit,structural_insurance_deductible,nonstructural_replacement_cost,nonstructural_retrofit_cost,nonstructural_insurance_limit,nonstructural_insurance_deductible,contents_replacement_cost,contents_retrofit_cost,contents_insurance_limit,contents_insurance_deductible,downtime_cost,downtime_insurance_limit,downtime_insurance_deductible,day_occupants,night_occupants,transit_occupants)"
