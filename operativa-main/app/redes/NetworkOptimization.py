import pulp
import networkx as nx


class NetworkOptimization:
    @staticmethod
    def minimum_spanning_tree(edges):
        """ Resuelve el Árbol de Expansión Mínima (MST) """
        G = nx.Graph()
        G.add_weighted_edges_from(edges)
        mst = nx.minimum_spanning_tree(G)
        return list(mst.edges(data=True))

    @staticmethod
    def max_flow(graph, source, sink):
        """ Resuelve el problema de flujo máximo """
        G = nx.DiGraph()
        G.add_weighted_edges_from(graph)
        flow_value, flow_dict = nx.maximum_flow(G, source, sink)
        return flow_value, flow_dict

    @staticmethod
    def min_cost_flow(supply, demand, edges):
        """ Resuelve el problema de Flujo de Costo Mínimo """
        prob = pulp.LpProblem("MinCostFlow", pulp.LpMinimize)

        # Definir variables
        flow_vars = {(u, v): pulp.LpVariable(f"flow_{u}_{v}", lowBound=0) for u, v, _ in edges}

        # Función objetivo (minimizar costos)
        prob += pulp.lpSum(cost * flow_vars[(u, v)] for u, v, cost in edges)

        # Restricciones de oferta y demanda
        nodes = set(node for edge in edges for node in edge[:2])
        for node in nodes:
            prob += (
                    pulp.lpSum(flow_vars[(u, v)] for u, v, _ in edges if u == node) -
                    pulp.lpSum(flow_vars[(u, v)] for u, v, _ in edges if v == node)
                    == (supply.get(node, 0) - demand.get(node, 0))
            )

        prob.solve()
        return {key: var.varValue for key, var in flow_vars.items()}, pulp.value(prob.objective)


if __name__ == "__main__":
    edges = [(0, 1, 4), (0, 2, 3), (1, 2, 1), (1, 3, 2), (2, 3, 4)]
    print("MST:", NetworkOptimization.minimum_spanning_tree(edges))

    flow_graph = [(0, 1, 10), (0, 2, 5), (1, 2, 15), (1, 3, 10), (2, 3, 10)]
    print("Flujo Máximo:", NetworkOptimization.max_flow(flow_graph, 0, 3))

    supply = {0: 20}
    demand = {3: 20}
    min_cost_edges = [(0, 1, 2), (0, 2, 3), (1, 3, 1), (2, 3, 4)]
    print("Flujo de Costo Mínimo:", NetworkOptimization.min_cost_flow(supply, demand, min_cost_edges))
