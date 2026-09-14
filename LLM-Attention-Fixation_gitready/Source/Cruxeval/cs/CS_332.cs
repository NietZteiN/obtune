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
        if (count == 0)
        {
            nums = new List<long>() { 0 };
        }
        else if (count % 2 == 0)
        {
            nums.Clear();
        }
        else
        {
            nums.RemoveRange(0, count / 2);
        }
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)-6L, (long)-2L, (long)1L, (long)-3L, (long)0L, (long)1L}))).SequenceEqual((new List<long>())));
    }

}
