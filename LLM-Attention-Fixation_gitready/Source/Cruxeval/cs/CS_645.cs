using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> nums, long target) {
        if (nums.Count(x => x == 0) > 0)
        {
            return 0;
        }
        else if (nums.Count(x => x == target) < 3)
        {
            return 1;
        }
        else
        {
            return nums.IndexOf(target);
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)1L, (long)1L, (long)2L})), (3L)) == (1L));
    }

}
