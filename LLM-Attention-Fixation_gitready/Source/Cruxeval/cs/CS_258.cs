using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> L, long m, long start, long step) {
        L.Insert((int)start, m);
        for (long x = start - 1; x > 0; x -= step)
        {
            start -= 1;
            L.Insert((int)start, L.ElementAt(L.IndexOf(m) - 1));
            L.RemoveAt((int)(L.IndexOf(m) - 1));
        }
        return L;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)7L, (long)9L})), (3L), (3L), (2L)).SequenceEqual((new List<long>(new long[]{(long)1L, (long)2L, (long)7L, (long)3L, (long)9L}))));
    }

}
