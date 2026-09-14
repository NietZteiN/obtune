using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> a) {
        List<long> b = new List<long>(a);
        for (int k = 0; k < a.Count - 1; k += 2)
        {
            b.Insert(k + 1, b[k]);
        }
        b.Add(b[0]);
        return b;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)5L, (long)5L, (long)5L, (long)6L, (long)4L, (long)9L}))).SequenceEqual((new List<long>(new long[]{(long)5L, (long)5L, (long)5L, (long)5L, (long)5L, (long)5L, (long)6L, (long)4L, (long)9L, (long)5L}))));
    }

}
