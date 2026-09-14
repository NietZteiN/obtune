using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> nums, long index) {
        long result = nums[(int)index] % 42 + nums[(int)index] * 2;
        nums.RemoveAt((int)index);
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)3L, (long)2L, (long)0L, (long)3L, (long)7L})), (3L)) == (9L));
    }

}
