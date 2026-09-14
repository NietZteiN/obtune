using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(long k, long j) {
        var arr = new List<long>();
        for(int i = 0; i < k; i++)
        {
            arr.Add(j);
        }
        return arr;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((7L), (5L)).SequenceEqual((new List<long>(new long[]{(long)5L, (long)5L, (long)5L, (long)5L, (long)5L, (long)5L, (long)5L}))));
    }

}
