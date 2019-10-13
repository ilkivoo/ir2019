fin = open("test.txt", 'r')
fout = open("test_0.txt", 'w')
lines = fin.readlines()

for line in lines:
    a, *el = line.split()
    print(0, *el, file=fout)

fin.close()
fout.close()
