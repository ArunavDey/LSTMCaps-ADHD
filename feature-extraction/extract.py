import nibabel as nib
import numpy as np
import pandas as pd
import os
import time
from utils.densities import density


# dir_home = os.path.expanduser("~")
dir_home = os.path.join("/mnt", "d")
dir_athena = os.path.join(dir_home, "Assets", "ADHD200", "KKI_athena")
dir_niak = os.path.join(dir_home, "Assets", "ADHD200", "KKI_niak")


def smri(subject, dx, idx, save_path="./features/"):
    anat_path = os.path.join(
        dir_niak, "anat_kki", f"X_{subject}", f"anat_X_{subject}_classify_stereolin.nii.gz")
    anat = nib.load(anat_path).get_fdata()

    # features = ['x', 'y', 'z', 'class', 'gm_density', 'wm_density', 'dx', 'idx'] # 8
    features = ['x', 'y', 'z', 'class', 'dx', 'idx']

    df = pd.DataFrame(columns=features)

    for x in range(100, 105):
        for y in range(100, 105):
            for z in range(100, 105):
                # for x in range(anat.shape[0]):
                #     for y in range(anat.shape[1]):
                #         for z in range(anat.shape[2]):
                row = [x, y, z]
                row.append(anat[x][y][z])
                row.append(dx)
                row.append(idx)
                df.loc[len(df.index)] = row

    print(f"Generated functional features for {subject}")

    save = os.path.join(save_path, f"anat_features_{subject}.csv")

    df.to_csv(save, index=False)


def fmri(subject, dx, idx, save_path="./features/"):
    falff_path = os.path.join(dir_athena, "KKI_falff_filtfix",
                              f"{subject}", f"falff_{subject}_session_1_rest_1.nii.gz")
    falff = nib.load(falff_path).get_fdata()  # 49, 58, 47

    reho_path = os.path.join(dir_athena, "KKI_reho_filtfix",
                             f"{subject}", f"reho_{subject}_session_1_rest_1.nii.gz")
    reho = nib.load(reho_path).get_fdata()  # 49, 58, 47

    fc_path = os.path.join(dir_athena, "KKI_preproc",
                           f"{subject}", f"fc_snwmrda{subject}_session_1_rest_1.nii.gz")
    fc = nib.load(fc_path).get_fdata()  # 49, 58, 47, 1, 10

    features = ['x', 'y', 'z', 'fc1', 'fc2', 'fc3', 'fc4', 'fc5', 'fc6',
                'fc7', 'fc8', 'fc9', 'fc10', 'falff', 'reho', 'dx', 'idx']  # 17

    df = pd.DataFrame(columns=features)

    for x in range(25, 30):
        for y in range(25, 30):
            for z in range(25, 30):
                # for x in range(falff.shape[0]):
                #     for y in range(falff.shape[1]):
                #         for z in range(falff.shape[2]):
                row = [x, y, z]
                for i in range(10):
                    row.append(fc[x][y][z][0][i])
                row.append(falff[x][y][z])
                row.append(reho[x][y][z])
                row.append(dx)
                row.append(idx)
                df.loc[len(df.index)] = row

    print(f"Generated functional features for {subject}")

    save = os.path.join(save_path, f"func_features_{subject}.csv")

    df.to_csv(save, index=False)


if __name__ == "__main__":
    pheno_path = os.path.join(
        dir_athena, "KKI_preproc", "KKI_phenotypic.csv")
    pheno = pd.read_csv(pheno_path)

    subADHD = list()
    subControl = list()

    for ind in pheno.index:
        subID = pheno["ScanDir ID"][ind]
        dx = pheno["DX"][ind]
        idx = pheno["ADHD Index"][ind]

        if dx == 0:
            subControl.append((subID, dx, idx))
        else:
            subADHD.append((subID, dx, idx))

    controlFunc = pd.DataFrame()
    controlAnat = pd.DataFrame()
    adhdFunc = pd.DataFrame()
    adhdAnat = pd.DataFrame()

    print("\nGenerating CSVs for Control set")
    for i in range(5):
        start = time.time()
        subID, dx, idx = subControl[i]
        fmri(subID, dx, idx, "./features/control/")
        smri(subID, dx, idx, "./features/control/")
        end = time.time()
        print(f"Took {end - start}s")

    print("\nGenerating CSVs for ADHD set")
    for i in range(5):
        start = time.time()
        subID, dx, idx = subADHD[i]
        fmri(subID, dx, idx, "./features/adhd/")
        smri(subID, dx, idx, "./features/adhd/")
        end = time.time()
        print(f"Took {end - start}s")
