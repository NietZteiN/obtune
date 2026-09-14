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
        for (int i = count - 1; i >= 0; i--)
        {
            long first = nums[0];
            nums.RemoveAt(0);
            nums.Insert(i, first);
        }
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)0L, (long)-5L, (long)-4L}))).SequenceEqual((new List<long>(new long[]{(long)-4L, (long)-5L, (long)0L}))));
    }

}
