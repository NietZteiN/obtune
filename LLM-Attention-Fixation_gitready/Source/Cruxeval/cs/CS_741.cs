using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> nums, long p) {
        long prev_p = p - 1;
        if (prev_p < 0) {
            prev_p = nums.Count - 1;
        }
        return nums[(int)prev_p];
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)6L, (long)8L, (long)2L, (long)5L, (long)3L, (long)1L, (long)9L, (long)7L})), (6L)) == (1L));
    }

}
