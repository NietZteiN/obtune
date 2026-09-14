using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(long num1, long num2, long num3) {
        List<long> nums = new List<long>() { num1, num2, num3 };
        nums.Sort();
        return $"{nums[0]},{nums[1]},{nums[2]}";
    }
    public static void Main(string[] args) {
    Debug.Assert(F((6L), (8L), (8L)).Equals(("6,8,8")));
    }

}
