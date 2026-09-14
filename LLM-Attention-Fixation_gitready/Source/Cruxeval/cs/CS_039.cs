using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> array, long elem) {
        if (array.Contains(elem)) {
            return array.IndexOf(elem);
        }
        return -1;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)6L, (long)2L, (long)7L, (long)1L})), (6L)) == (0L));
    }

}
