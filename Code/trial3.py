import os
import math
from timeit import default_timer as timer
import numpy as np
import pandas as pd
infinity = math.inf
start = timer()
f = open("signature.csv", 'w')
def text_cleaning(file_name):
    f= open(file_name, 'r')
    f = f.read()
    f = f.lower()
    f = f.replace('.', ' ')
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    no_punct_f = ""
    for char in f:
       if char not in punctuations:
           no_punct_f += char
           
    data = no_punct_f.split()
    
    stoping_word= ['ourselves', 'hers', 'between', 'yourself', 'but', 'again', 
                   'there', 'about', 'once', 'during', 'out', 'very', 'having',
                   'with', 'they', 'own', 'an', 'be', 'some', 'for', 'do', 
                   'its', 'yours', 'such', 'into', 'of', 'most', 'itself',
                   'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 
                   'him', 'each', 'the', 'themselves', 'until', 'below', 'are',
                   'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me',
                   'were', 'her', 'more', 'himself', 'this', 'down', 'should', 'our', 
                   'their', 'while', 'above', 'both', 'up', 'to', 'ours', 'had',
                   'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same',
                   'and', 'been', 'have', 'in', 'will', 'on', 'does', 'yourselves', 'then',
                   'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 'not',
                   'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where', 'too', 
                   'only', 'myself', 'which', 'those', 'i', 'after', 'few', 'whom', 't', 
                   'being', 'if', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 
                   'how', 'further', 'was', 'here', 'than'] 
    
    filtered_data = [w for w in data if not w in stoping_word] 
    
    for i in range(len(filtered_data)):
        filtered_data[i] += ' '
    filtered_data_string = ''
    for x in filtered_data:
        filtered_data_string += x
    return filtered_data_string

def FileHandling():
    file_name = []
    Data = {}
    basepath = os.getcwd()
    basepath = basepath + "\\20news-bydate\\20news-bydate-train"
    for entry in os.listdir(basepath):
        if os.path.isdir(os.path.join(basepath, entry)):
#            print(os.path.join(basepath, entry))
            i = 0
            for f in os.listdir(os.path.join(basepath, entry)):
#                print(i)
                file_name.append(f)
                Data[f] = text_cleaning(os.path.join(basepath, entry)+"\\"+f)
                i += 1
                if i >= 300:
                    break
#                
    return Data, file_name

def shingling(data_string, k, Type = 'char'):
    k_shingle = []
    if Type != 'char':
        data_string = data_string.split()
        for i in range(len(data_string) - k+1):
            str1 = ''
            for j in range(i,i+k):
                if j != (i+k)-1:
                    str1 += data_string[j] + ' '
                else:
                    str1 += data_string[j] 
#            k_shingle.append(hash(str1))
            k_shingle.append(str1)
    else:
        for i in range(len(data_string) - k+1):
#            k_shingle.append(hash(data_string[i:i+k])) 
            k_shingle.append(data_string[i:i+k]) 
    return set(k_shingle)

def Binary_Matrix(universal_set, k_shingle):
    matrix = []
    Keys = k_shingle.keys()
    for x in universal_set:
        row = []
        for  K in Keys:
            if x in k_shingle[K]:
                row.append(1)
            else:
                row.append(0)
        matrix.append(row)
    return matrix
     
def HashFunction(a,b,x,P,N):
    return ((a*x + b)%P)%N
def Signature_matrix(Matrix, Num_hash):
    N = len(Matrix)
    num = N + 1
    while True:
        if all(num%i!=0 for i in range(2,num//2)):
#            print(num)
            P = num
            break
        num += 1
#    a = [1, 2]
#    b = [0, 1]
        
    a  = np.random.randint(1, Num_hash,size = Num_hash)
    b  = np.random.randint(1, Num_hash,size = Num_hash)
    signature_matrix = np.ones((Num_hash, len(Matrix[0])), dtype= int) * infinity
    for i in range(len(Matrix)):
        for k in range(Num_hash):
            hash_value = HashFunction(a[k], b[k], i+1, P, N)
            for j in range(len(Matrix[0])):
                if Matrix[i][j] == 1:
                    if signature_matrix[k][j] > hash_value:
                        signature_matrix[k][j] = hash_value
#        sign_mat = np.matrix(signature_matrix)
##        for line in  sign_mat:
##            np.savetxt(f, line, fmt='%.2f')
##        f.write('\n')
##        print('newline')
#    f.close()
    return signature_matrix

def LSH(signature_matrix, b, r, Keys):
    index = np.arange(len(signature_matrix))
    np.random.shuffle(index)
#    print(index)
    band = {}
    for i in range(b):
#        print(signature_matrix.iloc[index[i*r: i*r+r]])
        band[i] = signature_matrix.iloc[index[i*r: i*r+r]]
#        print()
        
    buckets = {}
    for i in range(b):
        temp_keys = Keys.copy()
        buckets[i] = {}
        j = 0
        while j < len(temp_keys):
#        for j in range(len(temp_keys)):    
#            print(len(temp_keys))
            depulicate = []
            Values = buckets[i].values()
            flag = True
            for value in Values:
                if temp_keys[j] in value:
#                    print(key1)
                    flag = False
                    break
            if flag == True:
#                print(i,j)
                buckets[i][temp_keys[j]] = [temp_keys[j]]
                for k in range(j+1, len(temp_keys)):
#                    print(k)
#                    print(band[i][:,k])
#                    print()
                    if all(band[i][temp_keys[j]] == band[i][temp_keys[k]]) == True:
#                                print(key2)
                        buckets[i][temp_keys[j]].append(temp_keys[k])
                        depulicate.append(k)
                
                if len(depulicate) > 0:
#                    print(depulicate) 
                    temp_keys = [i for j, i in enumerate(temp_keys) if j not in depulicate]
                    
            j = j+1  
#                    print(temp_keys.pop(k), end = ' ')
                        
#    print(buckets)
    return(band,buckets)

''' Main Code '''
#FileHandling() 
Data, file_name = FileHandling()  
Keys = list(Data.keys())
k_shingle = {} 
universal_k_shingle = set()
for key in Keys:
    k_shingle[key] = shingling(Data[key], 5)
    universal_k_shingle = universal_k_shingle.union(k_shingle[key])

    
Matrix  = Binary_Matrix(universal_k_shingle, k_shingle)
##Matrix = [[1,0],[0,1],[1,1],[1,0],[0,1]]
Num_hash = 100
SignatureMatrix = Signature_matrix(Matrix, Num_hash)
SignMatrix  = pd.DataFrame(SignatureMatrix, columns = Keys)

b = 10
r = 6
t  = 0.55
lb = 0.3
band, bucket = LSH(SignMatrix, b, r, Keys)

### Result validation
actual = []
for i in range(len(Keys)):
    cluster = [Keys[i]]
    for j in range(i+1, len(Keys)):
        d1 = Keys[i]
        d2 = Keys[j]
        dist = len(k_shingle[d1].intersection(k_shingle[d2]))/len(k_shingle[d1].union(k_shingle[d2]))
        if dist > t:
            cluster.append(d2) 
            print('(',d1,d2,')=', dist)
    if len(cluster) > 1:
        actual.append(cluster)
        
#print(len(set(SignatureMatrix[:][0]).intersection(set(SignatureMatrix[1])))/len(set(SignatureMatrix[:][0]).union(set(SignatureMatrix[1]))))
end = timer()
clusters = []
for key1 in bucket:
    for key2 in bucket[key1]:
#        print(key1,key2)
        if len(bucket[key1][key2]) > 1:
            if bucket[key1][key2] not in clusters:
                clusters.append(bucket[key1][key2])

for x in clusters:
    similarity = len(k_shingle[x[0]].intersection(k_shingle[x[1]]))/len(k_shingle[x[0]].union(k_shingle[x[1]]))
    print(x,similarity)


