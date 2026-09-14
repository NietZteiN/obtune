using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> nums) {
        return nums[nums.Count / 2];
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)-1L, (long)-3L, (long)-5L, (long)-7L, (long)0L}))) == (-5L));
    }

}
