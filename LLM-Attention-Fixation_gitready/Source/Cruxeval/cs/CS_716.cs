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
        while (nums.Count > (count/2)){
            nums.Clear();
        }
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)2L, (long)1L, (long)2L, (long)3L, (long)1L, (long)6L, (long)3L, (long)8L}))).SequenceEqual((new List<long>())));
    }

}
