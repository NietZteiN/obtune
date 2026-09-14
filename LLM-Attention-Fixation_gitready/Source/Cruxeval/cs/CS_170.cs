using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> nums, long number) {
        return nums.Count(x => x == number);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)12L, (long)0L, (long)13L, (long)4L, (long)12L})), (12L)) == (2L));
    }

}
