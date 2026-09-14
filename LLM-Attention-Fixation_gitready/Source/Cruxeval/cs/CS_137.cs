using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums) {
        int count = 0;
        if (nums.Count == 0) return nums;
        while(nums.Count > 0) {
            if (count % 2 == 0) {
                nums.RemoveAt(nums.Count - 1);
            } else {
                nums.RemoveAt(0);
            }
            count++;
        }
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)3L, (long)2L, (long)0L, (long)0L, (long)2L, (long)3L}))).SequenceEqual((new List<long>())));
    }

}
