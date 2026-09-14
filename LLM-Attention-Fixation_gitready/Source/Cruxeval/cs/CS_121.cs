using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s) {
        string nums = string.Join("", s.Where(char.IsDigit));
        if (nums == "")
        {
            return "none";
        }
        int m = nums.Split(',').Select(int.Parse).Max();
        return m.ToString();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("01,001")).Equals(("1001")));
    }

}
