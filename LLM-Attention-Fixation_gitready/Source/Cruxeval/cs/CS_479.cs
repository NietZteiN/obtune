using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums, long pop1, long pop2) {
        nums.RemoveAt((int)(pop1 - 1));
        nums.RemoveAt((int)(pop2 - 1));
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)5L, (long)2L, (long)3L, (long)6L})), (2L), (4L)).SequenceEqual((new List<long>(new long[]{(long)1L, (long)2L, (long)3L}))));
    }

}
