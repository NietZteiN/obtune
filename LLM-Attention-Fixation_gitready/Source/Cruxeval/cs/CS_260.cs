using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums, long start, long k) {
        if (start + k > nums.Count) {
            k = nums.Count - start;
        }
        var range = nums.GetRange((int)start, (int)k);
        range.Reverse();
        nums.RemoveRange((int)start, (int)k);
        nums.InsertRange((int)start, range);
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)3L, (long)4L, (long)5L, (long)6L})), (4L), (2L)).SequenceEqual((new List<long>(new long[]{(long)1L, (long)2L, (long)3L, (long)4L, (long)6L, (long)5L}))));
    }

}
