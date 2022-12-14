import os
import time

import nibabel as nib
import numpy as np
import pandas as pd
import tqdm

from utils.densities import density

dir_home = os.path.join("/mnt", "hdd")
dir_adhd200 = os.path.join(dir_home, "Assets", "ADHD200")
# sites = ["KKI", "Peking_1", "Peking_2", "Peking_3"]
sites = ["KKI"]
func = pd.DataFrame()
anat = pd.DataFrame()

# def smri(subject, dx, site):
#     anat_path = os.path.join(dir_adhd200, f"{site}_athena",f"{site}_preproc", f"{subject}", f"wssd{subject}_session_1_anat.nii.gz")
#     gm_path = os.path.join(dir_adhd200, f"{site}_athena",f"{site}_preproc", f"{subject}", f"wssd{subject}_session_1_anat_gm.nii.gz")
#     wm_path = os.path.join(dir_adhd200, f"{site}_athena",f"{site}_preproc", f"{subject}", f"wssd{subject}_session_1_anat_wm.nii.gz")
#     csf_path = os.path.join(dir_adhd200, f"{site}_athena",f"{site}_preproc", f"{subject}", f"wssd{subject}_session_1_anat_csf.nii.gz")

#     anat = nib.load(anat_path).get_fdata()  # 197, 233, 189
#     gm = nib.load(gm_path).get_fdata()      # 197, 233, 189
#     wm = nib.load(wm_path).get_fdata()      # 197, 233, 189
#     csf = nib.load(csf_path).get_fdata()    # 197, 233, 189

#     features = ['x', 'y', 'z', 'gm_density', 'wm_density', 'csf_density', 'gm', 'wm', 'csf', 'dx'] # 10

#     gm_density, wm_density, csf_density = density(anat, gm, wm, csf)

#     df = pd.DataFrame(columns=features)

#     for x in range(anat.shape[0]):
#         for y in range(anat.shape[1]):
#             for z in range(anat.shape[2]):
#                 f0 = gm[x][y][z]
#                 f1 = wm[x][y][z]
#                 f2 = csf[x][y][z]

#                 if f0 == 0 and f1 == 0 and f2 == 0:
#                     continue

#                 else:
#                     row = [x, y, z, gm_density, wm_density, csf_density]
#                     row.append(f0)
#                     row.append(f1)
#                     row.append(f2)
#                     row.append(dx)
#                     df.loc[len(df.index)] = row

#     print(df.shape) # rows x number of features

#     print(f"Generated anatomical features for {subject} from {site}")

#     return df

def fmri(subject, dx, age, gender, handedness, piq, viq, site):
    falff_path = os.path.join(dir_adhd200, f"{site}_athena", f"{site}_falff_filtfix",
                              f"{subject}", f"falff_{subject}_session_1_rest_1.nii.gz")
    falff = nib.load(falff_path).get_fdata()  # 49, 58, 47

    reho_path = os.path.join(dir_adhd200, f"{site}_athena", f"{site}_reho_filtfix",
                             f"{subject}", f"reho_{subject}_session_1_rest_1.nii.gz")
    reho = nib.load(reho_path).get_fdata()  # 49, 58, 47

    fc_path = os.path.join(dir_adhd200, f"{site}_athena", f"{site}_preproc",
                           f"{subject}", f"fc_snwmrda{subject}_session_1_rest_1.nii.gz")
    fc = nib.load(fc_path).get_fdata()  # 49, 58, 47, 1, 10

    features = ['x', 'y', 'z', 'fc1', 'fc2', 'fc3', 'fc4', 'fc5', 'fc6',
                'fc7', 'fc8', 'fc9', 'fc10', 'falff', 'reho', 'age', 'gender', 'handedness', 'piq', 'viq', 'dx']  # 20 

    df = pd.DataFrame(columns=features)

    for x in range(falff.shape[0]):
        for y in range(falff.shape[1]):
            for z in range(falff.shape[2]):
                f0 = fc[x][y][z][0]
                f1 = falff[x][y][z]
                f2 = reho[x][y][z]
                
                if f1 != 0 and f2 != 0 and sum(f0) != 0:
                    row = [x, y, z]
                    for i in range(10):
                        row.append(f0[i])
                    row.append(f1)
                    row.append(f2)
                    row.append(age)
                    row.append(gender)
                    row.append(handedness)
                    row.append(piq)
                    row.append(viq)
                    row.append(dx)
                    df.loc[len(df.index)] = row

                else:
                    continue
    print(df.shape) # rows x number of features

    print(f"Generated functional features for {subject} from {site}")

    return df

if __name__ == "__main__":


    for site in sites:
        pheno = pd.read_csv(os.path.join(dir_adhd200, f"{site}_athena", f"{site}_preproc", f"{site}_phenotypic.csv"))

        rows = pd.DataFrame(columns=["subj", "end"])

        adhdCount = 0
        controlCount = 0
        
        for ind in tqdm.tqdm(pheno.index):

            dx = pheno["DX"][ind]
            if dx == 0:
                if controlCount >= 40:
                    print("control limit reached")
                    continue
                controlCount += 1
            else:
                if adhdCount >= 40:
                    print("adhd limit reached")
                    continue
                adhdCount += 1
            subID = pheno["ScanDir ID"][ind]
            age = pheno["Age"][ind]
            gender = pheno["Gender"][ind]
            handedness = pheno["Handedness"][ind]
            piq = pheno["Performance IQ"][ind]
            viq = pheno["Verbal IQ"][ind]

            print(f"Current subject: {subID}\nSite: {site}")

            func = pd.concat([func, fmri(subID, dx, age, gender, handedness, piq, viq, site)], axis=0)
            lastRow = func.tail(1).index[0]
            rows.loc[len(rows.index)] = [subID, lastRow]

        print(f"ADHD: {adhdCount}")
        print(f"Control: {controlCount}")

        func.to_csv(f"features/{site}_func.csv", index=False)
        rows.to_csv(f"features/{site}_rows_func.csv", index=False)
