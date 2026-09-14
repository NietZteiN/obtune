using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums) {
        long m = nums.Max();
        for (long i = 0; i < m; i++)
        {
            nums.Reverse();
        }
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)43L, (long)0L, (long)4L, (long)77L, (long)5L, (long)2L, (long)0L, (long)9L, (long)77L}))).SequenceEqual((new List<long>(new long[]{(long)77L, (long)9L, (long)0L, (long)2L, (long)5L, (long)77L, (long)4L, (long)0L, (long)43L}))));
    }

}
