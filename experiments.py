#!/usr/bin/env python3

import subprocess
import prefixed

def directory_size(directory):
    raw = (subprocess.run(["du", "-s", directory],
                          capture_output=True,
                          encoding='utf8').stdout.split('\t')[0])
    print("raw value is", raw)
    return (prefixed.Float(raw))

a = (subprocess.run(["du", "-s", "."],
                   capture_output=True,
                   encoding='utf8')
     .stdout)

print(a)

b = a.split()

print(b)

c = b[0]

print(c)

d = prefixed.Float(c)

print(d)

print(directory_size("."))

if __name__ == '__main__':
    main()
