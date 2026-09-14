using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums, long delete) {
        nums.Remove(delete);
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)4L, (long)5L, (long)3L, (long)6L, (long)1L})), (5L)).SequenceEqual((new List<long>(new long[]{(long)4L, (long)3L, (long)6L, (long)1L}))));
    }

}
