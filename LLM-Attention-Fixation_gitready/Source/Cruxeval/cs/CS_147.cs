using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums) {
        int middle = nums.Count / 2;
        return nums.Skip(middle).Concat(nums.Take(middle)).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)1L, (long)1L}))).SequenceEqual((new List<long>(new long[]{(long)1L, (long)1L, (long)1L}))));
    }

}
