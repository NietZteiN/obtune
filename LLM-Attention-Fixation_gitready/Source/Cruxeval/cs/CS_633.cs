using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> array, long elem) {
        array.Reverse();
        try
        {
            int found = array.IndexOf(elem);
            return found;
        }
        finally
        {
            array.Reverse();
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)5L, (long)-3L, (long)3L, (long)2L})), (2L)) == (0L));
    }

}
