# Name: Harsh Shah
# Student ID: 1002057387

import numpy as np
import matplotlib.pyplot as plt
import heapq

# Set random seed for consistent results
np.random.seed(42)

class CongestionControlConnection:
    def __init__(self, conn_id, initial_window, round_trip_time):
        self.conn_id = conn_id
        self.window_size = initial_window
        self.rtt_delay = round_trip_time
        self.sequence_no = 0
        self.ack_count = 0
        self.packet_loss_count = 0
        self.active_packets = 0
        self.dup_ack_counter = 0
        self.last_acked_seq = -1
        self.sent_packet_timings = {}

    def grow_window(self):
        self.window_size += 1

    def shrink_window(self):
        self.window_size = max(self.window_size // 2, 1)

    def send_packets(self, current_time, event_heap):
        # Send as many packets as allowed by the current window size
        while self.active_packets < self.window_size:
            self.sequence_no += 1
            ack_event_time = current_time + self.rtt_delay
            self.sent_packet_timings[self.sequence_no] = current_time
            heapq.heappush(event_heap, (ack_event_time, 'ack', self.conn_id, self.sequence_no))
            self.active_packets += 1

    def process_ack(self, sequence_no):
        if sequence_no == self.last_acked_seq:
            self.dup_ack_counter += 1
            if self.dup_ack_counter == 3:
                self.handle_packet_loss()
        elif sequence_no > self.last_acked_seq:
            self.dup_ack_counter = 0
            self.last_acked_seq = sequence_no
            self.grow_window()
            self.ack_count += 1
            self.active_packets -= 1

    def handle_packet_loss(self):
        self.packet_loss_count += 1
        self.shrink_window()
        self.active_packets = 0
        self.sequence_no = self.last_acked_seq

class AIMDSimulation:
    def __init__(self, max_buffer_size, service_rate, rtt_a, rtt_b, simulation_duration):
        self.buffer_limit = max_buffer_size
        self.packet_service_rate = service_rate
        self.sim_time = 0
        self.max_sim_time = simulation_duration
        self.packet_queue = []
        self.connection_a = CongestionControlConnection(conn_id=1, initial_window=1, round_trip_time=rtt_a)
        self.connection_b = CongestionControlConnection(conn_id=2, initial_window=1, round_trip_time=rtt_b)
        self.performance_metrics = {1: {'throughput': [], 'goodput': []}, 
                                    2: {'throughput': [], 'goodput': []}}
        self.event_heap = []

    def start_simulation(self):
        # Kickstart both connections
        self.connection_a.send_packets(self.sim_time, self.event_heap)
        self.connection_b.send_packets(self.sim_time + 10, self.event_heap)

        while self.sim_time < self.max_sim_time and self.event_heap:
            event_time, event_type, conn_id, sequence_no = heapq.heappop(self.event_heap)
            self.sim_time = event_time

            if event_type == 'ack':
                self.handle_ack(conn_id, sequence_no)

            # Introduce random packet losses
            if np.random.rand() < 0.15:
                if conn_id == 1:
                    self.connection_a.handle_packet_loss()
                else:
                    self.connection_b.handle_packet_loss()

            # Allow more packet transmissions
            if conn_id == 1:
                self.connection_a.send_packets(self.sim_time, self.event_heap)
            else:
                self.connection_b.send_packets(self.sim_time, self.event_heap)

            self.collect_metrics()

    def handle_ack(self, conn_id, sequence_no):
        if len(self.packet_queue) < self.buffer_limit:
            if conn_id == 1:
                self.connection_a.process_ack(sequence_no)
            else:
                self.connection_b.process_ack(sequence_no)
            self.packet_queue.append((conn_id, sequence_no))
            self.process_departure()
        else:
            # Queue overflow results in packet drop
            if conn_id == 1:
                self.connection_a.handle_packet_loss()
            else:
                self.connection_b.handle_packet_loss()

    def process_departure(self):
        if self.packet_queue:
            departing_packet = self.packet_queue.pop(0)
            conn_id, sequence_no = departing_packet
            service_time = np.random.exponential(1.0 / self.packet_service_rate)
            self.sim_time += service_time

            if conn_id == 1:
                self.connection_a.process_ack(sequence_no)
            else:
                self.connection_b.process_ack(sequence_no)

    def collect_metrics(self):
        for conn_id, conn in [(1, self.connection_a), (2, self.connection_b)]:
            throughput = conn.ack_count / self.sim_time if self.sim_time > 0 else 0
            goodput = (conn.ack_count - conn.packet_loss_count) / self.sim_time if self.sim_time > 0 else 0
            self.performance_metrics[conn_id]['throughput'].append(throughput)
            self.performance_metrics[conn_id]['goodput'].append(goodput)

    def visualize_results(self, label):
        plt.figure()
        plt.plot(self.performance_metrics[1]['throughput'], label='Conn A Throughput')
        plt.plot(self.performance_metrics[2]['throughput'], label='Conn B Throughput')
        plt.xlabel('Simulation Time')
        plt.ylabel('Throughput (packets/unit time)')
        plt.title(f'Throughput Over Time ({label})')
        plt.legend()
        plt.grid()
        plt.show()

        plt.figure()
        plt.plot(self.performance_metrics[1]['goodput'], label='Conn A Goodput')
        plt.plot(self.performance_metrics[2]['goodput'], label='Conn B Goodput')
        plt.xlabel('Simulation Time')
        plt.ylabel('Goodput (packets/unit time)')
        plt.title(f'Goodput Over Time ({label})')
        plt.legend()
        plt.grid()
        plt.show()

# Simulation settings
buffer_size = 15
service_rate = 3.0
rtt_a = 50
rtt_b = 50
sim_duration = 1000

# Equal RTT Scenario
sim_equal_rtt = AIMDSimulation(buffer_size, service_rate, rtt_a, rtt_b, sim_duration)
sim_equal_rtt.start_simulation()
sim_equal_rtt.visualize_results("Equal RTTs")

# Different RTT Scenario
rtt_b = 100
sim_diff_rtt = AIMDSimulation(buffer_size, service_rate, rtt_a, rtt_b, sim_duration)
sim_diff_rtt.start_simulation()
sim_diff_rtt.visualize_results("Different RTTs")
