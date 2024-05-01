import numpy as np
import sys
sys.path.insert(0, '../../')
from modules.inputs.preprocess import gen_traj_numpy, normalize_file, Normalizer
import re
import glob

# System info - EDIT THESE
input_top = '../../example/aligned_tau.pdb'
output_base_name = 'normed_clusttraj'
atomSelection = 'resid 3 to 12 and name N CA C O H'
n_clusters = 10

if __name__ == '__main__':
    list_clusttraj = sorted(glob.glob("../clusters/outputs/clusttraj_*"), 
                            key=lambda x: int(re.findall("\d+", x)[0]))
    list_clusttraj = list_clusttraj[:n_clusters]
    all_clusttraj = []
    for clusttraj in list_clusttraj:
        traj_numpy = gen_traj_numpy(input_top, clusttraj, atomSelection)
        all_clusttraj.append(traj_numpy)
    concat_clusttraj = np.concatenate(all_clusttraj)
    normed_data, min, max, avg = normalize_file(concat_clusttraj, norm_type='v3')
    np.save('normed_data.npy', normed_data)
    for i, traj in enumerate(all_clusttraj):
        norm = Normalizer(data=traj, custom_min=min, custom_max=max)
        normed_frame = norm.get_v3_norm()
        np.save(f'{output_base_name}.c{i}.npy', normed_frame)
    