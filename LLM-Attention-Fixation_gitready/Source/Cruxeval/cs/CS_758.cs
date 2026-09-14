using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(List<long> nums) {
        return nums.SequenceEqual(nums.AsEnumerable().Reverse());
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)0L, (long)3L, (long)6L, (long)2L}))) == (false));
    }

}
