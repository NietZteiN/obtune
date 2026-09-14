using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums, long sort_count) {
        nums.Sort();
        return nums.Take((int)sort_count).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)2L, (long)3L, (long)4L, (long)5L})), (1L)).SequenceEqual((new List<long>(new long[]{(long)1L}))));
    }

}
