"""
How are cell-centered data from ordered zones indexed?
They're indexed such that they use the same indexing as nodal data. See section
3-2.2 in the User's Manual:
https://tecplot.azureedge.net/products/360/current/help/topic.htm#t=Topics%2FOrdered_Data.htm&rhsearch=indexing&rhhlterm=indexing&rhsyns=%20

The index into the array can be defined as such:
CellIndex = i + (j)*(imax) + k*(imax-1)*(jmax-1) (where IJK are 0-based)

See the function below:
"""

def cell_index(zone,i,j,k):
    imax,jmax,kmax = zone.dimensions
    cell_index = i + j*imax + k*(imax-1)*(jmax-1)
    return cell_index
