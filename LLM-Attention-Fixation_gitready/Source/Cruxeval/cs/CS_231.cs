using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> years) {
        var a10 = years.Count(x => x <= 1900);
        var a90 = years.Count(x => x > 1910);
        if (a10 > 3)
        {
            return 3;
        }
        else if (a90 > 3)
        {
            return 1;
        }
        else
        {
            return 2;
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1872L, (long)1995L, (long)1945L}))) == (2L));
    }

}
