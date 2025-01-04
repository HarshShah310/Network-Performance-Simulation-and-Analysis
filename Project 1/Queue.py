# Name: Harsh Shah
# Student ID: 1002057387

import numpy as np
import matplotlib.pyplot as plt

def generate_interarrival_time(lambd):
    return -np.log(1 - np.random.uniform()) / lambd

def generate_service_time(mu):
    return -np.log(1 - np.random.uniform()) / mu

def simulate_mm1_queue(lambd, mu, num_arrivals):
    # Initialization
    current_time = 0
    arrival_time = generate_interarrival_time(lambd)
    departure_time = float('inf')
    n = 0  # number of customers in the system
    total_customers = 0
    total_wait_time = 0
    num_in_system = []
    times = []

    while total_customers < num_arrivals:
        # Determine next event (arrival or departure)
        if arrival_time < departure_time:
            current_time = arrival_time
            n += 1
            total_customers += 1
            num_in_system.append(n)
            times.append(current_time)
            
            # Schedule next arrival
            arrival_time = current_time + generate_interarrival_time(lambd)
            
            # If server is idle, schedule a departure
            if n == 1:
                departure_time = current_time + generate_service_time(mu)
        
        else:
            current_time = departure_time
            n -= 1
            num_in_system.append(n)
            times.append(current_time)
            
            # Schedule next departure if customers are in the queue
            if n > 0:
                departure_time = current_time + generate_service_time(mu)
            else:
                departure_time = float('inf')

    # Compute E[N] using Little's law or direct computation
    total_time = times[-1] - times[0]
    E_N_direct = sum(n_i * (times[i+1] - times[i]) for i, n_i in enumerate(num_in_system[:-1])) / total_time
    E_N_little = lambd * (total_wait_time / total_customers)
    
    return E_N_direct, E_N_little

def plot_results(rho_vals, E_N_simulation, E_N_theoretical):
    plt.plot(rho_vals, E_N_simulation, 'o-', label='Simulated E[N]')
    plt.plot(rho_vals, E_N_theoretical, 'r--', label='Theoretical E[N] = rho / (1 - rho)')
    plt.xlabel('Load (rho)')
    plt.ylabel('Average Number of Customers E[N]')
    plt.legend()
    plt.show()

# Parameters
mu = 3  # service rate
rho_vals = np.linspace(0.1, 0.9, 9)
num_arrivals = 100000
E_N_simulation = []
E_N_theoretical = []

# Run simulations for different loads
for rho in rho_vals:
    lambd = rho * mu
    E_N_direct, _ = simulate_mm1_queue(lambd, mu, num_arrivals)
    E_N_simulation.append(E_N_direct)
    E_N_theoretical.append(rho / (1 - rho))

# Plot the results
plot_results(rho_vals, E_N_simulation, E_N_theoretical)