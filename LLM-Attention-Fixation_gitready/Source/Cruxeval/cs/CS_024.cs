using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums, long i) {
        nums.RemoveAt((int)i);
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)35L, (long)45L, (long)3L, (long)61L, (long)39L, (long)27L, (long)47L})), (0L)).SequenceEqual((new List<long>(new long[]{(long)45L, (long)3L, (long)61L, (long)39L, (long)27L, (long)47L}))));
    }

}
