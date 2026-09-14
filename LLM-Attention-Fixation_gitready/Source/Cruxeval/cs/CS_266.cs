using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums) {
        for (var i = nums.Count - 1; i >= 0; i--)
        {
            if (nums[i] % 2 == 1)
            {
                nums.Insert(i + 1, nums[i]);
            }
        }
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)2L, (long)3L, (long)4L, (long)6L, (long)-2L}))).SequenceEqual((new List<long>(new long[]{(long)2L, (long)3L, (long)3L, (long)4L, (long)6L, (long)-2L}))));
    }

}
