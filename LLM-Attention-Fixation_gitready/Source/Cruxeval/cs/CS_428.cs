using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums) {
        for (int i = 0; i < nums.Count; i++) {
            if (i % 2 == 0) {
                nums.Add(nums[i] * nums[i + 1]);
            }
        }
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>())).SequenceEqual((new List<long>())));
    }

}
