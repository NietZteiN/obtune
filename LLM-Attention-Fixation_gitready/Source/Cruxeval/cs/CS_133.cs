using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums, List<long> elements) {
        for (int i = 0; i < elements.Count; i++)
        {
            nums.RemoveAt(nums.Count - 1);
        }
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)7L, (long)1L, (long)2L, (long)6L, (long)0L, (long)2L})), (new List<long>(new long[]{(long)9L, (long)0L, (long)3L}))).SequenceEqual((new List<long>(new long[]{(long)7L, (long)1L, (long)2L}))));
    }

}
