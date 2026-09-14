using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(List<long> nums) {
        nums.Reverse();
        return string.Join("", nums.Select(num => num.ToString()));
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)-1L, (long)9L, (long)3L, (long)1L, (long)-2L}))).Equals(("-2139-1")));
    }

}
