"""Genetic algorithm for neural network evolution."""
import random
import numpy as np
from typing import List, Tuple

class GeneticEngine:
    """Manages genetic algorithm for network evolution."""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.population_size = 4
        self.mutation_rate = 0.1
    
    def initialize_population(self, size: int) -> List:
        """Initialize a random population."""
        population = []
        for _ in range(size):
            individual = {
                "weights": np.random.randn(10, 10).tolist(),
                "bias": np.random.randn(10).tolist(),
                "fitness": 0.0
            }
            population.append(individual)
        return population
    
    def evaluate_fitness(self, individual: dict, score: float):
        """Evaluate fitness of an individual."""
        individual["fitness"] = float(score)
        return individual
    
    def select_parents(self, population: List, scores: List) -> Tuple:
        """Select two parents based on fitness-proportionate selection."""
        # Ensure scores are all positive
        min_score = min(scores) if scores else 0
        adjusted_scores = [s - min_score + 0.1 for s in scores]
        
        # Probabilistic selection
        idx1 = random.choices(range(len(population)), weights=adjusted_scores, k=1)[0]
        idx2 = random.choices(range(len(population)), weights=adjusted_scores, k=1)[0]
        
        return population[idx1], population[idx2]
    
    def crossover(self, parent1: dict, parent2: dict) -> dict:
        """Create offspring from two parents."""
        w1 = np.array(parent1["weights"])
        w2 = np.array(parent2["weights"])
        
        # Average crossover
        child_weights = ((w1 + w2) / 2).tolist()
        child_bias = (np.array(parent1["bias"]) + np.array(parent2["bias"])) / 2
        
        return {
            "weights": child_weights,
            "bias": child_bias.tolist(),
            "fitness": 0.0
        }
    
    def mutate(self, individual: dict) -> dict:
        """Mutate an individual."""
        if random.random() < self.mutation_rate:
            w = np.array(individual["weights"])
            w += np.random.randn(*w.shape) * 0.01
            individual["weights"] = w.tolist()
        
        if random.random() < self.mutation_rate:
            b = np.array(individual["bias"])
            b += np.random.randn(*b.shape) * 0.01
            individual["bias"] = b.tolist()
        
        return individual
    
    def evolve(self, population: List, scores: List) -> List:
        """Evolve population to next generation."""
        try:
            # Sort by fitness
            sorted_pop = sorted(zip(population, scores), key=lambda x: x[1], reverse=True)
            elite = [ind for ind, _ in sorted_pop[:len(population)//4]]
            
            # Create new generation
            new_population = elite.copy()
            
            while len(new_population) < len(population):
                parent1, parent2 = self.select_parents(population, scores)
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)
            
            return new_population[:len(population)]
        except Exception as e:
            # Return current population if evolution fails
            return population
