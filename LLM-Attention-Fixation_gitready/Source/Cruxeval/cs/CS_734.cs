using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums) {
        for (int i = nums.Count - 2; i >= 0; i--)
        {
            if (nums[i] % 2 == 0)
            {
                nums.RemoveAt(i);
            }
        }
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)5L, (long)3L, (long)3L, (long)7L}))).SequenceEqual((new List<long>(new long[]{(long)5L, (long)3L, (long)3L, (long)7L}))));
    }

}
