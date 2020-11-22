import numpy as np
from cvxpy import Variable, Problem, Minimize, GLPK_MI
import cvxopt
import datetime as dt


class cluster_optimization:

    def __init__(self, dataframe, mat):
        vect_length = len(dataframe['Utility'].to_numpy())
        self.u = dataframe['Utility'].to_numpy().reshape(vect_length,1)
        self.n = self.u.shape[0]
        self.c = np.array([[100] * self.n]).reshape(vect_length,1)
        self.x = Variable(self.n,boolean=True)
        self.y = Variable((self.n, self.n),boolean=True)
        self.d = mat / 1000

    def avg_dist(self, n, c, u, var_node, var_edge, dist_matrix, min_budget=1500, max_budget=1600, threshold_dist=15):
        """ 
        This function returns constraints list for the optimization problem. It returns budget constraint, average distance
        constraint, and node-edge coupling constraints

        :Params: 
            var_node (n,) : potential cluster nodes -> binary decision variable defined in cvxpy
            var_edge (nxn): edges b/w the nodes -> binary decision variable defined in cvxpy
            dist_matrix (nxn): numpy array of distances b/w the nodes 
            min_budget (float): minimum EV station installation budget 
            max_budget (float): maximum EV station installation budget
            threshold_dist (float): minimum average distance in the cluster
        
        :Returns:
            rtype: list
            rvalue: list of constraints

        """
        self.min_budget = min_budget
        self.max_budget = max_budget
        self.threshold_dist = threshold_dist
        constraints = []
        tot_sum = 0
        count = 0 
        for i in range(n):
                for j in range(n):
                    if i >= j:
                        constraints.append(var_edge[i,j] == 0)
                    else:
                        tot_sum += dist_matrix[i,j]*var_edge[i,j]
                        count += var_edge[i,j]
                        constraints.append( ((var_node[i] + var_node[j])/2) - var_edge[i,j] <= 0.5 )
                        constraints.append( ((var_node[i] + var_node[j])/2) - var_edge[i,j] >= 0 )
        constraints.append(tot_sum-threshold_dist*count >= 1)
        constraints.append(tot_sum-240*count <= 0)
        constraints.append(self.c.T@self.x >= min_budget)
        constraints.append(self.c.T@self.x <= max_budget)
        return constraints

    def optimize_cluster_selection(self):
        st_time = dt.datetime.now()
        constraints = self.avg_dist(self.n,self.c,self.u,self.x,self.y,self.d)
        prob = Problem(Minimize(self.c.T@self.x-self.u.T@self.x), constraints)
        score = prob.solve(solver=GLPK_MI)
        end_time = dt.datetime.now()
        print(f"Budget: {self.min_budget}-{self.max_budget}, Run Time: {end_time-st_time}, thresh: {self.threshold_dist}, score: {score}")

        return self.x.value