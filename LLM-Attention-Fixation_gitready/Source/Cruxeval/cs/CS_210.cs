using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(long n, long m, long num) {
        var xList = Enumerable.Range((int)n, (int)m - (int)n + 1).ToList();
        var j = 0;
        while (true)
        {
            j = (j + (int)num) % xList.Count;
            if (xList[j] % 2 == 0)
            {
                return xList[j];
            }
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F((46L), (48L), (21L)) == (46L));
    }

}
