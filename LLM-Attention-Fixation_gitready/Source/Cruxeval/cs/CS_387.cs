using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums, long pos, long value) {
        nums.Insert((int)pos, value);
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)3L, (long)1L, (long)2L})), (2L), (0L)).SequenceEqual((new List<long>(new long[]{(long)3L, (long)1L, (long)0L, (long)2L}))));
    }

}
