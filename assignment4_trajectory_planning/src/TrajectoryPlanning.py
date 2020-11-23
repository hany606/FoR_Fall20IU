import matplotlib.pyplot as plt
import numpy as np
from math import sqrt, floor

class TrajectoryPlaning:

    # Take the trajectory as a parameter
    # Plot 3 
    @staticmethod
    def plot_trajectory(traj, dt=1/100, title="Trajectory"):
        traj = traj.squeeze()
        q, dq, ddq = traj[:,:, 0], traj[:,:, 1], traj[:,:, 2]
        time = np.linspace(0, dt*len(traj), len(traj))

        fig, axs = plt.subplots(3,1)
        axs[0].plot(time, q)
        axs[0].set_xlabel("Time - seconds")
        axs[0].set_ylabel("q - rad")
        axs[0].legend(["Joint1", "Joint2", "Joint3"], loc="upper left", bbox_to_anchor=(1, 1))
        axs[0].set_title("Position")

        axs[1].plot(time, dq)
        axs[1].set_xlabel("Time - seconds")
        axs[1].set_ylabel("dq - rad/sec")
        axs[1].legend(["Joint1", "Joint2", "Joint3"], loc="upper left", bbox_to_anchor=(1, 1))
        axs[1].set_title("Velocity")
        

        axs[2].plot(time, ddq)
        axs[2].set_xlabel("Time - seconds")
        axs[2].set_ylabel("dq - rad/sec^2")
        axs[2].legend(["Joint1", "Joint2", "Joint3"], loc="upper left", bbox_to_anchor=(1, 1))
        axs[2].set_title("Acceleration")

        
        fig.suptitle(title, fontsize=16)
        plt.tight_layout()
        plt.show()

    # Take the constraints for the initial and goal configurations.
    # Returns a trajectory for each timestep, the entry has a 3 tuples for each joint
    #   each tuple has 3 elements (q_j^i, dq_j^i, ddq_j^i) st. 0<=j<=2 (joint index), i is the index of the iteration  
    @staticmethod
    def polynomial5(t0, q0, dq0, ddq0, tf, qf, dqf, ddqf, dt=1/100):
        q = lambda a,t: a[0] + a[1]*t + a[2]*(t**2) + a[3]*(t**3) + a[4]*(t**4) + a[5]*(t**5)
        dq = lambda a,t: a[1] + 2*a[2]*t + 3*a[3]*(t**2) + 4*a[4]*(t**3) + 5*a[5]*(t**4)
        ddq = lambda a,t: 2*a[2] + 6*a[3]*t + 12*a[4]*(t**2) + 20*a[5]*(t**3)

        A = np.array([[1, t0, t0**2, t0**3,    t0**4,       t0**5],
                      [0, 1,  2*t0,  3*(t0**2), 4*(t0**3),  5*(t0**4)],
                      [0, 0,  2,     6*t0,      12*(t0**2), 20*(t0**3)],
                      [1, tf, tf**2, tf**3,    tf**4,       tf**5],
                      [0, 1,  2*tf,  3*(tf**2), 4*(tf**3),  5*(tf**4)],
                      [0, 0,  2,     6*tf,      12*(tf**2), 20*(tf**3)]])
        x = []
        for j in range(3):
            b = np.array([[q0[j], dq0[j], ddq0[j], qf[j], dqf[j], ddqf[j]]]).T
            x.append(np.linalg.inv(A) @ b)
        
        traj_all = []
        time = np.linspace(t0, tf, int((tf-t0)/dt))
        for t in time:
            traj = []
            for j in range(3):
                traj.append([q(x[j],t), dq(x[j],t), ddq(x[j],t)])
            traj_all.append(traj)
        
        return np.array(traj_all)

    # Performs PTP command in robotics manipulators (Point to Point) (Joint space trajectory planning)
    # Returns a trajectory for each timestep, the entry has a 3 tuples for each joint
    #   each tuple has 3 elements (q_j^i, dq_j^i, ddq_j^i) st. 0<=j<=2 (joint index), i is the index of the iteration  
    @staticmethod
    def PTP(q0, qf, f=10, dq_max=1, ddq_max=10):
        dt = 1/f
        joints_status = []
        synchronization_flag = False    # Has two meaning (one of the profiles for the joints is trapezoidal) and (the case is trapezoidal after synchronization)
        t1 = None
        tau = None
        case = None
        # Check the case and calculate t1 and tau for each joint
        for j in range(3):
            joints_status.append([])
            delta_q = q0[j] - qf[j]
            dq_dash = sqrt(delta_q*ddq_max)
            tau = None
            tq = None
            c = None
            if(dq_dash <= dq_max):
                t1 = sqrt(delta_q/ddq_max)
                tau = 0
                c = "Triangular"                
            else:
                t1 = dq_max/ddq_max
                tau = delta_q/dq_max
                c = "Trapezoidal"
                synchronization_flag = True
            joints_status[-1].append([c,t1,tau])

        joints_status = np.array(joints_status)
        # Synhronize and select t1, tau and case for all the joints synchronized
        if(synchronization_flag):
            # It will Trapezoidal profile for all
            case = "Trapezoidal"
        else:
            # All of them are triangular and it will be triangular for all
            case = "Triangular"
        t1_dash = np.max(joints_status[:,1])
        print(f"Debug t1 maximization {t1_dash}")
        tau_dash = np.max(joints_status[:,2] - joints_status[:,1])
        print(f"Debug tau maximization {tau_dash}")
        # Replan after synchronization
        joints_status_dash = []
        for j in range(3):
            joints_status_dash.append([])
            delta_q = q0[j] - qf[j]
            dq_max_2dash = None
            ddq_max_2dash = None
            if(synchronization_flag == False):
                dq_max_2dash = delta_q / t1_dash
                ddq_max_2dash = delta_q / (tau_dash*t1_dash)       
            else:
                dq_max_2dash = delta_q / tau_dash
                ddq_max_2dash = delta_q / (tau_dash*t1_dash)  
            joints_status_dash[-1].append([case, t1_dash, tau_dash, dq_max_2dash, ddq_max_2dash])
        # joints_status = np.array(joints_status_dash)
        # Discretecize
        # Get n, m
        n = t1_dash//dt +1
        m = (tau_dash - t1_dash)//dt +1 
        # Caluclate t1, tau
        t1_2dash = n*dt
        tau_2dash = m*dt + t1_2dash
        # Calculate dq_max_3dash, ddq_max_3dash
        joints_status_2dash = []
        for j in range(3):
            joints_status_2dash.append([])
            delta_q = q0[j] - qf[j]
            dq_max_3dash = None
            ddq_max_3dash = None
            if(synchronization_flag == False):
                dq_max_3dash = delta_q / t1_2dash
                ddq_max_3dash = delta_q / (tau_2dash*t1_2dash)       
            else:
                dq_max_3dash = delta_q / tau_2dash
                ddq_max_3dash = delta_q / (tau_2dash*t1_2dash)  
            joints_status_2dash[-1].append([case, t1_2dash, tau_2dash, dq_max_3dash, ddq_max_3dash])
        
        # Apply the trajectory equations
        total_time = None
        # if trapezoidal
        if(synchronization_flag):
            total_time = (t1_2dash*2+tau_2dash)
        # if triangular
        else:
            total_time = t1_2dash*2
        time = np.linspace(0, total_time, total_time/dt) #TODO:?
        for t in time:
            for j in range(3):
                # Apply formulas
                # Trapezoidal profile
                if(joints_status_2dash[j][0] == "Trapezoidal"):
                    # Accelerate
                    if(0 <= t and t < t1_2dash):
                        # Implicit-Euler Integration
                        acc = +joints_status_2dash[j][4]
                        vel = vel_prev + acc*dt # vel += vel_init + acc*t
                        pos = pos_prev + vel*dt + acc*(dt**2) # pos += pos_init + vel_init*t + 0.5*acc*t*t
                    # Zero Acceleration
                    elif(t1_2dash <= t and t < tau_2dash):
                        acc = 0
                        vel = joints_status_2dash[j][3]
                        pos = pos_prev + vel*dt + acc*(dt**2) 
                    # Deceleration
                    else:
                        acc = -joints_status_2dash[j][4]
                        vel = vel_prev + acc*dt # vel += vel_init + acc*t
                        pos = pos_prev + vel*dt + acc*(dt**2) # pos += pos_init + vel_init*t + 0.5*acc*t*t
                # Triangular profile
                else:
                    # Accelerate
                    if(0 <= t and t < t1_2dash):
                        pass
                    # Deceleration
                    else:
                        pass


    # Performs LIN command on in robotics manipulators (Move in linear trajectory from point to point) (Cartesian space trajectory planning)
    # Returns a trajectory for each timestep, the entry has a 3 tuples for each joint
    #   each tuple has 3 elements (q_j^i, dq_j^i, ddq_j^i) st. 0<=j<=2 (joint index), i is the index of the iteration  
    @staticmethod
    def LIN(q0, qf, f=10, dq_max=1, ddq_max=10):
        # Create equation of line using the two points
        # Split the path to sub points, calculate the joints using IK
        # Plan point to point using the sub points
        # Check the singularity problems?
        pass

if __name__ == "__main__":
    (q0, qf) = ([-0.5, -0.6, 0], [1.57, 0.5, -2.0])
    t0,tf = 0, 2
    (dq0, dqf) = ([0,0,0], [0,0,0])
    (ddq0, ddqf) = ([0,0,0], [0,0,0])
    traj_poly5 = TrajectoryPlaning.polynomial5(t0, q0, dq0, ddq0, tf, qf, dqf, ddqf)
    TrajectoryPlaning.plot_trajectory(traj=traj_poly5, title="Polynomial - 5th Order")