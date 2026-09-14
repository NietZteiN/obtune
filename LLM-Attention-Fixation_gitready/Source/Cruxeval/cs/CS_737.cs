using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> nums) {
        var counts = 0;
        foreach (var i in nums)
        {
            if (long.TryParse(i.ToString(), out long result))
            {
                if (counts == 0)
                {
                    counts += 1;
                }
            }
        }
        return counts;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)0L, (long)6L, (long)2L, (long)-1L, (long)-2L}))) == (1L));
    }

}
