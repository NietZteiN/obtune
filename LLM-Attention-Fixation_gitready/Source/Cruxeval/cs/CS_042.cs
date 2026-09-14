using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums) {
        nums.Clear();
        for(int i=0; i<nums.Count; i++)
        {
            nums[i] = nums[i]*2;
        }
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)4L, (long)3L, (long)2L, (long)1L, (long)2L, (long)-1L, (long)4L, (long)2L}))).SequenceEqual((new List<long>())));
    }

}
