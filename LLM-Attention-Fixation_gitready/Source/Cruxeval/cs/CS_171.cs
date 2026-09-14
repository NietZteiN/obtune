using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums) {
        int count = nums.Count / 2;
        for (int i = 0; i < count; i++)
        {
            nums.RemoveAt(0);
        }
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)3L, (long)4L, (long)1L, (long)2L, (long)3L}))).SequenceEqual((new List<long>(new long[]{(long)1L, (long)2L, (long)3L}))));
    }

}
