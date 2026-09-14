using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        var nums = text.Where(char.IsNumber).ToList();
        Debug.Assert(nums.Count > 0);
        return string.Join("", nums);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("-123   	+314")).Equals(("123314")));
    }

}
