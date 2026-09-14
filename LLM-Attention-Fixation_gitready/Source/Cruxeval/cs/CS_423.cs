using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> selfie) {
        int lo = selfie.Count;
        for (int i = lo - 1; i >= 0; i--)
        {
            if (selfie[i] == selfie[0])
            {
                selfie.RemoveAt(lo - 1);
            }
        }
        return selfie;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)4L, (long)2L, (long)5L, (long)1L, (long)3L, (long)2L, (long)6L}))).SequenceEqual((new List<long>(new long[]{(long)4L, (long)2L, (long)5L, (long)1L, (long)3L, (long)2L}))));
    }

}
