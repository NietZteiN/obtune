using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> array, long L) {
        if (L <= 0)
        {
            return array;
        }
        if (array.Count < L)
        {
            array.AddRange(F(array, L - array.Count));
        }
        return array;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)3L})), (4L)).SequenceEqual((new List<long>(new long[]{(long)1L, (long)2L, (long)3L, (long)1L, (long)2L, (long)3L}))));
    }

}
