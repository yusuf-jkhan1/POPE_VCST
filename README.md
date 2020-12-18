# POPE VCST

> Author: Yusuf J Khan

### **P**lacement **O**ptimization of **P**ublic **EV** **C**harging **S**tations using **T**elematics data



### **Objective:**  
Develop a method to determine the Optimal Placement of EV public charging Stations by analyzing the geospatial vehicle telematics data provided by [99P Labs developer API](https://www.99plabs.com/)


### **Stages**
- Data Acquisition and Wrangling
- Candidate Location Identification
- Cluster Feature Engineering
- Selection Optimization
- Visualization

### **Data Acquisition and Wrangling**  
        
> **Modules**: ~~kotoTelematics~~, kotoQuery, kotoDataHandler, kotoMongoUtils, kotoS3SqliteUtils

![AcWr](https://github.com/yusuf-jkhan1/POPE_VCST/blob/master/imgs/AcWr.png/)

In the data acquisition stage we fetch data from the 99P developer labs API, while working around the 
API single call throughput volume constraint, as well as our local workspace memory constraints. We 
loop and fetch from the API, and then with each response, we apply a query function that iteratively 
aggregates to our intended insight from the response. Then before the loop closes, the query function 
also internally calls a data handler which stores the query output and performs the necessary logical 
comparisons and updates the data storage.
    
### **Candidate Location Identification**
> Modules: kotoDensityScan

![Dests](https://github.com/yusuf-jkhan1/POPE_VCST/blob/master/imgs/CbusDests.png)


In the candidate location identification stage, we use the stored output from the previous stage, 
specifically, the geospatial features, which we then pass through sci-kit learn's implementation 
of the dbscan algorithm, with the epsilon proximity parameter and the haversine distance metric 
supplied as such, that we are considering two observations as neighbors if their haversine distance
(great circle distance) is less than 200 meters, and each cluster has a critical mass at least 60 
observations. The result of this algorithm gives us an output that contains by row, the vehicle VIN, 
the trip SEQuence number, and LATitutde and LONgitude.

### **Cluster Feature Engineering**

> Modules: kotoDistMatrix ; Notebooks: Executable.ipynb

![Arriv](https://github.com/yusuf-jkhan1/POPE_VCST/blob/master/imgs/ArrivalHomog.png)

Once the clusters have been identified, then we enrich them with features to help us select which features
are most appropriate to be selected for EV charging station placements. The majority of this code, is not 
modularized, and exists in the Executable ipython notebook. The features we determine are: 
average dwell time by cluster, average hourly arrivals by cluster, absolute visits to each cluster, unique 
visits to each cluster. There are several intermediate features that are derived to arrive at these 
four features, however these are the final four features which are used to determine our utility feature 
by cluster. Average hourly arrivals follow a poisson process (during business hours), and average dwell 
time can be used to represent service rate, and is generally distributed. Given that arrival at these 
clusters don't incur any type of queue, we assume this as a M/G/Infinite server model. Then applying 
Little's theorem, we multiply the arrival rate, by the service rate to obtain the expected number of 
vehicles at a cluster at any given time during business hours (5am-10pm). We use the the unique visits 
and absolute visits to calculate the observed diversity at each cluster, because what we hope the optimal 
placement of EV charging stations would achieve is to signal to the latent EV adopters. Assuming the 
latent EV adopter probability is i.i.d then, reaching more people should be the best approach for our 
objective. So we multiply this observed diversity with expected membership, to output our utility score.

![InterArriv](https://github.com/yusuf-jkhan1/POPE_VCST/blob/master/imgs/InterArrivalDist.png)

The second portion of the feature engineering, is to take a representative location within the cluster, 
by simply finding the average of the latitudes and longitudes, and passing these through the kotoDistMatrix 
module which calls the google distance matrix api and returns an adjacency matrix of driving distance 
between every cluster, as opposed to euclidean or some other distance metric that doesn't take road paths 
into account.

### **Selection Optimization**

> Modules: kotoOptimus

![NetworkDiagram](https://github.com/yusuf-jkhan1/POPE_VCST/blob/master/imgs/NetDiag.png)

At this point, we have a utility score for each candidate location, the driving distance between each of them, 
and a representative cluster coordinate. At this point the structure of our data resembles a graph network, 
so we treat clusters as nodes, and edges as driving distance between nodes. This begins as a fully connected 
network, and through the optimization the objective function and the constraints, will select only a subset of 
nodes and edges. One of our simplifying assumptions was that we were going to treat the cost of each installation 
as a flat constant cost. The reason we include it at all is because it lays the framework for another interested 
user, who has a viable way to research and estimate: installation costs, based on location, proximity to powerlines, 
need for transformers or entirely new powerlines, maintenance, labor etc. and plug that into our optimization 
formulation. So we set an arbitrary cost vector of 100 per installation. We set the utility vector equal to the 
derived utilities from the previous stage. We initalize a boolean decision variable x to represent whether a cluster 
is selected or not, and another boolean decision variable y to represent the edge between clusters. 
Then we set the constraints as such:
- A total cost constraint so the cost of selected nodes must be less than our hypothetical budget. 
- A coupling constraint such that edge variable y is only true if the nodes at both ends of the edge are selected. 
- A dispersion constraint such that the average driving distance in the network is greater than a certain value. 
    To prevent bunching.
- A compression constraint such that the average driving distance in the network is less than the average 
    US model EV battery optimal range.
Our objective function then seeks to:
Minimize (total selection cost - total selection utility)
The output at this stage is a vector of binary variables, indicating whether a node was selected or not.
    
### **Visualization**
> Modules: kotoMap

![Selected](https://github.com/yusuf-jkhan1/POPE_VCST/blob/master/imgs/Select.png)

Now we have, raw telematics data, the density clustered and labeled data, as well as the optimized selection from 
clusters data. We already created a custom layout that we believe highlights the narrative and value of our 
project, and this is saved as a json config file within the data folder. However, the user can use the builder panel, 
to explore visualizing the data in different ways. The kotoMap module, has just a few methods which add the default 
data, add any user specified data, and then save the map as either an html or display the map if the user is 
using a jupyter notebook environment.


