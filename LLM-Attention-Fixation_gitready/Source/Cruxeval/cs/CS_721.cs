using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums) {
        int count = nums.Count();
        for (int num = 2; num < count; num++)
        {
            nums.Sort();
        }
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)-6L, (long)-5L, (long)-7L, (long)-8L, (long)2L}))).SequenceEqual((new List<long>(new long[]{(long)-8L, (long)-7L, (long)-6L, (long)-5L, (long)2L}))));
    }

}
