using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> array, long elem) {
        int ind = array.IndexOf(elem);
        return ind * 2 + array[array.Count - ind - 1] * 3;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)-1L, (long)2L, (long)1L, (long)-8L, (long)2L})), (2L)) == (-22L));
    }

}
