using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums, long spot, long idx) {
        nums.Insert((int)spot, idx);
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)0L, (long)1L, (long)1L})), (0L), (9L)).SequenceEqual((new List<long>(new long[]{(long)9L, (long)1L, (long)0L, (long)1L, (long)1L}))));
    }

}
