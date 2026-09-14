using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums) {
        int count = nums.Count;
        for (int i = 0; i < count; i++)
            nums.Insert(i, nums[i]*2);
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)2L, (long)8L, (long)-2L, (long)9L, (long)3L, (long)3L}))).SequenceEqual((new List<long>(new long[]{(long)4L, (long)4L, (long)4L, (long)4L, (long)4L, (long)4L, (long)2L, (long)8L, (long)-2L, (long)9L, (long)3L, (long)3L}))));
    }

}
