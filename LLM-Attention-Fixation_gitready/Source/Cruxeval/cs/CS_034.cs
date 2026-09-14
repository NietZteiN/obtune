using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums, long odd1, long odd2) {
        while(nums.Contains(odd1)){
            nums.Remove(odd1);
        }
        while(nums.Contains(odd2)){
            nums.Remove(odd2);
        }
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)3L, (long)7L, (long)7L, (long)6L, (long)8L, (long)4L, (long)1L, (long)2L, (long)3L, (long)5L, (long)1L, (long)3L, (long)21L, (long)1L, (long)3L})), (3L), (1L)).SequenceEqual((new List<long>(new long[]{(long)2L, (long)7L, (long)7L, (long)6L, (long)8L, (long)4L, (long)2L, (long)5L, (long)21L}))));
    }

}
