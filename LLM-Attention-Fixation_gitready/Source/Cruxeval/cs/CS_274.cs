using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> nums, long target) {
        int count = 0;
        foreach (var n1 in nums)
        {
            foreach (var n2 in nums)
            {
                count += (n1 + n2 == target) ? 1 : 0;
            }
        }
        return count;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)3L})), (4L)) == (3L));
    }

}
