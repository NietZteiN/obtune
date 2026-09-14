using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums) {
        nums = nums.Where(y => y > 0).ToList();
        if (nums.Count <= 3)
        {
            return nums;
        }
        nums.Reverse();
        int half = nums.Count / 2;
        List<long> result = new List<long>();
        result.AddRange(nums.Take(half));
        result.AddRange(Enumerable.Repeat(0L, 5));
        result.AddRange(nums.Skip(half));
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)10L, (long)3L, (long)2L, (long)2L, (long)6L, (long)0L}))).SequenceEqual((new List<long>(new long[]{(long)6L, (long)2L, (long)0L, (long)0L, (long)0L, (long)0L, (long)0L, (long)2L, (long)3L, (long)10L}))));
    }

}
