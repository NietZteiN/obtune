using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> nums) {
        long a = -1;
        List<long> b = nums.Skip(1).ToList();
        while (a <= b[0])
        {
            nums.Remove(b[0]);
            a = 0;
            b = b.Skip(1).ToList();
        }
        return nums;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)-1L, (long)5L, (long)3L, (long)-2L, (long)-6L, (long)8L, (long)8L}))).SequenceEqual((new List<long>(new long[]{(long)-1L, (long)-2L, (long)-6L, (long)8L, (long)8L}))));
    }

}
