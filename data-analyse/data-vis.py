import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.close('all')

# load data
latency_2 = pd.read_csv('../log/cleaned/staircase - with 2 node between - in a chain - latency.txt', sep=" ", header=None)
latency_1 = pd.read_csv('../log/cleaned/staircase - with 1 node between - in a chain - latency.txt', sep=" ", header=None)
latency_0 = pd.read_csv('../log/cleaned/staircase - with 0 node between - in a chain - latency.txt', sep=" ", header=None)

# take last column and remove 's' from data, e.g. 0.543s
latency_2 = latency_2.iloc[: , -1].str[:-1].astype('float').to_frame()
latency_1 = latency_1.iloc[: , -1].str[:-1].astype('float').to_frame()
latency_0 = latency_0.iloc[: , -1].str[:-1].astype('float').to_frame()

latency_data = [latency_0, latency_1, latency_2]
# arrange format
for index,list in enumerate(latency_data):
    list.columns = ['latency']
    list['nodes_between'] = index

latency_all = pd.concat([latency_0, latency_1, latency_2])
#print(latency_all.head())

# draw box plot of latency w.r.t. nodes in between
plt.figure()
bplot1 = latency_all.boxplot(by='nodes_between',column =['latency'], grid = True,fontsize=16,figsize=(8,6))
bplot1.set_xlabel('nodes between',fontsize=16)
bplot1.set_ylabel('latency(s)',fontsize=16)
bplot1.set_title("latency with respect to the number of relay nodes",fontsize=16)
bplot1.get_figure().suptitle('')
plt.savefig("./fig/latency - nodes between.png", format="png",dpi=300)
plt.show()

payload_2 = pd.read_csv('../log/cleaned/staircase - with 2 node between - in a chain - payload.csv')
payload_1 = pd.read_csv('../log/cleaned/staircase - with 1 node between - in a chain - payload.csv')
payload_0 = pd.read_csv('../log/cleaned/staircase - with 0 node between - in a chain - payload.csv')
payload_ideal = pd.read_csv('../log/cleaned/ideal - with 0 node between - in a chain - payload.csv')

# get right format
for i in range(9):
    # split string by " " and get last part, then remove 's' and convert to float
    payload_ideal[str(i+1)] = payload_ideal[str(i+1)].str.rsplit(" ", 1).str[-1].str[:-1].astype('float')
    payload_0[str(i + 1)] = payload_0[str(i + 1)].str.rsplit(" ", 1).str[-1].str[:-1].astype('float')
    payload_1[str(i + 1)] = payload_1[str(i + 1)].str.rsplit(" ", 1).str[-1].str[:-1].astype('float')
    payload_2[str(i + 1)] = payload_2[str(i + 1)].str.rsplit(" ", 1).str[-1].str[:-1].astype('float')

# change to one long column
payload_ideal_edit = pd.DataFrame()
payload_0_edit = pd.DataFrame()
payload_1_edit = pd.DataFrame()
payload_2_edit = pd.DataFrame()

tmp1 = pd.DataFrame(columns=['latency'])
tmp2 = pd.DataFrame(columns=['latency'])
tmp3 = pd.DataFrame(columns=['latency'])
tmp4 = pd.DataFrame(columns=['latency'])

for i in range(9):
    tmp1['latency'] = payload_ideal[str(i+1)].copy()
    tmp1['group'] = str(i+1)
    payload_ideal_edit = pd.concat([payload_ideal_edit, tmp1])

    tmp2['latency'] = payload_0[str(i + 1)].copy()
    tmp2['group'] = str(i + 1)
    payload_0_edit = pd.concat([payload_0_edit, tmp2])

    tmp3['latency'] = payload_1[str(i + 1)].copy()
    tmp3['group'] = str(i + 1)
    payload_1_edit = pd.concat([payload_1_edit, tmp3])

    tmp4['latency'] = payload_2[str(i + 1)].copy()
    tmp4['group'] = str(i + 1)
    payload_2_edit = pd.concat([payload_2_edit, tmp4])

# replace
payload_ideal = payload_ideal_edit
payload_0 = payload_0_edit
payload_1 = payload_1_edit
payload_2 = payload_2_edit
payload_ideal.dropna(inplace=True)
payload_0.dropna(inplace=True)
payload_1.dropna(inplace=True)
payload_2.dropna(inplace=True)


#plt.figure()
#payload_ideal.plot()
#plt.show()
payload_ideal_bygroup = payload_ideal.groupby(by="group")
avg_time_ideal = payload_ideal_bygroup.mean()
std_ideal = payload_ideal_bygroup.std()

payload_0_bygroup = payload_0.groupby(by="group")
avg_time_0 = payload_0_bygroup.mean()
std_0 = payload_0_bygroup.std()

payload_1_bygroup = payload_1.groupby(by="group")
avg_time_1 = payload_1_bygroup.mean()
std_1 = payload_1_bygroup.std()

payload_2_bygroup = payload_2.groupby(by="group")
avg_time_2 = payload_2_bygroup.mean()
std_2 = payload_2_bygroup.std()




# plot in one figure
plt.figure()
fig, ax = plt.subplots()
plot2 = avg_time_ideal.plot(label="ideal",fontsize=16,figsize=(8,6),ax=ax)#yerr=std_ideal
avg_time_0.plot(label="0 relay nodes",fontsize=16,figsize=(8,6),ax=ax)
avg_time_1.plot(label="1 relay nodes",fontsize=16,figsize=(8,6),ax=ax)
avg_time_2.plot(label="2 relay nodes",fontsize=16,figsize=(8,6),ax=ax)

plot2.set_xlabel('payload size (Bytes)',fontsize=16)
plot2.set_ylabel('latency(s)',fontsize=16)
plot2.set_title("latency with respect to payload size",fontsize=16)
plot2.set_xticks(np.arange(9), [(i+1)*25 for i in range(9)])
plot2.legend(['ideal',"0 relay nodes","1 relay nodes","2 relay nodes"])
plot2.set_ylim(0.6,1.2)
plt.savefig("./fig/latency - paylaod size.png", format="png",dpi=300)
plt.show()