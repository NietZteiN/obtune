using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> xs) {
        for (int idx = -xs.Count; idx < 0; idx++)
        {
            xs.Insert(0, xs[xs.Count - 1]);
            xs.RemoveAt(xs.Count - 1);
        }
        return xs;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)3L}))).SequenceEqual((new List<long>(new long[]{(long)1L, (long)2L, (long)3L}))));
    }

}
