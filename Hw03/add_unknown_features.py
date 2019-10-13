fin = open("task3_test.txt", 'r')
fout = open("test.txt", 'w')
lines = fin.readlines()

for line in lines:
    a, b, *el = line.split()
    to_add = set(range(1, 246))
    for t in el:
        fid, _ = t.split(":")
        fid = int(fid)
        to_add.remove(fid)
    for t in to_add:
        el.append(f"{t}:0")
    print(a, b, *el, file=fout)

fin.close()
fout.close()
