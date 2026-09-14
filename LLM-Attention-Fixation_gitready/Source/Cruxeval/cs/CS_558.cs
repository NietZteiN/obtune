using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(List<long> nums, List<long> mos) {
        foreach (var num in mos)
        {
            nums.RemoveAt(nums.IndexOf(num));
        }
        nums.Sort();
        foreach (var num in mos)
        {
            nums.Add(num);
        }
        
        for (int i = 0; i < nums.Count - 1; i++)
        {
            if (nums[i] > nums[i + 1])
            {
                return false;
            }
        }
        
        return true;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)3L, (long)1L, (long)2L, (long)1L, (long)4L, (long)1L})), (new List<long>(new long[]{(long)1L}))) == (false));
    }

}
