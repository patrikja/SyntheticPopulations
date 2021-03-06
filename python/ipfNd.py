import numpy as np

#Returns a matrix with one dimension less than the provided matrix. The submatrix is
#sliced out of the given matrix 'mat' at the index 'index'. The removed dimension is
#'dimension'.
#This is a very ugly work around since the only syntax I have found to extract submatrices
#is mat[:, :, ..., i, :, :, ...], e.g. mat[1, :, :] to get a submatrix at index 1 for the 
#0th dimension in a three dimensional matrix.
def get_submatrix(mat, dimension, index):
  #Iterativly create a string looking like 'mat[:,...,index,:,...]
  submatrix_string = 'mat['
  for d in range(0, dimension):
    submatrix_string += ':,'
  submatrix_string += str(index) + ','
  for d in range(dimension + 1, len(mat.shape)):
    submatrix_string += ':,'
  submatrix_string += ']'
  #The submatrix is returned by reference
  return eval(submatrix_string)


def ipfNd(mat, margins, epsilon):
  dims = range(0, len(seed.shape)) #A list of all dimensions (0, 1, 2 ...)
  steps = 0

  diff_sum = 1.
  while diff_sum >= epsilon:
  #for k in range(0,5):
    diff_sum = 0.
    for dim in dims:
      axes = dims[:] #Copy
      axes.remove(dim) #Remove current dimension
      sum_over_dims = mat.sum(axis=tuple(axes)) #Sum over all dimensions exept for for the current one

      diff_sum += sum(abs(sum_over_dims - margins[dim]))

      scalings = margins[dim]/sum_over_dims
      for scaling_i in range(0, len(scalings)):
        #Get a 
        submat = get_submatrix(mat, dim, scaling_i)
        submat *= scalings[scaling_i]
    steps += 1
  return (mat, steps) 



mat_shape=(2, 3, 4, 5, 6)

#Create seed of all ones
seed = np.ones(np.product(mat_shape), dtype=np.float).reshape(mat_shape)

#Create marginal distributions. All marginal distribution must sum to the same number.
margins0 = [13000, 8000]
margins1 = [7000, 7000, 7000]
margins2 = [7000, 7000, 6000, 1000]
margins3 = [2000, 5000, 4000, 3000, 7000]
margins4 = [1000, 5000, 4000, 6000, 4000, 1000]
margins = [margins0, margins1, margins2, margins3, margins4]    

#print seed
#print margins
(full_mat, iterations) = ipfNd(seed, margins, 0.0001)
print full_mat
print 'iterations: {0}'.format(iterations)
