using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(long n) {
        foreach (char digit in n.ToString())
        {
            if (!"012".Contains(digit) && !Enumerable.Range(5, 5).Contains(int.Parse(digit.ToString())))
            {
                return false;
            }
        }
        return true;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((1341240312L)) == (false));
    }

}
