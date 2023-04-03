<img src="img/header.jpg" width="1000" height=auto align="center"></a>

**🪄 Mastering the art of protein refinement, one conformation at a time 🪄**

Refining protein structures is important because the accuracy of protein structures influence how our understanding of its function and its interactions with other molecules, which can help to design new drugs to target specific molecular interactions.  

This repo contains six different ways of determining the native structure of biomolecules from simulation or clustering data. 

<img src="img/methods.jpg" alt="Girl in a jacket" width="500" height=auto align="center"></a>

*Fig 1. Six techniques of protein refinement. Blue is top cluster.* 

## Usage
`modules` contains the functions required to run the algorithm. `new_clusters/clusttraj.c*` contains sample clustering files prepared through CPPTRAJ Hierarchical clustering. `new_clusters/normed_clusttraj.c*` consists clustering files normalized through min-max normalization. `new_clusters/normed_data.txt` contains all clustering files are appended through and normalized. `similarity.py` generates a similarity dictionary from running the protein refinement method. 

## Tutorial

### Step 1.
```
git clone https://github.com/lexin-chen/PRIME.git
```
### Step 2. Normalization

- Normalize the trajectory data between $[0,1]$ using the Min-Max Normalization. 

### Step 3. Similarity Calculations
`similarity.py` generates a similarity dictionary from running the protein refinement method. 
- `-h` - for help with the argument options.
- `-m` - methods (*required)
- `-n` - number of clusters (*required)
- `-i` - similarity index (*required)
- `-t` - Fraction of outliers to trim in decimals. 
- `-w` - Weighing clusters by frames it contains.
- `-d` - directory where the `normed_clusttraj.c*` files are located.
- `-s` - location where `summary` file is located

```
python similarity.py -m medoid -n 11 -i RR
```
To generate a similarity dictionary using data in `sample_clusters/norm_clusttraj.c*` using the medoid method (3.1 in *Fig 1*) and Russell Rao index.

The result is a dictionary organized as followes:
Keyes are frame #. Values are [cluster 1 similarity, cluster #2 similarity, ..., average similarity of all clusters].

### Step 4. Determine the native structure.

