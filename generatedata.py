
import os
import datetime

BaseDay=datetime.datetime(2022, 6, 15, 1, 58, 45, 476805)
Today=datetime.datetime.now()
diff=(Today-BaseDay).days
ds=str(Today)[:10]

model_dir='gs://seangoh-smu-mle-usa/Models/FaceMaskEfficientNetModel'
old_data_dir='gs://seangoh-smu-mle-usa/FaceMask/Test'
drift_data_dir='gs://seangoh-smu-mle-usa/FaceMask/Drift'
#os.system('mkdir -p ./app')
os.system('mkdir -p /app/{}/WithMask'.format(ds))
os.system('mkdir -p /app/{}/WithoutMask'.format(ds))
os.system('gsutil -mq cp -r {} /app'.format(model_dir)) #remove . for docker image
os.system('gsutil -mq cp -r {} /app'.format(old_data_dir))
os.system('gsutil -mq cp -r {} /app'.format(drift_data_dir))

DriftMaskDir='/app/Drift/WithMask'
DriftNoMaskDir='/app/Drift/WithoutMask'
OriginalMaskDir='/app/Test/WithMask'
OriginalNoMaskDir='/app/Test/WithoutMask'
DestinationWithMask='/app/{}/WithMask'.format(ds)
DestinationWithoutMask='/app/{}/WithoutMask'.format(ds)
CopyFrom='/app/{}'.format(ds)

import random
#Change Period Elapsed to Variable
PeriodElapsed=diff
DataDecayRatio=0.9
DataSizeTrend=1.1
DistributionDrift=0.9
BaseTotalSample=100
TotalSample=BaseTotalSample*(0.7+0.6*(random.random())*DataSizeTrend**PeriodElapsed)
CurrentDriftRatio=1-DataDecayRatio**(PeriodElapsed+random.random()/2)
CurrentWithoutMaskRatio=1-0.5*DistributionDrift**(PeriodElapsed-1+random.random()/2)

DriftSampleSize=int(TotalSample*CurrentDriftRatio)
OriginalSampleSize=int(TotalSample-DriftSampleSize)

DriftWithoutMask=int(CurrentWithoutMaskRatio*DriftSampleSize)
DriftWithMask=int(DriftSampleSize-DriftWithoutMask)
OriginalWithoutMask=int(CurrentWithoutMaskRatio*OriginalSampleSize)
OriginalWithMask=int(OriginalSampleSize-OriginalWithoutMask)



DriftMaskNum=len(os.listdir(DriftMaskDir))
DriftNoMaskNum=len(os.listdir(DriftNoMaskDir))
OriginalMaskNum=len(os.listdir(OriginalMaskDir))
OriginalNoMaskNum=len(os.listdir(OriginalNoMaskDir))

DMSample,DMRepeat=DriftWithMask%DriftMaskNum,DriftWithMask//DriftMaskNum
DNMSample,DNMRepeat=DriftWithoutMask%DriftNoMaskNum,DriftWithoutMask//DriftNoMaskNum
OMSample,OMRepeat=OriginalWithMask%OriginalMaskNum,OriginalWithMask//OriginalMaskNum
ONMSample,ONMRepeat=OriginalWithoutMask%OriginalNoMaskNum,OriginalWithoutMask//OriginalNoMaskNum

def GeneratePaths(datadir,repeat,sample):
    dirs=os.listdir(datadir)
    paths=[os.path.join(datadir,imagedir) for imagedir in dirs*repeat]
    sampleindex=random.sample(dirs,sample)
    newpaths=[os.path.join(datadir,i) for i in sampleindex]
    paths.extend(newpaths)
    return paths

#Generate Directories to Copy
DriftMaskPaths=GeneratePaths(DriftMaskDir,DMRepeat,DMSample)
DriftNoMaskPaths=GeneratePaths(DriftNoMaskDir,DNMRepeat,DNMSample)
OriginalMaskPaths=GeneratePaths(OriginalMaskDir,OMRepeat,OMSample)
OriginalNoMaskPaths=GeneratePaths(OriginalNoMaskDir,ONMRepeat,ONMSample)

#Copy Files
import shutil
def GenerateFiles(filepaths,folderdestination,prefix):
    for num,path in enumerate(filepaths):
        destination=os.path.join(folderdestination,prefix+str(num)+'.jpeg')
        shutil.copyfile(path,destination)
    return


GenerateFiles(DriftMaskPaths,DestinationWithMask,'D')
GenerateFiles(DriftNoMaskPaths,DestinationWithoutMask,'DN')
GenerateFiles(OriginalMaskPaths,DestinationWithMask,'O')
GenerateFiles(OriginalNoMaskPaths,DestinationWithoutMask,'ON')

#os.system('gsutil rm gs://seangoh-smu-mle-usa/DailyQC/{}'.format(ds))
shellcommand='gsutil -mq cp -r {} gs://seangoh-smu-mle-usa/CloudBuild/DailyQC/'.format(CopyFrom,ds)
os.system(shellcommand)
print('v2')
