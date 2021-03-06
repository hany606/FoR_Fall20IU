import numpy as np

def translation_x(l):
    return np.array([[1,0,0, l],
                     [0,1,0, 0],
                     [0,0,1, 0],
                     [0,0,0, 1]])

def translation_y(l):
    return np.array([[1,0,0, 0],
                     [0,1,0, l],
                     [0,0,1, 0],
                     [0,0,0, 1]])

def translation_z(l):
    return np.array([[1,0,0, 0],
                     [0,1,0, 0],
                     [0,0,1, l],
                     [0,0,0, 1]])

def rotation_x(theta):
    return np.array([[1,         0,          0, 0],
                     [0,np.cos(theta),-np.sin(theta), 0],
                     [0,np.sin(theta), np.cos(theta), 0],
                     [0,         0,          0, 1]])


def rotation_y(theta):
    return np.array([[np.cos(theta) ,0,np.sin(theta), 0],
                     [0          ,1,         0, 0],
                     [-np.sin(theta),0,np.cos(theta), 0],
                     [0          ,0,         0, 1]])

def rotation_z(theta):
    return np.array([[np.cos(theta),-np.sin(theta),0, 0],
                     [np.sin(theta), np.cos(theta),0, 0],
                     [0         ,0          ,1, 0],
                     [0         ,0          ,0, 1]])

def get_rotation(H):
    return H[:3,:3]

def get_position(H):
    return H[:3,3]

def calc_error(H1, H2):
    shape = np.array(H1).shape
    error = 0
    for i in range(shape[0]):
        for j in range(shape[1]):
            error += abs(H1[i,j] - H2[i,j])
    return error