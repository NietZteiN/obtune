using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string num) {
        int letter = 1;
        foreach(var i in "1234567890")
        {
            num = num.Replace(i.ToString(), "");
            if (num.Length == 0) break;
            int startIndex = Math.Min(letter, num.Length);
            num = num.Substring(startIndex) + num.Substring(0, startIndex);
            letter += 1;
        }
        return num;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("bwmm7h")).Equals(("mhbwm")));
    }

}
