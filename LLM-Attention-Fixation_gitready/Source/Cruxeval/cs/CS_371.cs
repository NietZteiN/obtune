using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> nums) {
        nums.RemoveAll(num => num % 2 != 0);
        long sum = 0;
        foreach (var num in nums) {
            sum += num;
        }
        return sum;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)11L, (long)21L, (long)0L, (long)11L}))) == (0L));
    }

}
