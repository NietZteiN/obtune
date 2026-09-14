using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> nums, long n) {
        return nums[(int)n];
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)-7L, (long)3L, (long)1L, (long)-1L, (long)-1L, (long)0L, (long)4L})), (6L)) == (4L));
    }

}
