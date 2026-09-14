using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;

class Problem {
    public static List<long> F(List<long> nums) {
        int originalLength = nums.Count;
        for (int i = 0; i < originalLength; i++) {
            if (nums[i] % 3 == 0) {
                nums.Add(nums[i]);
            }
        }
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)3L}))).SequenceEqual((new List<long>(new long[]{(long)1L, (long)3L, (long)3L}))));
    }

}
