using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums, long idx, long added) {
        nums.Insert((int)idx, added);
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)2L, (long)2L, (long)2L, (long)3L, (long)3L})), (2L), (3L)).SequenceEqual((new List<long>(new long[]{(long)2L, (long)2L, (long)3L, (long)2L, (long)3L, (long)3L}))));
    }

}
