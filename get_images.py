import os

scans = os.listdir('app/static/subjects/HCD_wb1.4.2.pngs-selected/')

scans_test = [i.split('_V1_MR_', 1) for i in scans]

subj_list = set()
scantype_list = []
for i in scans:
    if i not in subj_list:
        subj_list.add(i.split('_V1_MR', 1)[0])

    scantype_list.append(i.split('_V1_MR_', 1)[1])


this_scan = scans[3]
cut_off = this_scan.find('.fM')

this_new_scan = this_scan[:cut_off]

print(this_new_scan)
