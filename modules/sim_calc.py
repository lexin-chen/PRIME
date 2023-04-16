from modules.sim_modules_vector import *
import numpy as np
import re
import json
import glob

class SimilarityCalculator:
    """ A class to calculate the similarity between clusters.
    
    Attributes:
        c0 (numpy.ndarray): The dominant cluster.
        input_files (list): The list of cluster files.
        summary_file (str): The path to the summary file.
        n_clusters (int): The number of clusters to analyze.
        frame_weighted_sim (bool): Whether to weight the similarity values by the number of frames in the cluster.
        n_ary (str): The n_ary similarity metric to use.
        weight (str): The weight to use for the similarity metric.
    
    Methods:
        calculate_pairwise: Calculates the similarity between the dominant cluster and all other clusters.
        calculate_union: Calculates the similarity between the dominant cluster and the union of all other clusters.
        calculate_sims: Calculates the similarity between the dominant cluster and the cluster with the highest similarity to the dominant cluster.
        calculate_medoid: Calculates the similarity between the dominant cluster and the cluster with the lowest average distance to the dominant cluster.
        calculate_outliers: Calculates the similarity between the dominant cluster and the cluster with the highest average distance to the dominant cluster.
    """
    
    def __init__(self, cluster_folder=None, summary_file=None, trim_frac=None, n_clusters=None, frame_weighted_sim=True, n_ary='RR', weight='nw'):
        """ Initializes a new instance of the SimilarityCalculator class.
        
        Args:
            cluster_folder (str): The path to the folder containing the normalized cluster files (`preprocess.py`).
            summary_file (str): The path to the summary file containing the number of frames for each cluster (CPPTRAJ clusteringoutput).
            trim_frac (float): The fraction of outliers to trim from the dominant cluster, c0.
            n_clusters (int): The number of clusters to analyze, None for all clusters.
            frame_weighted_sim (bool): Whether to weight similarity values by the number of frames.
            n_ary (str): The similarity metric to use for comparing clusters. 
            weight (str): The weighting scheme to use for comparing clusters.

        Returns:
            None.
            
        Notes:
            - Options for n_ary and weight under `sim_modules_vector.py`.
        """
        
        self.c0 = np.genfromtxt(f"{cluster_folder}/normed_clusttraj.c0")
        if trim_frac:
            self.c0 = trim_outliers(self.c0, trim_frac=trim_frac, n_ary=n_ary, weight=weight)
        self.input_files = sorted(glob.glob(f"{cluster_folder}/normed_clusttraj.c*"), key=lambda x: int(re.findall("\d+", x)[0]))[1:]
        self.summary_file = summary_file
        self.n_clusters = n_clusters
        self.frame_weighted_sim = frame_weighted_sim
        self.n_ary = n_ary
        self.weight = weight
        self.sims = {}
    
    def calculate_pairwise(self):
        """ Calculates pairwise similarity between each cluster and all other clusters.

        Notes:
            For each cluster file, loads the data and calculates the similarity score with the dominant c0 cluster.
            The similarity score is calculated as the average of pairwise similarity values between each frame in the cluster and the dominant c0 cluster.
            The similarity metric used is defined by the n_ary parameter and can be either 'RR' or 'SM'.
        
        Returns:
            If `frame_weighted_sim` is `False`, returns a dictionary containing the unweighted average similarity values between each pair of clusters.
            If `frame_weighted_sim` is `True`, returns the result of the `weight_dict` function, which applies a frame-weighting factor to the similarity values.
        """
        for each, file in enumerate(self.input_files):
            ck = np.genfromtxt(file)
            self.sims[each] = {}
            for i, x in enumerate(self.c0):
                total = 0
                for j, y in enumerate(ck):
                    c_total = np.sum(np.array([x, y]), axis=0)
                    pair_sim = calculate_counters(c_total, 2, c_threshold=None, w_factor="fraction")
                    if self.n_ary == 'RR':    
                        total += pair_sim["a"] / pair_sim["p"]
                    elif self.n_ary == 'SM':
                        total += (pair_sim["a"] + pair_sim["d"]) / pair_sim["p"]
                avg = total / len(ck)
                if f"f{i}" not in self.sims[each]:
                    self.sims[each][f"f{i}"] = []
                self.sims[each][f"f{i}"] = avg

        nw_dict = sort_dict_add_avg(self.sims)
        if self.frame_weighted_sim is False:
            return nw_dict
        if self.frame_weighted_sim is True:
            return weight_dict(file_path=None, summary_file=self.summary_file, dict=nw_dict, n_clusters=self.n_clusters)

    def calculate_union(self):
        for each, file in enumerate(self.input_files):
            ck = np.genfromtxt(file)
            self.sims[each] = {}
            for i, x in enumerate(self.c0):
                c_total = np.sum(ck, axis=0) + x
                n_fingerprints = len(ck) + 1
                index = gen_sim_dict(c_total, n_fingerprints, c_threshold=None, w_factor="fraction")
                if f"f{i}" not in self.sims[each]:
                    self.sims[each][f"f{i}"] = []
                self.sims[each][f"f{i}"] = index[self.weight][self.n_ary]
        
        nw_dict = sort_dict_add_avg(self.sims)
        if self.frame_weighted_sim is False:
            return nw_dict
        if self.frame_weighted_sim is True:
            return weight_dict(file_path=None, summary_file=self.summary_file, dict=nw_dict, n_clusters=self.n_clusters)

    def calculate_sims(self, index_func):
        for each, file in enumerate(self.input_files):
            ck = np.genfromtxt(file)
            index = index_func(ck, n_ary=self.n_ary, weight=self.weight)
            medoid = ck[index]
            self.sims[each] = {}
            for i, x in enumerate(self.c0):
                c_total = medoid + x
                pair_sim = calculate_counters(c_total, 2, c_threshold=None, w_factor="fraction")
                if f"f{i}" not in self.sims[each]:
                    self.sims[each][f"f{i}"] = []
                if self.n_ary == 'RR':    
                    self.sims[each][f"f{i}"] = pair_sim["a"] / pair_sim["p"]
                elif self.n_ary == 'SM':
                    self.sims[each][f"f{i}"] = (pair_sim["a"] + pair_sim["d"]) / pair_sim["p"]
        nw_dict = sort_dict_add_avg(self.sims)
        return nw_dict
    
    def calculate_medoid(self):
        nw_dict = self.calculate_sims(calculate_medoid)
        if self.frame_weighted_sim is False:
            return nw_dict
        if self.frame_weighted_sim is True:
            return weight_dict(file_path=None, summary_file=self.summary_file, dict=nw_dict, n_clusters=self.n_clusters)
        
    def calculate_outlier(self):
        nw_dict = self.calculate_sims(calculate_outlier)
        if self.frame_weighted_sim is False:
            return nw_dict
        if self.frame_weighted_sim is True:
            return weight_dict(file_path=None, summary_file=self.summary_file, dict=nw_dict, n_clusters=self.n_clusters)

def trim_outliers(total_data, trim_frac=0.1, n_ary='RR', weight='nw'):
    """ Function will trim a desired percentage of outliers from the dataset by calculating largest complement similarity. """
    n_fingerprints = len(total_data)
    c_total = np.sum(total_data, axis = 0)
    comp_sims = []
    for i, pixel in enumerate(total_data):
        c_total_i = c_total - total_data[i]
        Indices = gen_sim_dict(c_total_i, n_fingerprints - 1)
        sim_index = Indices[weight][n_ary]
        comp_sims.append(sim_index)
    comp_sims = np.array(comp_sims)
    cutoff = int(np.floor(n_fingerprints * float(trim_frac)))
    highest_indices = np.argpartition(-comp_sims, cutoff)[:cutoff]
    total_data = np.delete(total_data, highest_indices, axis=0)
    # total_data[highest_indices] = np.nan
    return total_data

def weight_dict(file_path=None, summary_file=None, dict=None, n_clusters=None):
    """ Similarity values are frame_weighted_sim by the number of frames of the cluster and this is stored in the summary file from clustering. """
    if file_path is not None:
        with open(file_path, 'r') as file:
            dict = json.load(file)
    elif dict is not None:
        dict = dict
    for key in dict:
        dict[key].pop()
    
    num = np.loadtxt(summary_file, unpack = True, usecols=(1), skiprows=(1))
    if n_clusters:
        num = num[0:n_clusters]
    w_sum = np.sum(num, axis=0)
    weights = num / w_sum
    weights = weights[1:]

    w_dict = {}
    for key in dict:
        old_list = dict[key]
        w_dict[key] = [old_list[i] * v for i, v in enumerate(weights)]
    for k in w_dict:
        average = sum(w_dict[k]) / len(w_dict[k])
        w_dict[k].append(average)

    return w_dict

def sort_dict_add_avg(dict):
    """ The dictionary is organized in order of frames and the average is attached to the end of each key. """
    nw_dict = {}
    for i in sorted(dict):
        for k, v in dict[i].items():
            if k not in nw_dict:
                nw_dict[k] = [None] * len(dict)
            nw_dict[k][i] = v
    for k in nw_dict:
        average = sum(nw_dict[k]) / len(nw_dict[k])
        nw_dict[k].append(average)
    
    return nw_dict
