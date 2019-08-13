
import numpy as np
from numpy import linalg 


def checkGreyscale(arr):
    """
    Flatten a layer (which is a marix) into array. Do this across each layer
    and check equality of two arrays. If all arrays are equal, it implies it is
    greyscale image, otherwise colored

    input: numpy array
    output: boolean value representing if an image is colored    
    """
    rows, cols, depth = arr.shape
    isGreyscale = True
    for d in range(1, depth):
        isGreyscale = isGreyscale and np.array_equal(np.matrix.flatten(arr[:,:,d-1]), np.matrix.flatten(arr[:,:,d]))
        if not isGreyscale:
            return False
    return True
        

def compressGreyscale(arr):
    """
    Function to compress greyscale images using SVD. Note that greyscale 
    images is a 2D matrix i.e. there are only rows and columns with no depth
    
    input: 2D numpy array representing original image
    output: 2D array representing compressed image    
    """
    nRows, nCols = arr.shape

    # convert integer representation of image to 
    # floating point for faster computation
    arr = arr/255
    
    # U, S, V
    U, S, V = linalg.svd(arr, full_matrices = True) 
    diagonalS = np.diag(S)

    # adjusting S based on linalg.svd() function's output
    # if nRows > nCols, we need to pad zeros as rows to matrix 'S'
    # if nRows < nCols, we need to pad zeros as cols to matrix 'S'
    if nRows > nCols:     
        diagonalS = np.pad(diagonalS, ((0, nRows - nCols), (0, 0)), 'constant')            
    elif nRows < nCols: 
        diagonalS = np.pad(diagonalS, ((0, 0), (0, nCols - nRows)), 'constant')            

    # compression
    arrCompressed = U[:,:] @ diagonalS[:,:] @ V[:,:]
    arrCompressed = (arrCompressed - np.min(arrCompressed))/(np.max(arrCompressed) - np.min(arrCompressed))
    arrCompressed = (arrCompressed * 255).astype(np.uint8)

    # final image
    finalImg = np.zeros((nRows, nCols))    
    finalImg[:,:] = arrCompressed

    return (arrCompressed, U, S, V)
    

def compressColored(arr):
    """
    Function to compress colored images using SVD. Note that colored 
    images is a 3D matrix i.e. there are rows, columns and depth
    
    input: 3D numpy array representing original image
    output: 3D array representing compressed image    
    """    
    # 'arr' is created using cv2.imread() function which uses 'BGR' channel scheme
    nRows, nCols, depth = arr.shape
    blueChannelMatrix = arr[:,:,0]
    greenChannelMatrix = arr[:,:,1]
    redChannelMatrix = arr[:,:,2]

    # convert each channel into floating point numbers for faster computation
    blueChannelMatrix = blueChannelMatrix/255
    greenChannelMatrix = greenChannelMatrix/255
    redChannelMatrix = redChannelMatrix/255

    # U, S, V
    blueU, blueS, blueV = linalg.svd(blueChannelMatrix, full_matrices = True)
    greenU, greenS, greenV = linalg.svd(greenChannelMatrix, full_matrices = True) 
    redU, redS, redV = linalg.svd(redChannelMatrix, full_matrices = True) 
    blueDiagonalS, greenDiagonalS, redDiagonalS = np.diag(blueS), np.diag(greenS), np.diag(redS)

    # adjusting S based on linalg.svd() function's output
    # if nRows > nCols, we need to pad zeros as rows to matrix 'S'
    # if nRows < nCols, we need to pad zeros as cols to matrix 'S'
    if nRows > nCols:     
        blueDiagonalS = np.pad(blueDiagonalS, ((0, nRows - nCols), (0, 0)), 'constant')
        greenDiagonalS = np.pad(greenDiagonalS, ((0, nRows - nCols), (0, 0)), 'constant')
        redDiagonalS = np.pad(redDiagonalS, ((0, nRows - nCols), (0, 0)), 'constant')        
    elif nRows < nCols: 
        blueDiagonalS = np.pad(blueDiagonalS, ((0, 0), (0, nCols - nRows)), 'constant')
        greenDiagonalS = np.pad(greenDiagonalS, ((0, 0), (0, nCols - nRows)), 'constant')
        redDiagonalS = np.pad(redDiagonalS, ((0, 0), (0, nCols - nRows)), 'constant')        
        
    # compression
    blueCompressed = blueU[:,:] @ blueDiagonalS[:,:] @ blueV[:,:]
    blueCompressed = (blueCompressed - np.min(blueCompressed))/(np.max(blueCompressed) - np.min(blueCompressed))
    blueCompressed = (blueCompressed * 255).astype(np.uint8)
    greenCompressed = greenU[:,:] @ greenDiagonalS[:,:] @ greenV[:,:]
    greenCompressed = (greenCompressed - np.min(greenCompressed))/(np.max(greenCompressed) - np.min(greenCompressed))
    greenCompressed = (greenCompressed * 255).astype(np.uint8)
    redCompressed = redU[:,:] @ redDiagonalS[:,:] @ redV[:,:]
    redCompressed = (redCompressed - np.min(redCompressed))/(np.max(redCompressed) - np.min(redCompressed))
    redCompressed = (redCompressed * 255).astype(np.uint8)

    # final matrices U, S, V
    U = np.zeros((nRows, nRows, depth))    
    U[:,:,0], U[:,:,1], U[:,:,2] = blueU, greenU, redU
    S = np.zeros((1, min(nRows, nCols), depth))    
    S[:,:,0], S[:,:,1], S[:,:,2] = blueS, greenS, redS
    V = np.zeros((nCols, nCols, depth))    
    V[:,:,0], V[:,:,1], V[:,:,2] = blueV[:,:], greenV[:,:], redV[:,:]
    
    # final compressed image written using cv2
    # Note that cv2 uses 'RGB' channel scheme when writing
    # and uses 'BGR' channel scheme when reading
    finalImg = np.zeros((nRows, nCols, depth))    
    finalImg[:,:,0], finalImg[:,:,1], finalImg[:,:,2] = blueCompressed, greenCompressed, redCompressed    

    return (finalImg, U, S, V)
    

def compressImage(arr):
    """
    Convert 'Image' class to numpy array. By default 'Image' class perceives 
    image as colored image and hence will create 3 channels i.e. 
    (rows, cols, depth). We need to manually check if image is greyscale or 
    colored. If it is greyscale (with 3 channels) it implies that every 
    channel has the same data. 
    Also, if it is a greyscale image, use the first layer only for 
    compression as other layers are duplicates of first layer
    
    input: numpy array representing original image
    output: numpy array representing compressed image
    """
    isGreyscale = checkGreyscale(arr)
    return (isGreyscale, compressGreyscale(arr[:,:,0])) if isGreyscale else (isGreyscale, compressColored(arr))
