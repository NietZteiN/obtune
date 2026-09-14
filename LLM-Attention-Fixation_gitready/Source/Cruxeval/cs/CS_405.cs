using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> xs) {
        long new_x = xs[0] - 1;
        xs.RemoveAt(0);
        while(new_x <= xs[0])
        {
            xs.RemoveAt(0);
            new_x -= 1;
        }
        xs.Insert(0, new_x);
        return xs;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)6L, (long)3L, (long)4L, (long)1L, (long)2L, (long)3L, (long)5L}))).SequenceEqual((new List<long>(new long[]{(long)5L, (long)3L, (long)4L, (long)1L, (long)2L, (long)3L, (long)5L}))));
    }

}
