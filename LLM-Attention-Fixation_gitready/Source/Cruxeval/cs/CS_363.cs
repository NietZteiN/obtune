using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums) {
        nums.Sort();
        int n = nums.Count;
        List<long> new_nums = new List<long>(){nums[n/2]};
        if (n % 2 == 0)
        {
            new_nums = new List<long>(){nums[n/2 - 1], nums[n/2]};
        }
        for (int i = 0; i < n/2; i++)
        {
            new_nums.Insert(0, nums[n-i-1]);
            new_nums.Add(nums[i]);
        }
        return new_nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L}))).SequenceEqual((new List<long>(new long[]{(long)1L}))));
    }

}
